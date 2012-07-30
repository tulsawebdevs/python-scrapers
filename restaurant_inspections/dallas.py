'''Scrape www.tulsa-health.org/food-safety/restaurant-inspections'''
import logging
import re
import sys

from bs4 import BeautifulSoup
import requests

from storage.csvfiles import get_csv_writer

logging.basicConfig(filename="scraping_errors.log")
logger = logging.getLogger(__name__)

URL_ROOT = 'http://www2.dallascityhall.com/FoodInspection/'

SEARCH_PARAMS = {'NAME': ' ',
                 'STNO': '',
                 'STNAME': '',
                 'ZIP': '',
                 'Submit': 'Search+Scores'}


def main(argv=None):
    fields = ['url', 'name', 'location', 'city', 'zip', 'date', 'score']
    filename = 'dallas.csv'
    csv_writer = get_csv_writer(filename, fields)

    print "Starting with url %s" % URL_ROOT
    print "POST params %s" % SEARCH_PARAMS
    resp = requests.post("%s%s" % (URL_ROOT, 'SearchScoresAction.cfm'),
                                          data=SEARCH_PARAMS)
    soup = BeautifulSoup(resp.content)
    body = soup.find('body')

    resultsHeader = body.find('span', {'class': 'style14'}).text
    m = re.search('Found (?P<count>\d+) records', resultsHeader)
    total_results = m.group('count').strip()
    print "Total Results: %s " % total_results

    data_table = body.find_all('table')[1]
    write_data_table(data_table, csv_writer)
    check_for_next_page(body, resp.cookies, csv_writer)


def check_for_next_page(body, cookies, csv_writer):
    pagination_table = body.find_all('table')[2]
    next_cell = pagination_table.find_all('td')[2]
    if next_cell.text.strip() == u'Next':
        next_uri = next_cell.a['href']
    get_next_page(next_uri, cookies, csv_writer)


def get_next_page(next_uri, cookies, csv_writer):
    resp = requests.get("%s%s" % (URL_ROOT, next_uri), cookies=cookies)
    soup = BeautifulSoup(resp.content)
    body = soup.find('body')
    cursor = body.find_all('p', {'class': 'style14'})[1].text
    print cursor.strip()
    data_table = body.find_all('table')[1]
    write_data_table(data_table, csv_writer)
    check_for_next_page(body, cookies, csv_writer)


def write_data_table(data_table, csv_writer):
    for data_row in data_table.find_all('tr'):
        if data_row.td.string == u'Name':
            continue
        cells = data_row.find_all('td')
        facility = {}
        facility['name'] = cells[0].string.strip()
        facility['location'] = cells[1].string.strip()
        facility['url'] = "%s#%s@%s" % (URL_ROOT,
                                     facility['name'],
                                     facility['location'])
        facility['city'] = 'Dallas'
        facility['zip'] = cells[3].string.strip()
        facility['date'] = cells[5].string.strip()
        facility['score'] = cells[6].string.strip()
        print "Facility: %s" % facility
        csv_writer.writerow(facility)


if __name__ == "__main__":
    sys.exit(main())
