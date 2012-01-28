import os
from urllib import urlencode

import requests

class QrimpParams(object):
    params = {'t': '',
              'o': '5',
              '_RETURNRESULT': 'true',
              'NOHEADER': 'true',
              'NOFOOTER': 'true'}

STORING_TO_QRIMP = False
if 'QRIMP_URL' in os.environ:
    QRIMP_URL = os.environ['QRIMP_URL']
    resp = requests.get(QRIMP_URL)
    if resp.status_code == 200:
        STORING_TO_QRIMP = True
        print "Storing to qrimp"
    else:
        print "Could not connect to qrimp"

def save_facility(facility, facility_id=None):
    if STORING_TO_QRIMP:
        try:
            qrimpParams = QrimpParams()
            qrimpParams.params.update({'t': 'facilities'})
            if facility_id:
                qrimpParams.params.update({'o':'3', 'id': facility_id})
            facilities_url = QRIMP_URL + urlencode(qrimpParams.params)
            full_url = facilities_url + '&' + urlencode(facility)
            resp = requests.get(full_url)
            if resp.status_code != 200:
                print "ERROR: %s %s" % (resp.status_code, resp.content)
            qrimpParams.params.update({'o':'5'})
            facility_id = resp.content
            return facility_id
        except:
            pass

def save_inspection(inspection, facility_name, facility_id):
    if STORING_TO_QRIMP:
        try:
            qrimpParams = QrimpParams()
            qrimpParams.params.update({'t': 'inspections'})
            inspections_url = QRIMP_URL + urlencode(qrimpParams.params)
            inspection['facility'] = facility_id
            inspection['name'] = facility_name
            inspection['date'] = inspection['date'].strftime('%m/%d/%Y')
            full_url = inspections_url + '&' + urlencode(inspection)
            resp = requests.get(full_url)
            if resp.status_code != 200:
                print "ERROR: %s %s" % (resp.status_code, resp.content)
        except:
            pass
