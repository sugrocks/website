import os
import re
import sys
import json
import html
import shutil
import crayons
import traceback
import basc_py4chan
import configparser
import urllib.error
import urllib.parse
import urllib.request
import multiprocessing
import better_exceptions

from time import sleep
from collections import deque
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

better_exceptions.MAX_LENGTH = None
THIS_DIR = os.path.dirname(os.path.abspath(__file__))

# Loading our config
config = configparser.ConfigParser()
config.read(os.path.join(THIS_DIR, 'config', 'threads.ini'))

# Init values
dco = deque('', 5)
jco = {}
dtrash = deque('', 5)
jtrash = {}

# Load boards with HTTPS
co = basc_py4chan.Board('co')
trash = basc_py4chan.Board('trash')


def debuglog(message):
    # Print nice debug messages
    sys.stdout.write('\r{} [{}] '.format(
        crayons.blue(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), crayons.green(message)))


def inline_css(text):
    # Add CSS inline
    # Spoilers
    formated = re.sub(r'<s>', '<s style="background:black;color:black;text-decoration:none">', text)
    # Quotes
    return re.sub(r'(class="quote")', 'style="color:green;"', formated)


def find_edition(text):
    # Our regex to find edition names
    reg = r'.*edition.*?\n'
    # Replace <br>s with new lines
    text = re.sub(r'<br\s*?/?>', '\n', text)
    # And here we search for it, case insensitive
    m = re.search(reg, text, re.IGNORECASE)
    # If there's something, return our result
    if m:
        # Remove any tags and unescape html entities
        return html.unescape(re.sub(r'<.*?>', '', m.group()).rstrip())
    else:
        return ''


def find_page(board, threadid):
    # Because 4chan's API terms
    sleep(0.8)
    # Be sure it's an int
    threadid = int(threadid)
    # Get catalog of the board
    url = 'https://a.4cdn.org/%s/catalog.json' % board
    req = urllib.request.urlopen(url)
    catalog = json.loads(req.read().decode('utf-8'))
    # Find our thread and return the page number
    for page in catalog:
        for thread in page['threads']:
            if thread['no'] == threadid:
                return page['page']
    return '0'


def stamp_to_strftime(timestamp):
    # Convert timestamp to a nice datetime on UTC (for templates)
    return datetime.utcfromtimestamp(timestamp).strftime('%m/%d/%y(%a)%H:%M:%S(UTC)')


def atom_date(timestamp):
    # Convert timestamp to a ATOM-compatible datetime
    return datetime.utcfromtimestamp(timestamp).isoformat('T') + 'Z'


def rss_date(timestamp):
    # Convert timestamp to a RFC822 datetime
    return datetime.utcfromtimestamp(timestamp).strftime('%a, %e %b %Y %H:%M:%S') + 'Z'


def is_sug(thread):
    # Will try to find out if the thread is a /sug/ one
    return (
        # Check subject
        (
            thread.topic.subject is not None and
            'Steven Universe General' in thread.topic.subject
        ) or (  # Or check for the two sug.rocks links
            'http://kametsu.com/topic/57130-cartoon-network-unofficial-previews/' in thread.topic.text_comment and
            'https://sug.rocks/dl.html' in thread.topic.text_comment
        )
    )


def load_cache():
    # Load latest threads from our latest api results
    global dco, dtrash
    debuglog('  Loading cache...  ')
    with open(os.path.join(THIS_DIR, 'api', 'threads.json')) as data_file:
        j = json.load(data_file)
        for thread in j['co']:
            dco.append(co.get_thread(int(thread)))
        for thread in j['trash']:
            dtrash.append(trash.get_thread(int(thread)))


def dictify(thread):
    return {
        "archive": "https://desuarchive.org/%s/thread/%d" % (thread._board.name, thread.topic.post_id),
        "board": thread._board.name,
        "dates": {
            "RFC822": rss_date(thread.topic.timestamp),
            "ISO8601": atom_date(thread.topic.timestamp),
            "string": stamp_to_strftime(thread.topic.timestamp),
            "timestamp": thread.topic.timestamp
        },
        "edition": find_edition(thread.topic.comment),
        "id": int(thread.topic.post_id),
        "media": {
            "deleted": thread.topic.file.file_deleted,
            "height": thread.topic.file.file_height,
            "name": thread.topic.file.filename_original,
            "spoiler": thread.topic.spoiler,
            "url": thread.topic.file.file_url,
            "width": thread.topic.file.file_width
        },
        "op": thread.topic.comment.replace('href="/', 'href="https://boards.4chan.org/'),
        "page": find_page(thread._board.name, thread.topic.post_id),
        "status": {
            "archived": thread.archived,
            "bump_limit": thread.bumplimit,
            "closed": (thread.closed or thread.archived or thread.is_404),
            "dead": thread.is_404,
            "image_limit": thread.imagelimit
        },
        "url": thread.url
    }


def sug_threads():
    # Main function
    global dco, dtrash

    # Init values
    uniqid = 0
    ignoreplz = config.get('config', 'ignore').split(',')
    co_threads = []
    trash_threads = []

    # Get /co/ and /trash/ current threads without too much details
    try:
        debuglog('      GET /co/      ')
        co_threads = co.get_all_threads(False)
    except:
        print(crayons.red('\nSomething went wrong here'))

    sleep(1)

    try:
        debuglog('     GET /trash/    ')
        trash_threads = trash.get_all_threads(False)
    except:
        print(crayons.red('\nSomething went wrong here'))

    debuglog('   Sorting threads  ')
    # Now we check if the thread is about /sug/
    for thread in co_threads:
        if is_sug(thread):
            # If thread is dead
            if not hasattr(thread, 'topic'):
                with open(os.path.join(THIS_DIR, 'api', 'threads.json')) as data_file:
                    j = json.load(data_file)
                    jco[int(thread.id)] = j['co'][int(thread.id)]
                    jco[int(thread.id)]['status']['closed'] = True
                    jco[int(thread.id)]['status']['dead'] = True
                    # Remove from deque
                    dco.remove(thread)
            else:
                # Test if we don't have this thread yet
                if not any(hasattr(x, 'topic') and x.topic.post_id == thread.topic.post_id for x in dco):
                    dco.append(thread)
        else:
            # Remove from cache if we don't care
            thread._board._thread_cache.pop(thread.id, None)

    for thread in trash_threads:
        if is_sug(thread):
            # If thread is dead
            if not hasattr(thread, 'topic'):
                with open(os.path.join(THIS_DIR, 'api', 'threads.json')) as data_file:
                    j = json.load(data_file)
                    jtrash[int(thread.id)] = j['trash'][int(thread.id)]
                    jtrash[int(thread.id)]['status']['closed'] = True
                    jtrash[int(thread.id)]['status']['dead'] = True
                    # Remove from deque
                    dtrash.remove(thread)
            else:
                # Test if we don't have this thread yet
                if not any(hasattr(x, 'topic') and x.topic.post_id == thread.topic.post_id for x in dtrash):
                    dtrash.append(thread)
        else:
            # Remove from cache if we don't care
            thread._board._thread_cache.pop(thread.id, None)

    debuglog('Updating all threads')
    for thread in dco:
        # If it doesn't exist anymore, ignore it
        if thread is None:
            continue

        try:
            thread.update(True)
            if str(thread.id) in ignoreplz:
                # Remove because ignored
                thread._board._thread_cache.pop(thread.id, None)
                dco.remove(thread)
            else:
                jco[int(thread.id)] = dictify(thread)
        except:
            print(crayons.red('\n' + str(thread.id) + ' didn\'t update'))
            traceback.print_exc()

        # For a unique id to indicate changes
        uniqid += thread.id

        try:
            if thread.is_404:
                uniqid += 1
            if thread.archived:
                uniqid += 2
            if thread.bumplimit:
                uniqid += 4
            if thread.imagelimit:
                uniqid += 8
        except:
            pass

    for thread in dtrash:
        # If it doesn't exist anymore, ignore it
        if thread is None:
            continue

        try:
            thread.update(True)
            if str(thread.id) in ignoreplz:
                # Remove because ignored
                thread._board._thread_cache.pop(thread.id, None)
                dtrash.remove(thread)
            else:
                jtrash[int(thread.id)] = dictify(thread)
        except:
            print(crayons.red('\n' + str(thread.id) + ' didn\'t update'))
            traceback.print_exc()

        # For a unique id to indicate changes
        uniqid += thread.id

        try:
            if thread.is_404:
                uniqid += 1
            if thread.archived:
                uniqid += 2
            if thread.bumplimit:
                uniqid += 4
            if thread.imagelimit:
                uniqid += 8
        except:
            pass

    # Merge /trash/ and /co/ threads
    threaddict = jtrash.copy()
    threaddict.update(jco)
    threadlist = list(jco) + list(jtrash)
    # Order by date
    threadlist.sort(key=lambda x: threaddict[x]['dates']['timestamp'])
    # Put dead threads at the end
    threadlist.sort(key=lambda x: threaddict[x]['status']['closed'], reverse=True)
    # And we now reverse the list
    threadlist = list(reversed(threadlist))

    debuglog('Loading templates...')
    # Current time
    datenow = datetime.utcnow().strftime('%B %d %Y at %H:%M:%S')
    atomnow = datetime.utcnow().isoformat('T') + 'Z'

    # Load the environment for the templates
    j2_html = Environment(loader=FileSystemLoader(os.path.join(THIS_DIR, 'templates', 'html')), trim_blocks=True)
    j2_xml = Environment(loader=FileSystemLoader(os.path.join(THIS_DIR, 'templates', 'xml')), trim_blocks=True)
    j2_xml.filters['inlinecss'] = inline_css

    debuglog(' Generating HTML... ')
    try:
        # Generate page (to a tmp folder first, in case of errors)
        j2_html.get_template('threads.html').stream(
            pagetype='page-threads', pagename='Home', pagedesc='Last threads and quick links', dategen=datenow,
            threadlist=threadlist, threaddict=threaddict, uniqid=uniqid)\
            .dump(os.path.join(THIS_DIR, 'tmp', 'index.html'))
        # Copy from tmp to the public folder
        shutil.copy2(os.path.join(THIS_DIR, 'tmp', 'index.html'), os.path.join(THIS_DIR, 'public'))
    except:
        print(crayons.red('\nError when generating HTML'))

    debuglog(' Generating Feeds...')
    try:
        # Generate feeds (to a tmp folder first, in case of errors)
        j2_xml.get_template('threads-atom.xml').stream(threadlist=threadlist, threaddict=threaddict, lastupdate=atomnow)\
            .dump(os.path.join(THIS_DIR, 'tmp', 'threads.xml'))
        j2_xml.get_template('threads-rss.xml').stream(threadlist=threadlist, threaddict=threaddict)\
            .dump(os.path.join(THIS_DIR, 'tmp', 'threads.rss'))
        # Copy from tmp to the public folder
        shutil.copy2(os.path.join(THIS_DIR, 'tmp', 'threads.xml'), os.path.join(THIS_DIR, 'public'))
        shutil.copy2(os.path.join(THIS_DIR, 'tmp', 'threads.rss'), os.path.join(THIS_DIR, 'public'))
    except:
        print(crayons.red('\nError when generating Atom/RSS feeds'))

    debuglog(' Generating GOTO... ')
    # Generate GOTO pages for every board
    try:
        tmplist = list(jco)
        if len(tmplist) > 0:
            # If there is a thread for this board
            # Sort by time
            tmplist.sort(key=lambda x: jco[x]['dates']['timestamp'], reverse=True)
            first = tmplist[0]
            if not jco[first]['status']['closed'] or not jco[first]['status']['dead']:
                # If the first thread is not closed, generate the redirection
                j2_html.get_template('go.html').stream(board='co', url=jco[first]['url'])\
                    .dump(os.path.join(THIS_DIR, 'go', 'co', 'index.html'))
            else:
                # Else, generate an "error" page
                j2_html.get_template('nogo.html').stream(board='co')\
                    .dump(os.path.join(THIS_DIR, 'go', 'co', 'index.html'))
        else:
            # Else, generate an "error" page
            j2_html.get_template('nogo.html').stream(board='co')\
                .dump(os.path.join(THIS_DIR, 'go', 'co', 'index.html'))
    except:
        print(crayons.red('\nError when generating GOTO for /co/'))

    try:
        tmplist = list(jtrash)
        if len(tmplist) > 0:
            # If there is a thread for this board
            # Sort by time
            tmplist.sort(key=lambda x: jtrash[x]['dates']['timestamp'], reverse=True)
            first = tmplist[0]
            if not jtrash[first]['status']['closed'] or not jtrash[first]['status']['dead']:
                # If the first thread is not closed, generate the redirection
                j2_html.get_template('go.html').stream(board='trash', url=jtrash[first]['url'])\
                    .dump(os.path.join(THIS_DIR, 'go', 'trash', 'index.html'))
            else:
                # Else, generate an "error" page
                j2_html.get_template('nogo.html').stream(board='trash')\
                    .dump(os.path.join(THIS_DIR, 'go', 'trash', 'index.html'))
        else:
            # Else, generate an "error" page
            j2_html.get_template('nogo.html').stream(board='trash')\
                .dump(os.path.join(THIS_DIR, 'go', 'trash', 'index.html'))
    except:
        print(crayons.red('\nError when generating GOTO for /trash/'))

    debuglog('  Generating API... ')
    # Generate API endpoint
    try:
        api = {
            '_': {
                'generated': int(datetime.utcnow().timestamp())
            },
            'co': jco,
            'trash': jtrash
        }

        # Save to json
        with open(os.path.join(THIS_DIR, 'api', 'threads.json'), 'w') as f:
            f.write(json.dumps(api, indent=2, sort_keys=True))
    except:
        print(crayons.red('\nError when generating API endpoint'))

    # Save uniqid to a file for javascript refresh
    with open(os.path.join(THIS_DIR, 'public', 'threadsid.txt'), 'w') as f:
        f.write(str(uniqid))

    debuglog('        Done.       ')


if __name__ == '__main__':
    # Load our cache for this run
    load_cache()

    while True:
        # Start our search as a subprocess
        p = multiprocessing.Process(target=sug_threads)
        p.start()

        # Run for 120 seconds or until it ends
        p.join(120)

        # If thread is still alive
        if p.is_alive():
            print(crayons.red('\nSearch didn\'t end in time, kill the process...'))
            # Terminate
            p.terminate()
            p.join()

        # Reload config and wait for next run
        config.read(os.path.join(THIS_DIR, 'config', 'threads.ini'))
        sec = config.get('config', 'refresh')
        debuglog('Waiting ' + sec + ' seconds.')
        sleep(int(sec))
