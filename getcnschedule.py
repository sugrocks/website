import os
import json
import requests
from dateutil import parser
from datetime import datetime, date
from bs4 import BeautifulSoup

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
available_dates = []
schedule = []

# Using the same data and source as the small schedule widget we find on the "Pictures" for SU
url = 'http://schedule.adultswim.com/servlet/ScheduleServlet?action=GO&theDate=%s&timeZone=EST'
d = date.today()

def gen_schedule_api():
    # Get the file and let BS parse it
    now = '%02d/%02d/%d' % (d.month, d.day, d.year)
    r = requests.get(url % now)
    soup = BeautifulSoup(r.text, 'html5lib')

    for date in soup.find_all('select')[1].find_all('option'):
        if date['value'] != '0':
            available_dates.append(date['value'])

    for date in available_dates:
        print('=== ' + date + ' ===')
        r = requests.get(url % date)
        soup = BeautifulSoup(r.text, 'html5lib')
        trs = soup.find_all('table')[2].find('tr').find_all('td', recursive=False)[1]\
            .find_all('table', recursive=False)[1].find_all('td')[3]\
            .find_all('table', recursive=False)[2].find('tbody').find_all('tr', attrs={'valign': 'top'})
        i = 0
        for tr in trs:
            i += 1
            if i % 2 == 0:
                try:
                    t = tr.find(class_='timecell')
                    time = ''.join(t.strings).strip()
                    s = tr.find_all(class_='showcell')
                    sh = s[1].find('a')
                    show = ''.join(sh.strings).strip()
                    if show == 'See All Showings':
                        show = '???'
                    ep = s[3].string
                    print('%s: %s [%s]' % (time, ep, show))
                except:
                    i = i - 1


if __name__ == '__main__':
    gen_schedule_api()
