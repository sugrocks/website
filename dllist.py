import os
import json
import configparser
import better_exceptions

from datetime import datetime
from operator import itemgetter
from jinja2 import Environment, FileSystemLoader

better_exceptions.MAX_LENGTH = None
THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def atom_date(timestamp):
    # Convert timestamp to a ATOM-compatible datetime
    timestamp = int(timestamp)
    return datetime.utcfromtimestamp(timestamp).isoformat('T') + 'Z'


def rss_date(timestamp):
    # Convert timestamp to a RFC822 datetime
    timestamp = int(timestamp)
    return datetime.utcfromtimestamp(timestamp).strftime('%a, %e %b %Y %H:%M:%S') + 'Z'


def get_id(episode, dltype=''):
    # Return what we'll use as id for linking
    return episode.replace('_', '').replace('x', '') + dltype


def get_cat(folder):
    # Return the category name from the folder name
    if folder == 'comic':
        return 'Main Comics (2014-15)'
    elif folder == '2017comic':
        return 'Main Comics (2017)'
    elif folder == 'book':
        return 'Books'
    elif folder == 'special':
        return 'Specials'
    elif folder == 'sucg':
        return 'Steven and the Crystal Gems'
    elif folder == 'harmony':
        return 'Harmony'
    else:
        return 'Others'


def format_epnumber(episode):
    # Return proper formated season and episode details
    if episode[:2] == '99':
        return 'Movie'

    return episode.replace('_', ' & ').replace('00x', 'Special ')


def split_season_episode(episode):
    split = episode.split('x')
    return [split[0].replace('06', 'Future').replace('99', 'Movie').replace('00', 'Special'), split[1]]


def gen_dl_page():
    # Main function
    # Loading our config
    config = configparser.ConfigParser()
    config.read(os.path.join(THIS_DIR, 'config', 'dl.ini'))

    # Initialize some variables
    preair = []
    sufuture = []
    itunes = []
    individual = []
    comics = []
    musics = []

    # Load every "preair" episodes
    for episode in dict(config.items('preair')):
        # Parse episode data
        data = config['preair'][episode].split(',')
        se = split_season_episode(episode)
        # Add it to the list
        preair.append({
            'id': get_id(episode, 'tmp'),
            'code': format_epnumber(episode),
            'season': se[0],
            'episode': se[1],
            'title': data[0],
            'filename': data[1],
            'torrent': data[2],
            'ctoon': data[3],
            'daily': data[4],
            'date': data[5]
        })

    # Load every "future" episodes
    for episode in dict(config.items('sufuture')):
        # Parse episode data
        data = config.get('sufuture', episode).split(',')
        # Add it to the list
        sufuture.append({
            'id': get_id(episode, 'f'),
            'code': episode,
            'season': 'Future',
            'episode': episode,
            'title': data[0],
            'filename': data[1],
            'ctoon': data[2],
            'date': data[3]
        })

    # Load every "itunes" episodes
    for episode in dict(config.items('itunes')):
        # Parse episode data
        data = config.get('itunes', episode).split(',')
        se = split_season_episode(episode)
        # Add it to the list
        itunes.append({
            'id': get_id(episode, 'i'),
            'code': format_epnumber(episode),
            'season': se[0],
            'episode': se[1],
            'title': data[0],
            'filename': data[1],
            'torrent': data[2],
            'ctoon': data[3],
            'date': data[4]
        })

    # Load every "individual" episodes
    for episode in dict(config.items('individual')):
        # Parse episode data
        data = config.get('individual', episode).split(',')
        se = split_season_episode(episode)
        # Add it to the list
        individual.append({
            'id': get_id(episode, 'm'),
            'code': format_epnumber(episode),
            'season': se[0],
            'episode': se[1],
            'title': data[0],
            'filename': data[1],
            'ctoon': data[2],
            'date': data[3]
        })

    # Load comics and books
    for comic in dict(config.items('comics')):
        # Parse episode data
        data = config.get('comics', comic).split(',')
        # Add it to the list
        comics.append({
            'id': comic.upper(),
            'title': data[0],
            'folder': data[1],
            'category': get_cat(data[1]),
            'cbz': data[2],
            'cbr': data[3],
            'pdf': data[4],
            'epub': data[5],
            'date': data[6]
        })

    # Load music
    for music in dict(config.items('music')):
        # Parse episode data
        data = config.get('music', music).split(',')
        # Add it to the list
        musics.append({
            'id': music.upper(),
            'title': data[0],
            'mp3': data[1],
            'flac': data[2],
            'date': data[3]
        })

    # Sort episodes
    preair = sorted(preair, key=itemgetter('code'))
    sufuture = sorted(sufuture, key=itemgetter('code'))
    itunes = sorted(itunes, key=itemgetter('code'))
    individual = sorted(individual, key=itemgetter('code'))
    comics = sorted(comics, key=itemgetter('category'))
    musics = sorted(musics, key=itemgetter('id'))

    # Get current date
    dategen = datetime.utcnow().strftime('%B %d %Y at %H:%M:%S')
    atomnow = datetime.utcnow().isoformat('T') + 'Z'

    # Load the environment for the templates
    j2_html = Environment(loader=FileSystemLoader(os.path.join(THIS_DIR, 'templates', 'html')), trim_blocks=True)

    j2_xml = Environment(loader=FileSystemLoader(os.path.join(THIS_DIR, 'templates', 'xml')), trim_blocks=True)
    j2_xml.filters['atomdate'] = atom_date
    j2_xml.filters['rssdate'] = rss_date

    # Generate html
    j2_html.get_template('dl.html').stream(
        pagetype='page-dl', pagename='Downloads', pagedesc='Direct links or torrents to episodes', dategen=dategen,
        # Add episodes/comics/musics lists
        preair=preair, sufuture=sufuture, itunes=itunes, individual=individual, comics=comics, musics=musics,
        # If there's nothing, we'll not display the "preair" list
        lenpa=len(preair))\
        .dump(os.path.join(THIS_DIR, 'public', 'dl.html'))

    # Concatenate every list and sort by date for the feeds
    allep = preair + sufuture + itunes + individual
    allep = sorted(allep, key=itemgetter('date'), reverse=True)[:15]

    # Generate feeds
    j2_xml.get_template('dl-atom.xml').stream(episodes=allep, lastupdate=atomnow)\
        .dump(os.path.join(THIS_DIR, 'public', 'dl.xml'))
    j2_xml.get_template('dl-rss.xml').stream(episodes=allep)\
        .dump(os.path.join(THIS_DIR, 'public', 'dl.rss'))


def gen_dl_api():
    # Generate API endpoint
    # Loading our config
    config = configparser.ConfigParser()
    config.read(os.path.join(THIS_DIR, 'config', 'dl.ini'))

    # Initialize some variables
    preair = []
    sufuture = []
    itunes = []
    individual = []
    comics = []

    # Load every "preair" episodes
    for episode in dict(config.items('preair')):
        # Parse episode data
        data = config['preair'][episode].split(',')
        se_ep = split_season_episode(episode)
        if data[2] == '1':
            torrent = 'https://cadl.sug.rocks/preair/' + data[1] + '.torrent'
        else:
            torrent = None
        # Add it to the list
        preair.append({
            'id': int(get_id(episode)),
            'season': se_ep[0],
            'episode': se_ep[1],
            'title': data[0],
            'url': 'https://cadl.sug.rocks/preair/' + data[1],
            'ctoon': 'https://ctoon.party/show/sun/watch/' + data[3],
            'dailymotion': 'www.dailymotion.com/video/' + data[4],
            'torrent': torrent,
            'date': int(data[5])
        })

    # Load every "sufuture" episodes
    for episode in dict(config.items('sufuture')):
        # Parse episode data
        data = config['sufuture'][episode].split(',')
        torrent = None
        # Add it to the list
        sufuture.append({
            'id': int(get_id(episode)),
            'season': 'Future',
            'episode': episode,
            'title': data[0],
            'url': 'https://cadl.sug.rocks/' + data[1],
            'ctoon': 'https://ctoon.party/show/sun/watch/' + data[2],
            'dailymotion': None,
            'torrent': None,
            'date': int(data[3])
        })

    # Load every "itunes" episodes
    for episode in dict(config.items('itunes')):
        # Parse episode data
        data = config.get('itunes', episode).split(',')
        se_ep = split_season_episode(episode)
        if data[2] == '1':
            torrent = 'https://cadl.sug.rocks/torrents/' + data[1] + '.torrent'
        else:
            torrent = None
        # Add it to the list
        itunes.append({
            'id': int(get_id(episode)),
            'season': se_ep[0],
            'episode': se_ep[1],
            'title': data[0],
            'url': 'https://cadl.sug.rocks/' + data[1],
            'ctoon': 'https://ctoon.party/show/sun/watch/' + data[3],
            'dailymotion': None,
            'torrent': torrent,
            'date': int(data[4])
        })

    # Load every "individual" episodes
    for episode in dict(config.items('individual')):
        # Parse episode data
        data = config.get('individual', episode).split(',')
        se_ep = split_season_episode(episode)
        # Add it to the list
        individual.append({
            'id': int(get_id(episode)),
            'season': se_ep[0],
            'episode': se_ep[1],
            'title': data[0],
            'url': 'https://cadl.sug.rocks/mega/' + data[1],
            'ctoon': 'https://ctoon.party/show/sun/watch/' + data[2],
            'dailymotion': None,
            'torrent': None,
            'date': int(data[3])
        })

    # Load comics and books
    for comic in dict(config.items('comics')):
        # Parse episode data
        data = config.get('comics', comic).split(',')
        # Add it to the list
        if data[2] == '1':
            cbz = 'https://cadl.sug.rocks/comics/' + data[1] + '/SUG-CBZ-' + comic.upper() + '.cbz'
        else:
            cbz = None

        if data[3] == '1':
            cbr = 'https://cadl.sug.rocks/comics/' + data[1] + '/SUG-CBR-' + comic.upper() + '.cbr'
        else:
            cbr = None

        if data[4] == '1':
            pdf = 'https://cadl.sug.rocks/comics/' + data[1] + '/SUG-PDF-' + comic.upper() + '.pdf'
        else:
            pdf = None

        if data[5] == '1':
            epub = 'https://cadl.sug.rocks/comics/' + data[1] + '/SUG-EPUB-' + comic.upper() + '.epub'
        else:
            epub = None

        comics.append({
            'id': comic.upper(),
            'title': data[0],
            'category': get_cat(data[1]),
            'cbz': cbz,
            'cbr': cbr,
            'pdf': pdf,
            'epub': epub,
            'date': int(data[6])
        })

    # Sort episodes
    preair = sorted(preair, key=itemgetter('id'))
    sufuture = sorted(sufuture, key=itemgetter('id'))
    itunes = sorted(itunes, key=itemgetter('id'))
    individual = sorted(individual, key=itemgetter('id'))
    comics = sorted(comics, key=itemgetter('category'))

    # Make our json object
    api = {}
    api['_'] = {"generated": int(datetime.utcnow().timestamp())}
    api['preair'] = preair
    api['sufuture'] = sufuture
    api['itunes'] = itunes
    api['individual'] = individual
    api['comics'] = comics

    # Save it
    with open(os.path.join(THIS_DIR, 'api', 'dl.json'), 'w') as f:
        f.write(json.dumps(api, indent=2, sort_keys=True))


if __name__ == '__main__':
    # Just start our function
    gen_dl_page()
    gen_dl_api()
