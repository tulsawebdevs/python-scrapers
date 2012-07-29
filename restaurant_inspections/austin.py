'''Scrape www.tulsa-health.org/food-safety/restaurant-inspections'''
import logging
import os
import re
import sys

from bs4 import BeautifulSoup
import requests

from storage.csvfiles import get_csv_writer

logging.basicConfig(filename="scraping_errors.log")
logger = logging.getLogger(__name__)

URL_ROOT = 'http://www.austintexas.gov/health/restaurant/scores.cfm'

SEARCH_PARAMS = {'begdate': '01/01/2012',
                 'enddate': '02/01/2012',
                 'selpara': '',
                 'estabname': None,
                 'estabcity': 'All',
                 'estabzip': 'All',
                 'Submit': 'Search'}


def main(argv=None):
    fields = ['url', 'name', 'location', 'city', 'zip', 'date', 'score']
    filename = 'austin.csv'
    csv_writer = get_csv_writer(filename, fields)

    print "Starting with url %s" % URL_ROOT
    print "POST params %s" % SEARCH_PARAMS
    search_resp = requests.post(URL_ROOT, data=SEARCH_PARAMS)
    soup = BeautifulSoup(search_resp.content)
    content = soup.find(id='col3_content')

    resultsHeader = content.p.text
    m = re.search('(?P<count>\d+) records found', resultsHeader)
    total_results = m.group('count').strip()
    print "Total Results: %s " % total_results

    data_table = content.table
    for data_row in data_table.find_all('tr'):
        if not getattr(data_row, 'td', False):
            continue
        cells = data_row.find_all('td')
        facility = {}
        facility['name'] = cells[0].string.strip()
        facility['location'] = cells[1].string.strip()
        facility['url'] = "%s#%s@%s" % (URL_ROOT,
                                     facility['name'],
                                     facility['location'])
        facility['city'] = cells[2].string.strip()
        facility['zip'] = cells[3].string.strip()
        facility['date'] = cells[4].string.strip()
        facility['score'] = cells[5].string.strip()
        print "Facility: %s" % facility
        csv_writer.writerow(facility)


if __name__ == "__main__":
    sys.exit(main())
