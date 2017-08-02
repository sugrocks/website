import os
import re
import sys
import json
import math
import crayons
import requests
import collections
import better_exceptions

from dateutil import parser
from bs4 import BeautifulSoup
from operator import itemgetter
from datetime import date, datetime

better_exceptions.MAX_LENGTH = None
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
last_group = ''


def log(group, text):
    global last_group

    if last_group != group:
        print('')

    last_group = group
    sys.stdout.write('\x1b[2K\r[{} - {}] {}'.format(
        crayons.blue(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), crayons.blue(group), crayons.green(text)))


def pretty(text):
    # This strips and removes tabs, new lines and (double) spaces from our string
    # Doesn't fucking always work
    text = text.replace('\t', '')
    text = text.replace('\n', '')
    text = text.replace('\\t', '')
    text = text.replace('\\n', '')
    text = re.sub(' +', ' ', text)
    text = text.strip()
    if text.startswith('"'):
        text = text[1:]
    if text.endswith('"'):
        text = text[:-1]
    return text


def fix_showname(show_name):
    if show_name == 'MOVIE:':  # Remove the colon plz
        return 'MOVIE'
    elif show_name == 'SPECIAL:':  # Remove the colon plz
        return 'SPECIAL'
    elif show_name == 'Cloudy':  # Fix name
        return 'Cloudy with a Chance of Meatballs'
    elif show_name == 'Cloudy With a Chance of Meatballs':  # Fix name
        return 'Cloudy with a Chance of Meatballs'
    elif show_name == 'The Amazing World of Gumball':  # Fix name
        return 'Amazing World of Gumball'

    return show_name


def grab_cnschedule(url):
    # Get the schedule from the "backdoor" and parse it for every available day
    schedule = {}
    available_dates = []

    log('cn', 'Will get today\'s page')

    # Get the file for today and let BS parse it
    d = date.today()
    now = '%02d/%02d/%d' % (d.month, d.day, d.year)
    r = requests.get(url % now)

    log('cn', 'Parsing...')

    soup = BeautifulSoup(r.text, 'html5lib')

    # We'll now save all the available dates
    for select_date in soup.find_all('select')[1].find_all('option'):
        if select_date['value'] != '0':
            available_dates.append(select_date['value'])

    log('cn', 'Parsed. Available dates: ' + ', '.join(available_dates))

    # Now, we'll go throught each day
    for available_date in available_dates:
        # Get a YYYY-MM-DD version of the date
        parsed_date = parser.parse(available_date).strftime('%Y-%m-%d')
        # Init the list and the increment counter
        schedule[parsed_date] = {
            'source': 'Cartoon Network',
            'schedule': []
        }
        i = 0

        log('cn', 'Downloading and parsing ' + parsed_date)

        # Get the day's page
        r = requests.get(url % available_date)
        soup = BeautifulSoup(r.text, 'html5lib')

        log('cn', 'Parsed. Extracting data...')

        # And let's go directly to where the list is (yup, it's a bit complicated)
        trs = soup.find_all('table')[2].find('tr').find_all('td', recursive=False)[1]\
            .find_all('table', recursive=False)[1].find_all('td')[3]\
            .find_all('table', recursive=False)[2].find('tbody').find_all('tr', attrs={'valign': 'top'})

        # And now, for each lines...
        for i, tr in enumerate(trs):
            alt_table = False
            el_time = tr.find(class_='timecell')  # Get the element that contains the time

            if el_time is None:
                el_time = tr.find(class_='timeoncell')
                alt_table = True

            if not pretty(''.join(el_time.strings)).endswith('m'):
                continue

            try:
                # Get the "time" and "show" details
                if alt_table:  # Sometimes, it's using '[...]oncell' instead of just '[...]cell'
                    el_time = tr.find(class_='timeoncell')   # Get the element that contains the time
                    el_show = tr.find_all(class_='showoncell')  # Get the element**s** that contains show details
                    el_show_name = el_show[0].find('a')  # Get the element that contains the show name
                    episode_name = el_show[2].string  # Get the episode title
                    show_name = pretty(''.join(el_show_name.strings))  # Get the actual show name

                    # Show might not be under a link, so we try to get the first string in the element then
                    if show_name == 'See All Showings':
                        show_name = pretty(el_show[0].contents[0])

                else:  # If it's not, let's get our values
                    el_show = tr.find_all(class_='showcell')  # Get the element**s** that contains show details
                    el_show_name = el_show[1].find('a')  # Get the element that contains the show name
                    episode_name = el_show[3].string  # Get the episode title
                    show_name = pretty(''.join(el_show_name.strings))  # Get the actual show name

                    # Show might not be under a link, so we try to get the first string in the element then
                    if show_name == 'See All Showings':
                        show_name = pretty(el_show[1].contents[0])

                show_name = fix_showname(show_name)

                if episode_name is None:  # If no episode title is found, return an empty string
                    episode_name = ''

                try:
                    el_next_time = trs[i + 2].find(class_='timecell')
                    if el_next_time is None:
                        el_next_time = tr.find(class_='timeoncell')   # Get the element that contains the time

                    next_time = pretty(''.join(el_next_time.strings))
                except IndexError:
                    next_time = '6:00 am'

                time = pretty(''.join(el_time.strings))  # Get the air time
                parsed_datetime = parser.parse('%s %s -0400' % (parsed_date, time))  # And let's parse it
                parsed_next_datetime = parser.parse('%s %s -0400' % (parsed_date, next_time))  # And let's parse it

                # If it's before 6am and after (including) 8pm, it's the adultswim part
                if parsed_datetime.hour < 6 or parsed_datetime.hour >= 20:
                    continue

                slots = math.ceil(((int(parsed_next_datetime.timestamp()) - int(parsed_datetime.timestamp())) / 60) / 15)
                if slots < 1:
                    slots = 2

                # Add all the details to our schedule list
                schedule[parsed_date]['schedule'].append({
                    'date': parsed_date,
                    'time': time,
                    'timestamp': int(parsed_datetime.timestamp()),
                    'timestamp_end': int(parsed_next_datetime.timestamp()),
                    'show': show_name,
                    'title': episode_name,
                    'slots': slots
                })
            except:
                # If something goes wrong, show the <tr> and raise the error
                print(tr)
                raise

        log('cn', 'Data extracted.')

    # And now that we have everything we need,
    # let's return our list
    log('cn', 'Done!')
    return schedule


def grab_zapschedule(url):
    # Get the schedule from the "backdoor" and parse it for every available day
    schedule = {}
    available_dates = []

    log('zap', 'Will get today\'s page')

    # Get the file for today and let BS parse it
    r = requests.get(url)

    log('zap', 'Parsing...')

    soup = BeautifulSoup(r.text, 'html5lib')

    # We'll now save all the available dates
    for select_date in soup.find(id='zc-ssl-dayNav-popup').find_all(class_='zc-topbar-dropdown-item'):
        available_dates.append({'date': select_date.string, 'url': select_date['href']})

    log('zap', 'Parsed. Found ' + str(len(available_dates)) + ' days available')

    # Now, we'll go throught each day
    for available_date in available_dates:
        # Get a YYYY-MM-DD version of the date
        parsed_date = parser.parse(available_date['date']).strftime('%Y-%m-%d')
        # Init the list and the increment counter
        schedule[parsed_date] = {
            'source': 'Zap2it',
            'schedule': []
        }
        i = 0

        log('zap', 'Downloading and parsing ' + parsed_date)

        # Get the day's page
        r = requests.get(available_date['url'])
        soup = BeautifulSoup(r.text, 'html5lib')

        log('zap', 'Parsed. Extracting data...')

        # And let's go directly to where the list is (yup, it's a bit complicated)
        trs = soup.find_all(class_='zc-ssl-pg')

        # And now, for each lines...
        for i, tr in enumerate(trs):
            # Well, actually only the even ones
            if tr['id'].startswith('row1'):
                try:
                    # Get the "time" and "show" details
                    el_time = tr.find(class_='zc-ssl-pg-time')  # Get the element that contains the time
                    el_show_name = tr.find(class_='zc-ssl-pg-title')
                    el_episodenumber = tr.find(class_='zc-ssl-pg-ep')

                    try:
                        el_next_time = trs[i + 1].find(class_='zc-ssl-pg-time')
                        next_time = pretty(''.join(el_next_time.strings))
                    except IndexError:
                        next_time = '6:00 am'

                    show_name = pretty(''.join(el_show_name.strings))  # Get the actual show name

                    try:
                        episode_name = pretty(''.join(el_episodenumber.strings))
                    except:
                        episode_name = ''

                    show_name = fix_showname(show_name)

                    time = pretty(''.join(el_time.strings)).lower()  # Get the air time
                    parsed_datetime = parser.parse('%s %s -0500' % (parsed_date, time))  # And let's parse it
                    parsed_next_datetime = parser.parse('%s %s -0500' % (parsed_date, next_time))  # And let's parse it

                    # If it's before 6am and after (including) 8pm, it's the adultswim part
                    if parsed_datetime.hour < 6 or parsed_datetime.hour >= 20:
                        continue

                    slots = math.ceil(((int(parsed_next_datetime.timestamp()) - int(parsed_datetime.timestamp())) / 60) / 15)
                    if slots < 1:
                        slots = 2

                    # Add all the details to our schedule list
                    schedule[parsed_date]['schedule'].append({
                        'date': parsed_date,
                        'time': time,
                        'timestamp': int(parsed_datetime.timestamp()),
                        'timestamp_end': int(parsed_next_datetime.timestamp()),
                        'show': show_name,
                        'title': episode_name,
                        'slots': slots
                    })
                except:
                    # If something goes wrong, show the <tr> and raise the error
                    print(tr)
                    raise

        log('zap', 'Data extracted.')

    # And now that we have everything we need,
    # let's return our list
    log('zap', 'Done!')
    return schedule


def merge_schedules(cn_sch, zap_sch):
    log('merge', 'Fixing empty schedules...')
    for s_date, values in cn_sch.items():
        if len(values['schedule']) == 0:
            cn_sch[s_date] = zap_sch[s_date]

    log('merge', 'Adding missing days from Zap2it...')
    for s_date, __ in zap_sch.items():
        if s_date not in cn_sch:
            cn_sch[s_date] = zap_sch[s_date]

    log('merge', 'Ordering...')
    for day in cn_sch:
        cn_sch[day]['schedule'] = sorted(cn_sch[day]['schedule'], key=itemgetter('timestamp'))

    ordered = collections.OrderedDict(sorted(cn_sch.items()))

    log('merge', 'Done!')
    return ordered


def gen_api(sch):
    # Save our schedule in a json file
    log('json', 'Generating json...')

    sch['_'] = {'generated': int(datetime.utcnow().timestamp())}

    with open(os.path.join(THIS_DIR, 'api', 'cnschedule.json'), 'w') as f:
        f.write(json.dumps(sch, indent=2, sort_keys=False))

    log('json', 'Done!')


if __name__ == '__main__':
    # Using the [as] "backdoor", where we can put a date in the URL
    source_url = 'http://schedule.adultswim.com/servlet/ScheduleServlet?action=GO&theDate=%s&timeZone=EST'
    # First we grab CN's schedule and put it in a list
    cn_schedule = grab_cnschedule(source_url)

    # Using Zap2it's schedule list for CN to get the list
    source_url = 'http://tvschedule.zap2it.com/tvlistings/ZCSGrid.do?sgt=list&stnNum=12131&aid=tvschedule'
    # Now we grab Zap2it's schedule and put it in a list
    zap_schedule = grab_zapschedule(source_url)

    # We merge and order the schedules
    saved_schedule = merge_schedules(cn_schedule, zap_schedule)

    # Then we save what we've got
    gen_api(saved_schedule)
