import os
import json
import hashlib
import requests
from dateutil import parser
from bs4 import BeautifulSoup

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def grab_cn(url):
    # Parse the XML from CN
    cn = []  # Init our list that will hold our dicts
    r = requests.get(url)  # Get the file
    soup = BeautifulSoup(r.text, 'html5lib')  # Parse the file

    # For each episodes
    for ep in soup.find_all('show'):
        # Parse the date and time to a python datatime object
        # Example of values: ep['date'] = 'March 10' / ep['time'] = '7:00 PM'
        parsedtime = parser.parse('%s %s -0500' % (ep['date'], ep['time']))

        # Add it to the list
        cn.append({
            'id': int(ep['episodeid']),
            'title': ep['episode'].strip(),
            'date': ep['date'],
            'time': ep['time'],
            'timestamp': int(parsedtime.timestamp())
        })

    return cn


def grab_zap(url):
    # Parse date from Zap2It (Screener)
    zap = []  # Init our list that will hold our dicts
    r = requests.get(url)  # Get the file
    soup = BeautifulSoup(r.text, 'html5lib')  # Parse the file
    trs = soup.find(id='zc-episode-guide').find_all('tr')  # Get directly the <tr> from the guide

    for tr in trs[1:6]:  # 5 elements, excluding table header
        # Season number
        s = tr.find(attrs={'itemprop': 'partOfSeason'}).contents[0]
        # Episode number
        e = tr.find(attrs={'itemprop': 'episodeNumber'}).contents[0]
        # Title
        t = tr.find(attrs={'itemprop': 'name'}).contents[0]
        # Air date
        d = tr.find(attrs={'itemprop': 'datePublished'}).contents[0]
        # Paragraph with synopsis (if any)
        o = tr.find('p').contents
        p = None
        if len(o) != 0:  # if there's something inside this <p>, it means we have a synopsis
            p = o[0]

        # Generate unique id with our content
        m = hashlib.md5()
        m.update(('[S%sE%s] %s (%s) - Airing: %s' % (s, e, t, p, d)).encode('utf-8'))
        id = str(int(m.hexdigest(), 16))[0:12]

        # Add it to the list
        zap.append({
            'id': int(id),
            'title': t,
            'date': d,
            'episode': 'S' + s + 'E' + e,
            'synopsis': p
        })

    return zap


def gen_schedule_api(cn=[], zap=[]):
    # Save our schedules in a json file
    with open(os.path.join(THIS_DIR, 'api', 'schedule.json'), 'w') as f:
        f.write(json.dumps({'cn': cn, 'zap': zap}, indent=2, sort_keys=True))


if __name__ == '__main__':
    # Get data from CN
    show_id = '399692'
    search_term = 'steven universe'
    cn_url = 'http://www.cartoonnetwork.com/cnschedule/xmlServices/ScheduleServices?' +\
             'methodName=getAllShowings&showId=%s&name=%s&timezone=EST' % (show_id, search_term)
    cn = grab_cn(cn_url)

    # Get data from Zap2It (Screener)
    s_id = 'EP01616432'
    t = 'Steven+Universe'
    zap_url = 'http://tvlistings.zap2it.com/tvlistings/ZCProgram.do?sId=%s&t=%s&method=getEpisodesForShow&desc=on' % (s_id, t)
    zap = grab_zap(zap_url)

    # Gen our json
    gen_schedule_api(cn, zap)
