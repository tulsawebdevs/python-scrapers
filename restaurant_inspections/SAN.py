import logging
import re
import sys
import time
import mechanize
# from mechanize
 # import ParseResponse, urlopen, urljoin
# import urllib



from bs4 import BeautifulSoup
import requests

from storage.csvfiles import get_csv_writer, get_value

logging.basicConfig(filename="scraping_errors.log")
logger = logging.getLogger(__name__)

URL_ROOT = 'http://www2.sdcounty.ca.gov/ffis'
SECONDS_THROTTLE = 3


BRK = "==============================================\n"
SEARCH_PARAMS = {'lbCity':'',
}

def main(argv=None):
    fields = ['url', 'name', 'location', 'city', 'zip', 'date', 'score']
    filename = 'sandiego.csv'
    csv_writer = get_csv_writer(filename, fields)

#   Have to use mechanize to get past ASPX form handling
    br = mechanize.Browser()
    br.user_agent_alias = 'Linux Firefox' 
    start_search_url=(URL_ROOT+'/default.aspx')
    start_search=br.open(start_search_url)

    soup=BeautifulSoup(start_search.read())    
    city_list=soup.find('select',id='lbCity').find_all('option')
    city_list.pop(0) # get rid of 'Select a City'

    for city in city_list:
        print BRK
        br.select_form(name='Form1')
        br.form.set_all_readonly(False) # allow changing the .value of all controls
        br["__EVENTTARGET"] = 'lbCity'        
        br['lbCity']=[city.get_text()]
        city_results=br.submit()

        br.select_form(name='Form1')
        try:
            more_pages = br.form.find_control("btnNext")
        except:
            more_pages=False
        
        if more_pages:
            br.form.set_all_readonly(False) # allow changing the .value of all controls
            br["__EVENTTARGET"] = 'Linkbutton3'
            city_results=br.submit()
                

        facilities=_scrape_content(city_results, csv_writer)
        
        time.sleep(SECONDS_THROTTLE)
        br.open(start_search_url)
    return




def _scrape_content(content, csv_writer):

    soup=BeautifulSoup(content)

    result_table=soup.find('table',id='dgSearchResults')
    
    for each_row in result_table.find_all('tr'):

        facility_link=each_row.find('td').find('a')

        if facility_link:
            facility={}
            facility['city'] = 'San Diego'
            facility['url']="%s/%s" % (URL_ROOT, facility_link['href'])
            facility['name']=facility_link.get_text()
            street_td=each_row.next_sibling.find('td')
            facility['location']=street_td.get_text()

            # Need a better regex that doesn't capture the -0000
            zip_code = re.search('\d{5}?(-\d{0,4})?$', facility['location'])
            
            if zip_code:
                # print zip_code.group(0)
                facility['zip']=zip_code.group(0)
                
            facility_resp = requests.get(facility['url'])
            facility_soup = BeautifulSoup(facility_resp.content)
            facility['date']=facility_soup.find('span',id='lblInspectionDate').get_text()
                
            insp_list=facility_soup.find(id='dgInspections').find_all('tr')
        
            num_insp=len(insp_list)
            
            insp_row=1
            while insp_row<=num_insp:
                try:
                    facility['score']=insp_list[insp_row].contents[3].get_text()
                except:
                    facility['score']=''
                
                insp_row+=1
                
                if facility['score']!='' and facility['score']!='Directed':
                    
                    break
                
                                
            print "Facility: %s" % facility
            csv_writer.writerow(facility)
            time.sleep(SECONDS_THROTTLE)

if __name__ == "__main__":
    sys.exit(main())
