import os
import re
import json
import requests

from datetime import date
from dateutil import parser
from bs4 import BeautifulSoup

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def pretty(text):
    # This strips and removes tabs, new lines and (double) spaces from our string
    text = re.sub('\t', ' ', text)
    text = re.sub('\n', ' ', text)
    text = re.sub(' +', ' ', text)
    return text.strip()


def grab_schedule(url):
    # Get the schedule from the "backdoor" and parse it for every available day
    schedule = {}
    available_dates = []

    # Get the file for today and let BS parse it
    d = date.today()
    now = '%02d/%02d/%d' % (d.month, d.day, d.year)
    r = requests.get(url % now)
    soup = BeautifulSoup(r.text, 'html5lib')

    # We'll now save all the available dates
    for select_date in soup.find_all('select')[1].find_all('option'):
        if select_date['value'] != '0':
            available_dates.append(select_date['value'])

    # Now, we'll go throught each day
    for available_date in available_dates:
        # Get a YYYY-MM-DD version of the date
        parsed_date = parser.parse(available_date).strftime('%Y-%m-%d')
        # Init the list and the increment counter
        schedule[parsed_date] = []
        i = 0

        # Get the day's page
        r = requests.get(url % available_date)
        soup = BeautifulSoup(r.text, 'html5lib')

        # And let's go directly to where the list is (yup, it's a bit complicated)
        trs = soup.find_all('table')[2].find('tr').find_all('td', recursive=False)[1]\
            .find_all('table', recursive=False)[1].find_all('td')[3]\
            .find_all('table', recursive=False)[2].find('tbody').find_all('tr', attrs={'valign': 'top'})

        # And now, for each lines...
        for tr in trs:
            i += 1
            # Well, actually only the even ones
            if i % 2 == 0:
                try:
                    # Get the "time" and "show" details
                    el_time = tr.find(class_='timecell')  # Get the element that contains the time
                    el_show = tr.find_all(class_='showcell')  # Get the element**s** that contains show details

                    if el_time is None:  # Sometime, it's using '[...]oncell' instead of just '[...]cell'
                        el_time = tr.find(class_='timeoncell')   # Get the element that contains the time
                        el_show = tr.find_all(class_='showoncell')  # Get the element**s** that contains show details
                        el_show_name = el_show[0].find('a')  # Get the element that contains the show name
                        el_episodenumber = el_show[2].string  # Get the episode number
                        show_name = pretty(''.join(el_show_name.strings))  # Get the actual show name

                        # Show might not be under a link, so we try to get the first string in the element then
                        if show_name == 'See All Showings':
                            show_name = pretty(el_show[0].contents[0])
                    else:  # If it's not, let's get our values
                        el_show_name = el_show[1].find('a')  # Get the element that contains the show name
                        el_episodenumber = el_show[3].string  # Get the episode number
                        show_name = pretty(''.join(el_show_name.strings))  # Get the actual show name

                        # Show might not be under a link, so we try to get the first string in the element then
                        if show_name == 'See All Showings':
                            show_name = pretty(el_show[1].contents[0])

                    if show_name == 'MOVIE:':  # Remove the colon plz
                        show_name = 'MOVIE'

                    time = pretty(''.join(el_time.strings))  # Get the air time
                    parsed_datetime = parser.parse('%s %s -0500' % (parsed_date, time))  # And let's parse it

                    # If it's before 6am and after (including) 8pm, it's the adultswim part
                    if parsed_datetime.hour < 6 or parsed_datetime.hour >= 20:
                        continue

                    # Add all the details to our schedule list
                    schedule[parsed_date].append({
                        'date': available_date,
                        'time': time,
                        'timestamp': int(parsed_datetime.timestamp()),
                        'show': show_name,
                        'title': el_episodenumber
                    })
                except:
                    # If something goes wrong, show the <tr> and raise the error
                    print(tr)
                    raise

    # And now that we have everything we need,
    # let's return our list
    return schedule


def gen_api(sch):
    # Save our schedule in a json file
    with open(os.path.join(THIS_DIR, 'api', 'cnschedule.json'), 'w') as f:
        f.write(json.dumps(sch, indent=2, sort_keys=True))


if __name__ == '__main__':
    # Using the same data and source as the small schedule widget we find on the "Pictures" for SU
    source_url = 'http://schedule.adultswim.com/servlet/ScheduleServlet?action=GO&theDate=%s&timeZone=EST'

    # First we grab the schedule and put this in a pretty list
    saved_schedule = grab_schedule(source_url)
    # Then we save what we've got
    gen_api(saved_schedule)
