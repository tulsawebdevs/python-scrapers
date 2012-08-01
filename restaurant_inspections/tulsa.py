import logging
import re
import sys
import time

from bs4 import BeautifulSoup
import requests

from storage.csvfiles import get_csv_writer, get_value

logging.basicConfig(filename="scraping_errors.log")
logger = logging.getLogger(__name__)

URL_ROOT = 'http://tulsa.ok.gegov.com/tulsa/'
PAGE_SIZE = 200
SECONDS_THROTTLE = 3

SEARCH_PARAMS = {'startrow': 1,
               'maxrows': PAGE_SIZE,
               'source': 'quick',
               'precision': 'LIKE',
               'startDate': '07-01-2011',
               'endDate': '07-31-2012',
               'establishmentClass': 'ANY',
               'filter': 'est',
               'Search': 'Search'}


def main(argv=None):
    fields = ['url', 'name', 'location', 'city', 'zip', 'date', 'score']
    filename = 'tulsa.csv'
    csv_writer = get_csv_writer(filename, fields)

    search_url = "%s%s" % (URL_ROOT, 'index.cfm')
    print "Starting with url %s" % search_url
    print "POST params %s" % SEARCH_PARAMS
    search_resp = requests.post(search_url, data=SEARCH_PARAMS)
    soup = BeautifulSoup(search_resp.content)
    content = soup.find(id='content')
    _scrape_content(content, csv_writer)



def _scrape_content(content, csv_writer):
    resultsHeader = content.find(id='searchResultsHeader')
    print ' '.join([text for text in resultsHeader.stripped_strings][:-2])

    facility_links = content.find(id='searchResults').find_all('a',
                                                    {'class': 'resultMore'})
    for facility_link in facility_links:
        facility_url = "%s%s" % (URL_ROOT, facility_link['href'])
        time.sleep(SECONDS_THROTTLE)
        facility_resp = requests.get(facility_url)
        facility_soup = BeautifulSoup(facility_resp.content)
        latest_inspection = facility_soup.find(id='inspectionHistory').ul.li
        latest_inspection_link = latest_inspection.a
        inspection_url = "%s%s" % (URL_ROOT, latest_inspection_link['href'])
        time.sleep(SECONDS_THROTTLE)
        inspection_resp = requests.get(inspection_url)
        inspection_soup = BeautifulSoup(inspection_resp.content)
        inspection_detail = inspection_soup.find(id='inspectionDetail')
        facility = {}
        facility['name'] = get_value(inspection_detail.h3)
        m = re.search('Location:  (?P<location>.*)[\r\n\t]+Smoking', inspection_detail.text)
        facility['location'] = m.group('location').strip()
        facility['url'] = inspection_url
        facility['city'] = 'Tulsa'
        m = re.search('.*(?P<zip>\d{5})$', facility['location'])
        facility['zip'] = m.group('zip').strip()
        inspection_info = inspection_detail.find(id='inspectionInfo')
        inspection_date_row = inspection_info.table.tr
        facility['date'] = get_value(inspection_date_row.find_all('td')[1])
        inspection_violations = inspection_detail.find(id='inspectionViolations')
        facility['score'] = _get_inspection_score(inspection_violations)
        print "Facility: %s" % facility
        csv_writer.writerow(facility)

    next_page_link = content.find('a', text='Next %s' % PAGE_SIZE)
    if next_page_link:
        time.sleep(SECONDS_THROTTLE)
        next_url = "%s%s" % (URL_ROOT, next_page_link['href'])
        search_resp = requests.get(next_url)
        soup = BeautifulSoup(search_resp.content)
        content = soup.find(id='content')
        _scrape_content(content, csv_writer)


def _get_inspection_score(inspection_violations):
    score = 100
    violations = []
    for violation_type in inspection_violations.find_all('div'):
        v_type = violation_type.a['href']
        m = re.search('info.cfm\?.*#(?P<type>.*)', v_type)
        v_type = m.group('type')
        for item in violation_type.find_next_sibling('ol').find_all('li'):
            violations.append(v_type)
    for violation in violations:
        if violation == 'CDC':
            score = score - 14
        elif violation == 'Other':
            score = score - 6
        elif violation == 'General':
            score = score - 2
    return score


if __name__ == "__main__":
    sys.exit(main())
