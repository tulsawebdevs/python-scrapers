import json
import os
import string
import urlparse

import requests

STORING_TO_WYMI = False
if 'WYMI_API_KEY' in os.environ:
    WYMI_API_KEY = os.environ['WYMI_API_KEY']
    WYMI_API_HOST = os.environ['WYMI_API_HOST']
    WYMI_API_ROOT = os.environ['WYMI_API_ROOT']
    WYMI_USERNAME = os.environ['WYMI_USERNAME']
    if WYMI_API_KEY and WYMI_API_HOST and WYMI_API_ROOT and WYMI_USERNAME:
        STORING_TO_WYMI = True
        print "Storing to wymi"
    else:
        print ("You must set WYMI_USERNAME, WYMI_API_KEY, WYMI_API_HOST, and "
              "WYMI_API_ROOT environment variables to store to WYMI.")


def save_facility(facility):
    if STORING_TO_WYMI:
        req_data = {
            'name': facility['name'],
            'address': facility['location'],
            'city': 'Tulsa',
            'state': 'OK',
            'type': facility['type'],
            'zip_code': ''
        }
        facility_token = ''
        # TODO refactor into build_wymi_url
        if id in facility:
            facility_token = '%s/' % facility['id']
        wymi_url = "http://%s%s/facility/%s?username=%s&api_key=%s" % (
            WYMI_API_HOST, WYMI_API_ROOT, facility_token, WYMI_USERNAME,
            WYMI_API_KEY)
        req_content = json.dumps(req_data)
        req_headers = {"content-type": "application/json"}
        if id in facility:
            import pdb; pdb.set_trace()
            requests.put(wymi_url, req_content, headers=req_headers)
            return facility['id']
        else:
            resp = requests.post(wymi_url, req_content, headers=req_headers)
            facility_id = parse_id_from_location(resp.headers['location'])
            return facility_id


def save_inspection(inspection):
    if STORING_TO_WYMI:
        req_data = {
            'facility': "%s/facility/%s/" % (WYMI_API_ROOT,
                                             inspection['facility_id']),
            'date': inspection['date'].strftime('%Y-%m-%d'),
            'score': '-1',
            'type': inspection['purpose']
        }
        # TODO refactor into build_wymi_url
        inspection_token = ''
        if id in inspection:
            inspection_token = '%s/' % inspection['id']
        wymi_url = "http://%s%s/inspection/%s?username=%s&api_key=%s" % (
            WYMI_API_HOST, WYMI_API_ROOT, inspection_token, WYMI_USERNAME,
            WYMI_API_KEY)
        req_content = json.dumps(req_data)
        req_headers = {"content-type": "application/json"}
        if id in inspection:
            import pdb; pdb.set_trace()
            requests.put(wymi_url, req_content, headers=req_headers)
            return inspection['id']
        else:
            resp = requests.post(wymi_url, req_content, headers=req_headers)
            inspection_id = parse_id_from_location(resp.headers['location'])
            return inspection_id


def save_violation(violation):
    if STORING_TO_WYMI:
        pass


def parse_id_from_location(location):
    parts = urlparse.urlparse(location)
    id = string.split(string.strip(parts.path, '/'), '/')[-1]
    return id

