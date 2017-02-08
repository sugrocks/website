import os
import re
import sys
import json
import html
import shutil
import crayons
import py8chan
import basc_py4chan
import configparser
import urllib.error
import urllib.parse
import urllib.request
import multiprocessing
from time import sleep
from collections import deque
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

# Loading our config
filecache = configparser.ConfigParser()
filecache.read(os.path.join(THIS_DIR, 'config', 'threads-cache.ini'))

# Init values
dco = deque('', 5)
dtrash = deque('', 5)
dsugen = deque('', 50)

# Load boards with HTTPS
co = basc_py4chan.Board('co', True)
trash = basc_py4chan.Board('trash', True)
sugen = py8chan.Board('sugen', True)


def debuglog(message):
    # Print nice debug messages
    sys.stdout.write('\r{} [{}] '.format(
        crayons.blue(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), crayons.green(message)))


def urlify(text):
    # Make cliquable URLs
    urlfinder = re.compile(r'(?<!")((https?://|www)[-\w./#?%=&\!]+)')
    return urlfinder.sub(r'<a href="\1">\1</a>', text)


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
    # Also fuck 8ch
    text = re.sub(r'<\/p>', '\n', text)
    # And here we search for it, case insensitive
    m = re.search(reg, text, re.IGNORECASE)
    # If there's something, return our result
    if m:
        # Remove any <p> that 8ch left and unescape html entities
        return html.unescape(re.sub(r'<p.*>', '', m.group()).rstrip())
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
    return (thread.topic.subject is not None and
        '/sug/' in thread.topic.subject or
        'https://sug.rocks/leaks.html' in thread.topic.text_comment)


def load_cache():
    # Load latest threads from our file-based cache
    global dco, dtrash, dsugen
    debuglog('  Loading cache...  ')
    for threadid in dict(filecache.items('threads')):
        if filecache['threads'][threadid] == 'co':
            dco.append(co.get_thread(int(threadid)))
        elif filecache['threads'][threadid] == 'trash':
            dtrash.append(trash.get_thread(int(threadid)))
#        elif filecache['threads'][threadid] == 'sugen':
#            dsugen.append(sugen.get_thread(int(threadid)))


def sug_threads():
    # Main function
    global dco, dtrash, dsugen

    # Init temporary value to test if something changed
    uniqid = 0

    # Get /co/, /trash/ and /sugen/ current threads without too much details
    try:
        debuglog('      GET /co/      ')
        cothr = co.get_all_threads(False)
    except:
        print(crayons.red('\nSomething went wrong here'))
    try:
        debuglog('     GET /trash/    ')
        trashthr = trash.get_all_threads(False)
    except:
        print(crayons.red('\nSomething went wrong here'))
    try:
        debuglog('     GET /sugen/    ')
        sugenthr = sugen.get_all_threads(False)
    except:
        print(crayons.red('\nSomething went wrong here'))

    debuglog('   Sorting threads  ')
    # First, remove threads that doesn't work anymore from the cache
    toremove = []
    for i in dco:
        if not hasattr(i, 'topic'):
            toremove.append(i)
    for i in toremove:
        dco.remove(i)

    toremove = []
    for i in dtrash:
        if not hasattr(i, 'topic'):
            toremove.append(i)
    for i in toremove:
        dtrash.remove(i)

    toremove = []
    for i in dsugen:
        if not hasattr(i, 'topic'):
            toremove.append(i)
    for i in toremove:
        dsugen.remove(i)

    # Now we check if the thread is about /sug/
    for thread in cothr:
        if (is_sug(thread)):
            # Test if we don't have this thread yet
            if not any(x.topic.post_id == thread.topic.post_id for x in dco):
                dco.append(thread)
        else:
            # Remove from cache if we don't care
            thread._board._thread_cache.pop(thread.id, None)

    for thread in trashthr:
        if (is_sug(thread)):
            # Test if we don't have this thread yet
            if not any(x.topic.post_id == thread.topic.post_id for x in dtrash):
                dtrash.append(thread)
        else:
            # Remove from cache if we don't care
            thread._board._thread_cache.pop(thread.id, None)

    for thread in sugenthr:
        if (is_sug(thread)):
            # Test if we don't have this thread yet
            if not any(x.topic.post_id == thread.topic.post_id for x in dsugen):
                dsugen.append(thread)
                dsugen = sorted(dsugen, key=lambda x: x.topic.timestamp, reverse=True)
        else:
            # Remove from cache if we don't care
            thread._board._thread_cache.pop(thread.id, None)

    debuglog('Updating all threads')
    # Merge /trash/, /co/ and (only the latest) /sugen/ threads
    threadlist = list(dtrash) + list(dco) + [list(dsugen)[0]]
    # Order by date
    threadlist.sort(key=lambda x: x.topic.timestamp)
    # Put dead threads at the end
    threadlist.sort(key=lambda x: x.closed, reverse=True)
    # And we now reverse the list
    threadlist = list(reversed(threadlist))

    # Try to update our threads meta and remove them if 404'd
    filecache['threads'] = {}
    for thread in threadlist:
        try:
            thread.update(True)
            if thread.is_404:
                # If it did 404, delete it from our cache and the list
                thread._board._thread_cache.pop(thread.id, None)
                threadlist.remove(thread)
            else:
                # Or add it on our text-cache
                filecache['threads'][str(thread.id)] = thread._board.name
        except:
            print(crayons.red('\n' + str(thread.topic.post_id) + ' didn\'t update'))

        # For a unique id to indicate changes
        uniqid += thread.topic.post_id

        try:
            if thread.closed:
                uniqid += 1
            if thread.archived:
                uniqid += 2
            if thread.bumplimit:
                uniqid += 4
            if thread.imagelimit:
                uniqid += 8
        except:
            pass

    debuglog('Loading templates...')
    # Current time
    datenow = datetime.utcnow().strftime('%B %d %Y at %H:%M:%S')
    atomnow = datetime.utcnow().isoformat('T') + 'Z'

    # Load the environment for the templates
    j2_html = Environment(loader=FileSystemLoader(os.path.join(THIS_DIR, 'templates', 'html')), trim_blocks=True)
    j2_html.globals['find_page'] = find_page
    j2_html.filters['stamptostrftime'] = stamp_to_strftime
    j2_html.filters['edition'] = find_edition

    j2_xml = Environment(loader=FileSystemLoader(os.path.join(THIS_DIR, 'templates', 'xml')), trim_blocks=True)
    j2_xml.filters['atomdate'] = atom_date
    j2_xml.filters['rssdate'] = rss_date
    j2_xml.filters['urlify'] = urlify
    j2_xml.filters['inlinecss'] = inline_css
    j2_xml.filters['edition'] = find_edition

    debuglog(' Generating HTML... ')
    try:
        # Generate page (to a tmp folder first, in case of errors)
        j2_html.get_template('threads.html').stream(
            pagetype='page-threads', pagename='Home', pagedesc='Last threads and quick links', dategen=datenow,
            threadlist=threadlist, uniqid=uniqid)\
            .dump(os.path.join(THIS_DIR, 'tmp', 'index.html'))
        # Copy from tmp to the public folder
        shutil.copy2(os.path.join(THIS_DIR, 'tmp', 'index.html'), os.path.join(THIS_DIR, 'public'))
    except:
        print(crayons.red('\nError when generating HTML'))

    debuglog(' Generating Feeds...')
    try:
        # Generate feeds (to a tmp folder first, in case of errors)
        j2_xml.get_template('threads-atom.xml').stream(threadlist=threadlist, lastupdate=atomnow)\
            .dump(os.path.join(THIS_DIR, 'tmp', 'threads.xml'))
        j2_xml.get_template('threads-rss.xml').stream(threadlist=threadlist)\
            .dump(os.path.join(THIS_DIR, 'tmp', 'threads.rss'))
        # Copy from tmp to the public folder
        shutil.copy2(os.path.join(THIS_DIR, 'tmp', 'threads.xml'), os.path.join(THIS_DIR, 'public'))
        shutil.copy2(os.path.join(THIS_DIR, 'tmp', 'threads.rss'), os.path.join(THIS_DIR, 'public'))
    except:
        print(crayons.red('\nError when generating Atom/RSS feeds'))

    debuglog(' Generating GOTO... ')
    # Generate GOTO pages for every board
    try:
        tmplist = list(dco)
        if len(tmplist) > 0:
            # If there is a thread for this board
            # Sort by time
            tmplist.sort(key=lambda x: x.topic.timestamp, reverse=True)
            if not tmplist[0].archived:
                # If the first thread is not archived, generate the redirection
                j2_html.get_template('go.html').stream(url=tmplist[0].url)\
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
        tmplist = list(dtrash)
        if len(tmplist) > 0:
            # If there is a thread for this board
            # Sort by time
            tmplist.sort(key=lambda x: x.topic.timestamp, reverse=True)
            # Generate the redirection
            j2_html.get_template('go.html').stream(url=tmplist[0].url)\
                .dump(os.path.join(THIS_DIR, 'go', 'trash', 'index.html'))
        else:
            # Else, generate an "error" page
            j2_html.get_template('nogo.html').stream(board='trash')\
                .dump(os.path.join(THIS_DIR, 'go', 'trash', 'index.html'))
    except:
        print(crayons.red('\nError when generating GOTO for /trash/'))

    try:
        tmplist = list(dsugen)
        if len(tmplist) > 0:
            # If there is a thread for this board
            # Sort by time
            tmplist.sort(key=lambda x: x.topic.timestamp, reverse=True)
            # Generate the redirection
            j2_html.get_template('go.html').stream(url=tmplist[0].url)\
                .dump(os.path.join(THIS_DIR, 'go', 'sugen', 'index.html'))
        else:
            # Else, generate an "error" page
            j2_html.get_template('nogo.html').stream(board='sugen')\
                .dump(os.path.join(THIS_DIR, 'go', 'sugen', 'index.html'))
    except:
        print(crayons.red('\nError when generating GOTO for /sugen/'))

    debuglog('  Generating API... ')
    # Generate API endpoint
    try:
        api = []
        # Go through every threads we found
        for thread in threadlist:
            # Specific things because of /sugen/
            if thread._board.name == 'sugen':
                media = thread.topic.first_file.thumbnail_url
                archive = None
                page = 0
                bumplimit = False
                imagelimit = False
                archived = False
                op = thread.topic.comment.replace('href="/', 'href="https://8ch.net/')
            else:
                media = thread.topic.file.thumbnail_url
                archive = 'https://desuarchive.org/' + thread._board.name + '/thread/' + str(thread.topic.post_number)
                page = find_page(thread._board.name, thread.topic.post_number)
                bumplimit = thread.bumplimit
                imagelimit = thread.imagelimit
                archived = thread.archived
                op = thread.topic.comment.replace('href="/', 'href="https://boards.4chan.org/')

            # Add to the API array output
            api.append({
                'id': int(thread.topic.post_number),
                'board': thread._board.name,
                'timestamp': int(thread.topic.timestamp),
                'edition': find_edition(op),
                'page': int(page),
                'status': {
                    'bump_limit': bumplimit,
                    'image_limit': imagelimit,
                    'archived': archived
                },
                'url': thread.url,
                'archive': archive,
                'media': media,
                'op': op
            })

        # Save to json
        with open(os.path.join(THIS_DIR, 'api', 'threads.json'), 'w') as f:
            f.write(json.dumps(api, indent=2, sort_keys=True))
    except:
        print(crayons.red('\nError when generating API endpoint'))

    # Save uniqid to a file for javascript refresh
    with open(os.path.join(THIS_DIR, 'public', 'threadsid.txt'), 'w') as f:
        f.write(str(uniqid))

    # Cache our threads
    with open(os.path.join(THIS_DIR, 'config', 'threads-cache.ini'), 'w') as f:
        filecache.write(f)

    debuglog('        Done.       ')


if __name__ == '__main__':
    # Load our cache for this run
    load_cache()

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
        exit(1)

    exit(0)
