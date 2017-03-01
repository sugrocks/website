import os
import json
import crayons
import requests
from dateutil import parser
from datetime import datetime
from bs4 import BeautifulSoup

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
schedule = []

# Using the same data and source as the small schedule widget we find on the "Pictures" for SU
showId = '399692'
searchTerm = 'steven universe'
url = 'http://www.cartoonnetwork.com/cnschedule/xmlServices/ScheduleServices?methodName=getAllShowings&showId=%s&title=%s&name=%s&timezone=EST' % (showId, searchTerm, searchTerm)

# Get the file and let BS parse it
r = requests.get(url)
soup = BeautifulSoup(r.text, 'html5lib')

# For each episodes
for ep in soup.find_all('show'):
    # Parse the date and time to a python datatime object
    # Example of values: ep['date'] = 'March 10' / ep['time'] = '7:00 PM'
    parsedtime = parser.parse('%s %s -0500' % (ep['date'], ep['time']))

    # Add it to the list
    schedule.append({
        'id': int(ep['episodeid']),
        'title': ep['episode'].strip(),
        'date': ep['date'],
        'time': ep['time'],
        'timestamp': int(parsedtime.timestamp())
    })

# Save our list as a json
with open(os.path.join(THIS_DIR, 'api', 'schedule.json'), 'w') as f:
    f.write(json.dumps(schedule, indent=2, sort_keys=True))
