import csv
import os


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
        facilities_writer.writerow(facility.values())
        facilities_file.flush()

def save_inspection(inspection):
    if STORING_TO_CSV:
        inspections_writer.writerow(inspection.values())
        inspections_file.flush()
