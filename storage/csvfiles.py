import csv
import logging
import os

logging.basicConfig(filename='errors.log')
logger = logging.getLogger(__name__)

STORING_TO_CSV = False
if 'STORE_TO_CSV' in os.environ:
    facilities_file = open('thd_facilities.csv', 'wb')
    facilities_writer = csv.DictWriter(facilities_file, ['url', '_id', 'type',
                            'name', 'location', 'latitude', 'longitude'])
    # HACK: 2.6 doesn't have writeheader() method :(
    facilities_writer.writerow(dict((field,field)
                              for field in facilities_writer.fieldnames))

    inspections_file = open('thd_inspections.csv', 'wb')
    inspections_writer = csv.DictWriter(inspections_file, ['facility', 'url',
                            '_id', 'date', 'priority', 'purpose', 'result',
                            'actions'])
    # HACK: 2.6 doesn't have writeheader() method :(
    inspections_writer.writerow(dict((field, field)
                                for field in inspections_writer.fieldnames))
    STORING_TO_CSV = True
    print "Storing to csv"


def save_facility(facility):
    if STORING_TO_CSV:
        try:
            facilities_writer.writerow(facility)
            facilities_file.flush()
        except:
            logger.exception("Error writing facility: %s" % facility['_id'])


def save_inspection(inspection):
    if STORING_TO_CSV:
        try:
            inspections_writer.writerow(inspection)
            inspections_file.flush()
        except:
            logger.exception("Error writing inspection: %s"
                             % inspection['_id'])
