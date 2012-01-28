import os
import datetime

from pymongo import Connection

STORING_TO_MONGO = False
if 'MONGODB_URI' in os.environ:
    try:
        mongo = Connection(os.environ['MONGODB_URI'])
        thd_db = mongo.thd
        facilities = thd_db.facilities
        inspections = thd_db.inspections
        STORING_TO_MONGO = True
    except:
        print "Could not connect to mongo"

def save_facility(facility):
    if STORING_TO_MONGO:
        facilities.insert(facility)

def save_inspection(inspection):
    if STORING_TO_MONGO:
        inspection['date'] = datetime.datetime.combine(inspection['date'],
                                              datetime.time())
        inspections.insert(inspection)
