import csvfiles
import couch
import mongo


def save_facility(facility):
    couch.save_facility(facility)
    mongo.save_facility(facility)
    csvfiles.save_facility(facility)


def save_inspection(inspection):
    couch.save_inspection(inspection)
    mongo.save_inspection(inspection)
    csvfiles.save_inspection(inspection)


def save_violation(violation):
    couch.save_violation(violation)
    mongo.save_violation(violation)
    csvfiles.save_violation(violation)
