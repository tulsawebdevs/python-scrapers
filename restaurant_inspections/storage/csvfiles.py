import csv
import logging
import os

logging.basicConfig(filename='errors.log')
logger = logging.getLogger(__name__)


# HACK: 2.6 doesn't have DictWriter.writeheader() method :(
def writeheader(csv_writer):
    csv_writer.writerow(dict((field, field)
                             for field in csv_writer.fieldnames))


STORING_TO_CSV = False
if 'STORE_TO_CSV' in os.environ:
    facilities_file = open('thd_facilities.csv', 'wb')
    facilities_writer = csv.DictWriter(facilities_file, ['url', '_id', 'type',
                            'name', 'location', 'latitude', 'longitude'])
    writeheader(facilities_writer)

    inspections_file = open('thd_inspections.csv', 'wb')
    inspections_writer = csv.DictWriter(inspections_file, ['facility', 'url',
                            '_id', 'date', 'priority', 'purpose', 'result',
                            'actions'])
    writeheader(inspections_writer)

    violations_file = open('thd_violations.csv', 'wb')
    violations_writer = csv.DictWriter(violations_file, ['_id', 'inspection',
                            'type', 'food_code', 'comments'])
    writeheader(violations_writer)

    STORING_TO_CSV = True
    print "Storing to csv"


def strip_value(string):
    if getattr(string, 'strip', False):
        return string.strip()
    else:
        return string


def ascii_values(dictionary):
    new_dictionary = {}
    for key, value in dictionary.items():
        if type(value) is str:
            # TODO: better handling of non-ascii characters
            for x in value:
                if ord(x) > 128:
                    print "Found non-ascii character %s" % x
            new_dictionary[key] = ''.join([x for x in value if ord(x) < 128])
    return new_dictionary


def get_csv_writer(filename, fields):
    csv_file = open(filename, 'wb')
    csv_writer = csv.DictWriter(csv_file, fields)
    writeheader(csv_writer)
    return csv_writer


def save_facility(csv_writer, facility):
    try:
        csv_writer.writerow(facility)
    except:
        logger.exception("Error writing facility: %s" % facility['_id'])


def save_inspection(inspection):
    if STORING_TO_CSV:
        try:
            inspections_writer.writerow(ascii_values(inspection))
            inspections_file.flush()
        except:
            logger.exception("Error writing inspection: %s"
                             % inspection['_id'])


def save_violation(violation):
    if STORING_TO_CSV:
        try:
            violation = ascii_values(violation)
            violations_writer.writerow(violation)
            violations_file.flush()
        except:
            logger.exception("Error writing violation: %s (food code %s) for "
                             "inspection: %s"
                             % (violation['_id'],
                                violation['food_code'],
                                violation['inspection']))
