import logging
import re
import sys
import time
import re

from bs4 import BeautifulSoup
import requests

from storage.csvfiles import get_csv_writer, get_value

logging.basicConfig(filename="scraping_errors.log")
logger = logging.getLogger(__name__)

URL_ROOT = 'http://samhd.tx.gegov.com/San Antonio/'
PAGE_SIZE = 200
SECONDS_THROTTLE = 2


DEMERIT_MULTIPLIER=3

SEARCH_PARAMS = {
'1':1,
'sd':'09/20/2012',
'ed':'10/20/2012',
'rel2':'L.licenseName',
'rel3':'L.licenseName',
'dtRng':'NO',
'pre':'similar',
'smoking':'ANY',
        
}


def main(argv=None):
    fields = ['url', 'name', 'location', 'city', 'zip', 'date', 'score']
    filename = 'sanantonio.csv'
    csv_writer = get_csv_writer(filename, fields)

    search_url = "%s%s" % (URL_ROOT, 'search.cfm')
    print "Starting with url %s" % search_url
    print "POST params %s" % SEARCH_PARAMS
    search_resp = requests.post(search_url, data=SEARCH_PARAMS)
    soup = BeautifulSoup(search_resp.content)
    content = soup.find('td')

    page_links = content.find_all(href=re.compile("search"))

    for page_link in page_links:
        next_page_url = "%s%s" % (URL_ROOT, page_link['href'])
        next_page_content = requests.get(next_page_url)
        next_page_soup=BeautifulSoup(next_page_content.content)
        content = next_page_soup.find('td')
        _scrape_content(content, csv_writer)



def _scrape_content(content, csv_writer):

    facility_links = content.find_all(href=re.compile("estab"))
    
    for facility_link in facility_links:
        facility={}
        facility['city'] = 'San Antonio'
        
        next_b=facility_link.find('b')
        if next_b:
            facility['name']=next_b.string

        addr_div=facility_link.next_sibling.next_sibling.get_text().strip()        
        addr_div=re.sub('\s\s+',' ',addr_div) #remove extra spaces
        addr_div=re.sub('\s,+',',',addr_div)#remove space before comma
        facility['location'] =addr_div
        
        m = re.search('.*(?P<zip>\d{5})$', facility['location'])
        facility['zip'] = m.group('zip').strip()

        facility_url = "%s%s" % (URL_ROOT, facility_link['href'])
        facility['url'] = facility_url
        
        facility_resp = requests.get(facility_url)
        facility_soup = BeautifulSoup(facility_resp.content)
        
        get_first_report_date=facility_soup.find('b',text=re.compile("Date"))
        
        if get_first_report_date:
            facility['date'] = get_first_report_date.next_sibling.strip()
            get_demerits=get_first_report_date.parent.find('b',text=re.compile('Demerits'))
            inspection_demerits=get_demerits.next_sibling.strip()
            facility['score']=100-(DEMERIT_MULTIPLIER*int(inspection_demerits))
        
        time.sleep(SECONDS_THROTTLE)

        print "Facility: %s" % facility
        csv_writer.writerow(facility)


if __name__ == "__main__":
    sys.exit(main())
