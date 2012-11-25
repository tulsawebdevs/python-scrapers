import logging
import re
import sys
import time
import re
import mechanize

from bs4 import BeautifulSoup
import requests

from storage.csvfiles import get_csv_writer, get_value

logging.basicConfig(filename="scraping_errors.log")
logger = logging.getLogger(__name__)

URL_ROOT = 'http://inspections.eatsafe.la.gov'
# http://inspections.eatsafe.la.gov/Results.aspx?pageIndex=190&pageSize=150
SECONDS_THROTTLE = 3


BRK = "==============================================\n"

def main(argv=None):
    fields = ['url', 'name', 'location', 'city', 'zip', 'date', 'score']
    filename = 'whoodat.csv'
    csv_writer = get_csv_writer(filename, fields)
    
    page_number=0
    more_to_do=True

#   Have to use mechanize to get past the pain in the ASPX form handling
    br = mechanize.Browser()
    br.user_agent_alias = 'Linux Firefox'

    while more_to_do:

        print BRK
        # SEARCH_PARAMS['pageIndex']=page_number
        search_url = "%s%s%i%s" % (URL_ROOT, '/Results.aspx?pageIndex=',page_number,'&pageSize=150')
        search_resp = br.open(search_url)
        content=search_resp.read()
        soup=BeautifulSoup(content)

        if soup.find('div',text=re.compile('No records to display')):
            more_to_do=False
        else:
            facilities=_scrape_content(content, csv_writer)
            time.sleep(SECONDS_THROTTLE)
            page_number=page_number+1

    print "============= DONE ==============="


def _scrape_content(content, csv_writer):

    soup=BeautifulSoup(content)
    result_table=soup.find('table',id=re.compile("MainContent_ResultGrid_ctl00"))
    
    for each_row in result_table.find_all('tr',id=re.compile('MainContent_ResultGrid')):
        facility={}
        facility['city'] = 'New Orleans'
        facility_link=each_row.find('a')
        facility['url']="%s/%s" % (URL_ROOT, facility_link['href'])
        facility['name']=facility_link['title']
        street_td=facility_link.parent.next_sibling
        town_td=street_td.next_sibling
        zip_td=town_td.next_sibling.next_sibling        
        facility['location']="%s %s" % (street_td.get_text(),town_td.get_text())
        facility['zip']=zip_td.get_text()
        
        facility_resp = requests.get(facility['url'])
        time.sleep(SECONDS_THROTTLE)
        facility_soup = BeautifulSoup(facility_resp.content)
        
        print BRK
        last_inspection=facility_soup.find('tr',id=re.compile("MainContent_InspectionGrid_ctl00__0"))
        
        if last_inspection:
            inspection_pdf=last_inspection.find('td')
            inspection_date=inspection_pdf.next_sibling
            facility['date']=inspection_date.get_text()
            critical=inspection_date.next_sibling.next_sibling
            critical_corrected=critical.next_sibling
            non_critical=critical_corrected.next_sibling
            non_critical_corrected=non_critical.next_sibling
          
            score=100
            score=score-int(critical.get_text())*6
            score=score-int(critical_corrected.get_text())*3
            score=score-int(non_critical.get_text())*3
            score=score-int(non_critical_corrected.get_text())*2
            facility['score']=score

        print "Facility: %s" % facility
        csv_writer.writerow(facility)

if __name__ == "__main__":
    sys.exit(main())
