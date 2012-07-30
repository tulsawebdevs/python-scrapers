'''Scrape www.tulsa-health.org/food-safety/restaurant-inspections'''
import logging
import hashlib
import os
import re
import sys
import time
from itertools import izip_longest

import dateutil.parser
from geopy import geocoders
from pyquery import PyQuery as pq
import requests

from storage import save_facility, save_inspection, save_violation

logging.basicConfig(filename="scraping_errors.log")
logger = logging.getLogger(__name__)

THD_ROOT = 'http://tulsa.ok.gegov.com/tulsa'
PAGE_SIZE = 20
SECONDS_THROTTLE = 3
if 'SECONDS_THROTTLE' in os.environ:
    SECONDS_THROTTLE = os.environ['SECONDS_THROTTLE']


SEARCH_PARAMS = {'startrow': 1,
               'maxrows': PAGE_SIZE,
               'source': 'quick',
               'precision': 'LIKE',
               'startDate': '01-07-2011',
               'endDate': '01-07-2012',
               'establishmentClass': 'ANY',
               'filter': 'est',
               'Search': 'Search'}


# http://stackoverflow.com/q/434287/571420
def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return izip_longest(*args, fillvalue=fillvalue)


def scrape_facility(facility_url):
    try:
        facility = {}
        facility['url'] = facility_url
        facility['_id'] = facility['url']
        facility_resp = requests.get(facility['url'])
        # easier to get name, location, type from the inspection page
        # TODO: refactor to pull from facility page to avoid skipping
        # facilities with no inspections
        inspection_links = pq(facility_resp.content).find(
            'div#inspectionHistory a')
        inspection_url = THD_ROOT + '/' + pq(inspection_links[0]).attr('href')
        time.sleep(SECONDS_THROTTLE)
        inspection_resp = requests.get(inspection_url)
        doc = pq(inspection_resp.content)
        facility['name'] = doc.find(
            'div#inspectionDetail h3').text()
        m = re.search('Location: (?P<location>.*)<br/>',
                     doc.find('div#inspectionDetail').html())
        facility['location'] = m.group('location').strip()
        info = doc.find('div#inspectionInfo tr td')
        for (counter, pair) in enumerate(grouper(info, 2)):
            value = pq(pair[1]).text()
            if counter == 1:
                facility['type'] = value
        if 'MAPQUEST_API_KEY' in os.environ:
            mq = geocoders.MapQuest(os.environ['MAPQUEST_API_KEY'])
            try:
                (place, (lat, long)) = mq.geocode(facility.get('location', ''))
                facility['latitude'] = lat
                facility['longitude'] = long
            except:
                logger.exception("Could not geocode location '%s' for %s" %
                                 (facility.get('location', ''),
                                  facility.get('name', '')))
        print "facility: %s" % facility
        facility['id'] = save_facility(facility)
        return facility, facility_resp
    except:
            logger.exception("Could not scrape facility %s" %
                             facility.get('url', ''))


def scrape_inspection(inspection_url, facility):
    try:
        inspection = {}
        inspection['facility'] = facility['_id']
        if 'id' in facility:
            inspection['facility_id'] = facility['id']
        inspection['_id'] = inspection_url
        inspection['url'] = inspection_url
        inspection_resp = requests.get(inspection['url'])
        doc = pq(inspection_resp.content)

        info = doc.find('div#inspectionInfo tr td')
        for (counter, pair) in enumerate(grouper(info, 2)):
            value = pq(pair[1]).text()
            if counter == 0:
                date = dateutil.parser.parse(value)
                inspection['date'] = date.date()
            elif counter == 2:
                inspection['priority'] = value
            elif counter == 3:
                inspection['purpose'] = value
            elif counter == 4:
                inspection['result'] = value
            elif counter == 5:
                inspection['actions'] = value

        print "inspection: %s" % inspection
        inspection['id'] = save_inspection(inspection)
        return inspection, inspection_resp
    except:
        logger.exception("Could not scrape inspection %s" %
                         inspection.get('url', ''))



def scrape_violations(inspection_page_content, inspection):
    doc = pq(inspection_page_content)
    violationTypes = doc.find('div#violationTypes')
    violations = []
    for (counter, violationTypeEl) in enumerate(violationTypes):
        violation_type_link = pq(violationTypeEl).children('a')[0]
        violation_type = pq(violation_type_link).attr('href')
        m = re.search('info.cfm\?.*#(?P<type>.*)', violation_type)
        violation_type = m.group('type')
        violationEls = pq(violationTypeEl).siblings('ol')[counter]
        for violationEl in violationEls:
            violation = {}
            violation['inspection'] = inspection
            violation['type'] = violation_type
            violationObj = pq(violationEl)
            food_code = violationObj.attr('value')
            if food_code:
                violation['food_code'] = food_code
                violation['_id'] = hashlib.md5(inspection['_id'] +
                                               food_code).hexdigest()
                violation['comments'] = violationObj.text()
                print "violation: %s" % violation
                violations.append(violation)
                save_violation(violation)
    score = 100
    for violation in violations:
        print violation['type'] + " " + str(score)
        if violation['type'] == 'CDC':
            score = score - 14
        elif violation['type'] == 'Other':
            score = score - 6
        elif violation['type'] == 'General':
            score = score - 2
    inspection['score'] = score
    save_inspection(inspection)
    return violations

def scrape_inspections(startrow):
    try:
        SEARCH_PARAMS.update({'startrow': startrow})
        search_resp = requests.post(THD_ROOT + '/index.cfm', data=SEARCH_PARAMS)
        facility_links = pq(search_resp.content).find(
            'div#searchResults a.resultMore')
        for f_link in facility_links:
            facility_url = THD_ROOT + '/' + pq(f_link).attr('href')
            time.sleep(SECONDS_THROTTLE)
            facility, facility_resp = scrape_facility(facility_url)

            inspection_links = pq(facility_resp.content).find(
                'div#inspectionHistory a')
            for i_link in inspection_links:
                inspection_url = THD_ROOT + '/' + pq(i_link).attr('href')
                inspection, inspection_resp = scrape_inspection(inspection_url,
                                                                facility)
                scrape_violations(inspection_resp.content,
                                               inspection)
                time.sleep(SECONDS_THROTTLE)

            if 'MAPQUEST_API_KEY' in os.environ:
                mq = geocoders.MapQuest(os.environ['MAPQUEST_API_KEY'])
                try:
                    (place, (lat, long)) = mq.geocode(facility.get('location', ''))
                    facility['latitude'] = lat
                    facility['longitude'] = long
                except:
                    logger.exception("Could not geocode location '%s' for %s" %
                                     (facility.get('location', ''),
                                      facility.get('name', '')))

            print "facility: %s" % facility
            facility['id'] = save_facility(facility)
    except:
        logger.exception("Could not scrape at startrow: %s" % startrow)



def main(argv=None):
    if argv is None:
        argv = sys.argv
    if "MAX_RESULTS" in os.environ:
        total_results = os.environ['MAX_RESULTS']
    else:
        index_url = THD_ROOT + '/index.cfm'
        print "Starting with url %s" % index_url
        print "POST params %s" % SEARCH_PARAMS
        search_resp = requests.post(index_url, data=SEARCH_PARAMS)
        doc = pq(search_resp.content)
        resultsHeader = pq(doc).find('#searchResultsHeader')
        total_results = pq(resultsHeader.find('strong')[2]).text()
    print "Total Results: %s " % total_results
    for startrow in range(1, int(total_results) + PAGE_SIZE, PAGE_SIZE):
        print "Scraping from %s to %s" % (startrow, startrow + PAGE_SIZE)
        scrape_inspections(startrow)


if __name__ == "__main__":
    sys.exit(main())