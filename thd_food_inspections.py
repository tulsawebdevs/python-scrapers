'''Scrape www.tulsa-health.org/food-safety/restaurant-inspections'''
import os
import re
import sys
import time
from itertools import izip_longest

import dateutil.parser
from geopy import geocoders
from pyquery import PyQuery as pq
import requests

from storage import couch, mongo, qrimp

STORING_TO_MONGO = False
if 'MONGO_SERVER' in os.environ:
    STORING_TO_MONGO = True

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
        facility['href'] = pq(f_link).attr('href')
        facility['_id'] = facility['href']
        facility_id = qrimp.save_facility(facility)
        facility_resp = requests.get(THD_ROOT + '/' + facility['href'])
        inspection_links = pq(facility_resp.content).find(
            'div#inspectionHistory a')
        for i_link in inspection_links:
            inspection = {}
            inspection['facility'] = facility['_id']
            inspection['href'] = pq(i_link).attr('href')
            inspection['_id'] = inspection['href']
            inspection_resp = requests.get(THD_ROOT + '/' + inspection['href'])
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

            couch.save_inspection(inspection)
            mongo.save_inspection(inspection)
            qrimp.save_inspection(inspection, facility['name'], facility_id)

            time.sleep(SECONDS_THROTTLE)

        if 'MAPQUEST_API_KEY' in os.environ:
            mq = geocoders.MapQuest(os.environ['MAPQUEST_API_KEY'])
            try:
                (place, (lat, long)) = mq.geocode(facility['location'])
                facility['latitude'] = lat
                facility['longitude'] = long
            # IndexError when location can't be geocoded
            except IndexError:
                pass

        couch.save_facility(facility)
        mongo.save_facility(facility)
        qrimp.save_facility(facility, facility_id)
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
