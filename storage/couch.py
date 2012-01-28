import os
import socket

import couchdb
from couchdb.mapping import Document, TextField, DateField, FloatField

STORING_TO_COUCHDB = False
if 'COUCHDB_URL' in os.environ:
    COUCHDB_URL = os.environ['COUCHDB_URL']
    try:
        couch = couchdb.Server(COUCHDB_URL)
        facility_db = couch['thd_facilities']
        inspection_db = couch['thd_inspections']
        STORING_TO_COUCHDB = True
    except socket.error:
        print "Could not connect to couchdb database"

class Facility(Document):
    _id = TextField()
    name = TextField()
    location = TextField()
    latitude = FloatField()
    longitude = FloatField()
    href = TextField()

class Inspection(Document):
    _id = TextField()
    facility = TextField()
    date = DateField()
    type = TextField()
    priority = TextField()
    purpose = TextField()
    result = TextField()
    actions = TextField()

def save_facility(facility):
    if STORING_TO_COUCHDB:
        facility_doc = Facility(**facility)
        facility_db.update([facility_doc])

def save_inspection(inspection):
    if STORING_TO_COUCHDB:
        inspection_doc = Inspection(**inspection)
        inspection_db.update([inspection_doc])
