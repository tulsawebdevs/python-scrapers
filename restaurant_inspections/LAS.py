import logging
import re
import sys
import time
import json
import requests

from storage.csvfiles import get_csv_writer, get_value

logging.basicConfig(filename="scraping_errors.log")
logger = logging.getLogger(__name__)

URL_ROOT = 'http://www.southernnevadahealthdistrict.org/restaurants/stores/restaurants.php'
SECONDS_THROTTLE = 3
SEARCH_PARAMS = {
'start': 0,
'limit': 500,
}


BRK = "==============================================\n"

def main(argv=None):
    fields = ['url', 'name', 'location', 'city', 'zip', 'date', 'score']
    filename = 'lasvegas.csv'
    csv_writer = get_csv_writer(filename, fields)
    more_to_do=True
    
    
    rest_start=0
    
    while more_to_do:

        SEARCH_PARAMS['start']=rest_start
        search_resp = requests.post(URL_ROOT,data=SEARCH_PARAMS)
        print BRK
        # we have to fix this almost valid JSON response
        json_blob=search_resp.content
        json_blob=json_blob.replace('total','\"total\"')
        json_blob=json_blob.replace('restaurants','\"restaurants\"')
        response_list=json.loads(json_blob)
        response_count=len(response_list['restaurants'])
        
        if response_count==0:
            more_to_do=False
        else:

            for rest in response_list['restaurants']:
                facility={}
                facility['url']='http://www.southernnevadahealthdistrict.org/restaurants/inspections.php'
                facility['name']= rest['restaurant_name']
                facility['location']="%s" % rest['address']
                facility['city']="%s, %s" % (rest['city_name'],rest['state'])
                facility['zip']=rest['zip_code']
                facility['date']=rest['date_current'].split(' ')[0]
                facility['score']=100-int(rest['demerits'])

                print "Facility: %s" % facility
                csv_writer.writerow(facility)
                
 
            rest_start=rest_start+response_count
        
        time.sleep(SECONDS_THROTTLE)


if __name__ == '__main__':
	main()
	
	
# FOR REFERENCE
# {
#     "permit_id": "0009329",
#     "permit_number": "PR0009329",
#     "restaurant_name": "Nobu Restaurant",
#     "address": "4455 Paradise Rd",
#     "latitude": "36.10882900",
#     "longitude": "-115.15241900",
#     "city_name": "Las Vegas",
#     "state": "NV",
#     "zip_code": "89169-6574",
#     "current_grade": "C",
#     "date_current": "2012-10-24 00:00:00",
#     "demerits": "39",
#     "category_name": "Restaurant",
#     "prev_insp": [
#         {
#             "inspection_id": "DA0905180",
#             "permit_id": "PR0009329",
#             "inspection_date": "2011-12-12 00:00:00",
#             "fixed_date": "12/12/2011",
#             "inspection_time": "2011-12-12 18:00:00",
#             "inspection_demerits": "9",
#             "inspection_grade": "A",
#             "violations": "214,215,229,230,233",
#             "permit_status": null,
#             "inspection_type": "Routine Inspection"
#         },
#         {
#             "inspection_id": "DA0405927",
#             "permit_id": "PR0009329",
#             "inspection_date": "2010-03-24 00:00:00",
#             "fixed_date": "3/24/2010",
#             "inspection_time": "2010-03-24 18:40:00",
#             "inspection_demerits": "9",
#             "inspection_grade": "A",
#             "violations": "18,27,31,36,37,114",
#             "permit_status": null,
#             "inspection_type": "Routine Inspection"
#         },
#         {
#             "inspection_id": "DA0405926",
#             "permit_id": "PR0009329",
#             "inspection_date": "2009-03-25 00:00:00",
#             "fixed_date": "3/25/2009",
#             "inspection_time": "2009-03-25 18:00:00",
#             "inspection_demerits": "10",
#             "inspection_grade": "A",
#             "violations": "14,31,37,114",
#             "permit_status": null,
#             "inspection_type": "Routine Inspection"
#         },
#         {
#             "inspection_id": "DA0405925",
#             "permit_id": "PR0009329",
#             "inspection_date": "2008-08-12 00:00:00",
#             "fixed_date": "8/12/2008",
#             "inspection_time": "2008-08-12 17:20:00",
#             "inspection_demerits": "3",
#             "inspection_grade": "A",
#             "violations": "23,31,37",
#             "permit_status": null,
#             "inspection_type": "Routine Inspection"
#         },
#         {
#             "inspection_id": "DA0405924",
#             "permit_id": "PR0009329",
#             "inspection_date": "2007-11-29 00:00:00",
#             "fixed_date": "11/29/2007",
#             "inspection_time": "2007-11-29 18:55:00",
#             "inspection_demerits": "6",
#             "inspection_grade": "A",
#             "violations": "14,22,35",
#             "permit_status": null,
#             "inspection_type": "Routine Inspection"
#         },
#         {
#             "inspection_id": "DA0405923",
#             "permit_id": "PR0009329",
#             "inspection_date": "2007-04-17 00:00:00",
#             "fixed_date": "4/17/2007",
#             "inspection_time": "2007-04-17 17:15:00",
#             "inspection_demerits": "1",
#             "inspection_grade": "A",
#             "violations": "37",
#             "permit_status": null,
#             "inspection_type": "Routine Inspection"
#         },
#         {
#             "inspection_id": "DA0405922",
#             "permit_id": "PR0009329",
#             "inspection_date": "2007-04-06 00:00:00",
#             "fixed_date": "4/6/2007",
#             "inspection_time": "2007-04-06 17:30:00",
#             "inspection_demerits": "23",
#             "inspection_grade": "C",
#             "violations": "4,14,23,27,28,30,35,36,37,112,114",
#             "permit_status": null,
#             "inspection_type": "Routine Inspection"
#         },
#         {
#             "inspection_id": "DA0405921",
#             "permit_id": "PR0009329",
#             "inspection_date": "2006-06-27 00:00:00",
#             "fixed_date": "6/27/2006",
#             "inspection_time": "2006-06-27 18:30:00",
#             "inspection_demerits": "8",
#             "inspection_grade": "A",
#             "violations": "13,23,24,30,31,35",
#             "permit_status": null,
#             "inspection_type": "Routine Inspection"
#         },
#         {
#             "inspection_id": "DA0405920",
#             "permit_id": "PR0009329",
#             "inspection_date": "2005-09-27 00:00:00",
#             "fixed_date": "9/27/2005",
#             "inspection_time": "2005-09-27 19:10:00",
#             "inspection_demerits": "10",
#             "inspection_grade": "A",
#             "violations": "20,22,23,31,32,37,114",
#             "permit_status": null,
#             "inspection_type": "Routine Inspection"
#         },
#         {
#             "inspection_id": "DA0405919",
#             "permit_id": "PR0009329",
#             "inspection_date": "2004-08-20 00:00:00",
#             "fixed_date": "8/20/2004",
#             "inspection_time": "2004-08-20 15:30:00",
#             "inspection_demerits": "5",
#             "inspection_grade": "A",
#             "violations": "37,111",
#             "permit_status": null,
#             "inspection_type": "Routine Inspection"
#         },
#         {
#             "inspection_id": "DA0405918",
#             "permit_id": "PR0009329",
#             "inspection_date": "2003-12-17 00:00:00",
#             "fixed_date": "12/17/2003",
#             "inspection_time": "2003-12-17 17:00:00",
#             "inspection_demerits": "5",
#             "inspection_grade": "A",
#             "violations": "13,27,35",
#             "permit_status": null,
#             "inspection_type": "Routine Inspection"
#         },
#         {
#             "inspection_id": "DA0405917",
#             "permit_id": "PR0009329",
#             "inspection_date": "2002-09-26 00:00:00",
#             "fixed_date": "9/26/2002",
#             "inspection_time": "2002-09-26 15:45:00",
#             "inspection_demerits": "10",
#             "inspection_grade": "A",
#             "violations": "14,18,24,111",
#             "permit_status": null,
#             "inspection_type": "Routine Inspection"
#         },
#         {
#             "inspection_id": "DA0405916",
#             "permit_id": "PR0009329",
#             "inspection_date": "2001-09-20 00:00:00",
#             "fixed_date": "9/20/2001",
#             "inspection_time": "2001-09-20 15:35:00",
#             "inspection_demerits": "6",
#             "inspection_grade": "A",
#             "violations": "23,36,112",
#             "permit_status": null,
#             "inspection_type": "Routine Inspection"
#         },
#         {
#             "inspection_id": "DA0405915",
#             "permit_id": "PR0009329",
#             "inspection_date": "2001-06-06 00:00:00",
#             "fixed_date": "6/6/2001",
#             "inspection_time": "2001-06-06 14:55:00",
#             "inspection_demerits": "2",
#             "inspection_grade": "A",
#             "violations": "24,27",
#             "permit_status": null,
#             "inspection_type": "Routine Inspection"
#         },
#         {
#             "inspection_id": "DA0405913",
#             "permit_id": "PR0009329",
#             "inspection_date": "2001-05-15 00:00:00",
#             "fixed_date": "5/15/2001",
#             "inspection_time": "2001-05-15 15:05:00",
#             "inspection_demerits": "20",
#             "inspection_grade": "B",
#             "violations": "22,27,64,111,112,113",
#             "permit_status": null,
#             "inspection_type": "Routine Inspection"
#         },
#         {
#             "inspection_id": "DA0405912",
#             "permit_id": "PR0009329",
#             "inspection_date": "2000-10-05 00:00:00",
#             "fixed_date": "10/5/2000",
#             "inspection_time": "2000-10-05 13:10:00",
#             "inspection_demerits": "8",
#             "inspection_grade": "A",
#             "violations": "10,14,18",
#             "permit_status": null,
#             "inspection_type": "Routine Inspection"
#         },
#         {
#             "inspection_id": "DA0405911",
#             "permit_id": "PR0009329",
#             "inspection_date": "2000-03-31 00:00:00",
#             "fixed_date": "3/31/2000",
#             "inspection_time": "2000-03-31 13:50:00",
#             "inspection_demerits": "7",
#             "inspection_grade": "A",
#             "violations": "13,14",
#             "permit_status": null,
#             "inspection_type": "Routine Inspection"
#         }
#     ],
#     "violations": "201,203,206,209,211,214,218,219,223,225,227,229,234",
#     "insp_type": "Routine Inspection"
# }
