import os
import json
import hashlib
import requests
import better_exceptions

from dateutil import parser
from datetime import datetime
from bs4 import BeautifulSoup

better_exceptions.MAX_LENGTH = None
THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def grab_cn(url):
    # Parse the XML from CN
    cn_list = []  # Init our list that will hold our dicts
    r = requests.get(url)  # Get the file
    soup = BeautifulSoup(r.text, 'html5lib')  # Parse the file

    # For each episodes
    for ep in soup.find_all('show'):
        # Parse the date and time to a python datatime object
        # Example of values: ep['date'] = 'March 10' / ep['time'] = '7:00 PM'
        parsedtime = parser.parse('%s %s -0500' % (ep['date'], ep['time']))

        # Add it to the list
        cn_list.append({
            'id': int(ep['episodeid']),
            'title': ep['episode'].strip(),
            'date': ep['date'],
            'time': ep['time'],
            'timestamp': int(parsedtime.timestamp())
        })

    return cn_list


def grab_zap(url):
    # Parse date from Zap2It
    zap_list = []  # Init our list that will hold our dicts
    r = requests.get(url)  # Get the file
    soup = BeautifulSoup(r.text, 'html5lib')  # Parse the file
    trs = soup.find(id='zc-episode-guide').find_all('tr')  # Get directly the <tr> from the guide

    for tr in trs[1:6]:  # 5 elements, excluding table header
        episode = '_unknown_'

        # Season number
        try:
            episode = 'S' + tr.find(attrs={'itemprop': 'partOfSeason'}).contents[0]
        except:
            pass

        # Episode number
        try:
            episode = episode + 'E' + tr.find(attrs={'itemprop': 'episodeNumber'}).contents[0]
        except:
            pass

        # Title
        try:
            title = tr.find(attrs={'itemprop': 'name'}).contents[0]
        except:
            title = '_unknown_'

        # Air date
        try:
            date_pub = tr.find(attrs={'itemprop': 'datePublished'}).contents[0]
        except:
            date_pub = '_unknown_'

        # Paragraph with synopsis (if any)
        try:
            synopsis_p = tr.find('p').contents
            if len(synopsis_p) != 0:  # if there's something inside this <p>, it means we have a synopsis
                synopsis = synopsis_p[0]
        except:
            synopsis = None

        # Generate unique id with our content
        m = hashlib.md5()
        m.update(('%s %s %s' % (episode, title, date_pub)).encode('utf-8'))
        gen_id = str(int(m.hexdigest(), 16))[0:12]

        # Add it to the list
        zap_list.append({
            'id': int(gen_id),
            'title': title,
            'date': date_pub,
            'episode': episode,
            'synopsis': synopsis
        })

    return zap_list


def gen_schedule_api(cn, zap):
    details = {'generated': int(datetime.utcnow().timestamp())}

    # Save our schedules in a json file
    with open(os.path.join(THIS_DIR, 'api', 'koschedule.json'), 'w') as f:
        f.write(json.dumps({'_': details, 'cn': cn, 'zap': zap}, indent=2, sort_keys=True))


if __name__ == '__main__':
    # URL with the data from CN
    show_id = '2079533'
    search_term = 'OK K.O.! Let\'s Be Heroes'
    cn_url = 'http://www.cartoonnetwork.com/cnschedule/xmlServices/ScheduleServices?' +\
             'methodName=getAllShowings&showId=%s&name=%s&timezone=EST' % (show_id, search_term)

    # URL with the data from Zap2It
    s_id = 'EP02378975'
    t = 'OK+K.O.%21+Let%27s+Be+Heroes%21'
    zap_url = 'http://tvlistings.zap2it.com/tvlistings/ZCProgram.do?sId=%s&t=%s&method=getEpisodesForShow&desc=on' % (s_id, t)

    # Get the data and generate our json
    gen_schedule_api(
        grab_cn(cn_url),
        grab_zap(zap_url)
    )
