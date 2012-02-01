'''Scrape www.tulsa-health.org/food-safety/restaurant-inspections'''
import logging
import os
import re
import sys
import time
from itertools import izip_longest

import dateutil.parser
from geopy import geocoders
from pyquery import PyQuery as pq
import requests

from storage import save_facility, save_inspection

logging.basicConfig(filename="scraping_errors.log")
logger = logging.getLogger(__name__)

THD_ROOT = 'http://tulsa.ok.gegov.com/tulsa'
PAGE_SIZE = 20
SECONDS_THROTTLE = 1

SEARCH_PARAMS = {'startrow': 1,
               'source': 'quick',
               'precision': 'LIKE',
               'startDate': '01-07-2011',
               'endDate': '01-07-2012',
               'establishmentClass': 'ANY',
               'maxrows': PAGE_SIZE,
               'filter': 'est',
               'Search': 'Search'}


# http://stackoverflow.com/q/434287/571420
def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return izip_longest(*args, fillvalue=fillvalue)


def scrape_inspections(startrow):
    SEARCH_PARAMS.update({'startrow': startrow})
    search_resp = requests.post(THD_ROOT + '/index.cfm', data=SEARCH_PARAMS)
    doc = pq(search_resp.content)
    facility_links = pq(search_resp.content).find(
        'div#searchResults a.resultMore')
    for f_link in facility_links:
        facility = {}
        facility['url'] = THD_ROOT + '/' + pq(f_link).attr('href')
        facility['_id'] = facility['url']
        facility_resp = requests.get(facility['url'])
        inspection_links = pq(facility_resp.content).find(
            'div#inspectionHistory a')
        for i_link in inspection_links:
            inspection = {}
            inspection['facility'] = facility['_id']
            inspection['url'] = THD_ROOT + '/' + pq(i_link).attr('href')
            inspection['_id'] = inspection['url']
            inspection_resp = requests.get(inspection['url'])
            doc = pq(inspection_resp.content)
            facility['name'] = doc.find(
                'div#inspectionDetail h3').text()
            m = re.search('Location: (?P<location>.*)<br/>',
                         doc.find('div#inspectionDetail').html())
            facility['location'] = m.group('location').strip()

            info = doc.find('div#inspectionInfo tr td')
            for (counter, pair) in enumerate(grouper(info, 2)):
                value = pq(pair[1]).text()
                if counter == 0:
                    date = dateutil.parser.parse(value)
                    inspection['date'] = date.date()
                elif counter == 1:
                    facility['type'] = value
                elif counter == 2:
                    inspection['priority'] = value
                elif counter == 3:
                    inspection['purpose'] = value
                elif counter == 4:
                    inspection['result'] = value
                elif counter == 5:
                    inspection['actions'] = value

            print "inspection: %s" % inspection

            save_inspection(inspection)

            time.sleep(SECONDS_THROTTLE)

        if 'MAPQUEST_API_KEY' in os.environ:
            mq = geocoders.MapQuest(os.environ['MAPQUEST_API_KEY'])
            try:
                (place, (lat, long)) = mq.geocode(facility['location'])
                facility['latitude'] = lat
                facility['longitude'] = long
            except:
                logger.exception("Could not geocode location: %s"
                                 % facility['location'])

        save_facility(facility)
        print "facility: %s" % facility


def main(argv=None):
    if argv is None:
        argv = sys.argv
    search_resp = requests.post(THD_ROOT + '/index.cfm', data=SEARCH_PARAMS)
    doc = pq(search_resp.content)
    resultsHeader = pq(doc).find('#searchResultsHeader')
    total_results = pq(resultsHeader.find('strong')[2]).text()
    print "Total Results: %s " % total_results
    for startrow in range(1, int(total_results) + PAGE_SIZE, PAGE_SIZE):
        print "Scraping from %s to %s" % (startrow, startrow + PAGE_SIZE)
        scrape_inspections(startrow)


if __name__ == "__main__":
    sys.exit(main())
