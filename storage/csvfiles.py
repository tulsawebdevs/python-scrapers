import csv
import logging
import os

logging.basicConfig(filename='errors.log')
logger = logging.getLogger(__name__)

STORING_TO_CSV = False
if 'STORE_TO_CSV' in os.environ:
    facilities_file = open('thd_facilities.csv', 'wb')
    facilities_writer = csv.writer(facilities_file)
    inspections_file = open('thd_inspections.csv', 'wb')
    inspections_writer = csv.writer(inspections_file)
    STORING_TO_CSV = True
    print "Storing to csv"


def save_facility(facility):
    if STORING_TO_CSV:
        try:
            facilities_writer.writerow(facility.values())
            facilities_file.flush()
        except:
            logger.exception("Error writing facility: %s" % facility['_id'])


def save_inspection(inspection):
    if STORING_TO_CSV:
        try:
            inspections_writer.writerow(inspection.values())
            inspections_file.flush()
        except:
            logger.exception("Error writing inspection: %s"
                             % inspection['_id'])
