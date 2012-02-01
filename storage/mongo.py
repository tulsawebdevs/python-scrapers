import os
import datetime

from pymongo import Connection

STORING_TO_MONGO = False
if 'MONGODB_URI' in os.environ:
    try:
        mongo = Connection(os.environ['MONGODB_URI'])
        db = mongo.heroku_app2532900
        facilities = db.facilities
        inspections = db.inspections
        STORING_TO_MONGO = True
        print "Storing to mongo"
    except:
        print "Could not connect to mongo"

def save_facility(facility):
    if STORING_TO_MONGO:
        facilities.save(facility)

def save_inspection(inspection):
    if STORING_TO_MONGO:
        inspection['date'] = datetime.datetime.combine(inspection['date'],
                                              datetime.time())
        inspections.save(inspection)
