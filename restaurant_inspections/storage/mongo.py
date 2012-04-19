import os
import datetime

from pymongo import Connection

STORING_TO_MONGO = False
if 'MONGODB_URI' in os.environ:
    try:
        mongo = Connection(os.environ['MONGODB_URI'])
        db = mongo[os.environ['MONGODB_DATABASE']]
        facilities = db.facilities
        inspections = db.inspections
        violations = db.violations
        STORING_TO_MONGO = True
        print "Storing to mongo"
    except:
        print "Could not connect to mongo"


def save_facility(facility):
    if STORING_TO_MONGO:
        facilities.save(facility, safe=True)


def save_inspection(inspection):
    if STORING_TO_MONGO:
        inspection['date'] = datetime.datetime.combine(inspection['date'],
                                              datetime.time())
        inspections.save(inspection, safe=True)


def save_violation(violation):
    if STORING_TO_MONGO:
        violations.save(violation, safe=True)
