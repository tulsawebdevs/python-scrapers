==============================================
Tulsa Health Department Restaurant Inspections
==============================================

Run
===

Activate virtualenv::

    source bin/activate

Adjust settings as needed::

    vim thd_food_inspections/thd_food_inspections.py

    PAGE_SIZE = 20
    SECONDS_THROTTLE = 10

    SEARCH_PARAMS = {
                   'startrow': 1,
                   'maxrows': PAGE_SIZE,
                   ...
                   'startDate': '01-07-2011',
                   'endDate': '01-07-2012',
                   ...
                   }
    
Run scraper::

    python thd_food_inspections/thd_food_inspections.py

Heroku
------

#. Sign up for Heroku_ 
#. install gem::

    gem install heroku

#. login::

    heroku login

#. create app::

    heroku create --stack cedar

#. push to heroku::

    git push heroku master

#. run::

    heroku run python thd_food_inspections/thd_food_inspections.py

Note: Heroku cannot store files; using Cloudant and/or mongolab is suggested.
(See below)

.. _Heroku: http://heroku.com

Store
=====

You can store the data to a number of destinations by setting environment
variables.

CSV Files
---------

#. Set environment variable::

    export STORE_TO_CSV=True

Will write the data to 3 files: thd_facilities.csv, thd_inspections.csv, thd_violations.csv

CouchDB
-------

#. Install CouchDB_, or use Cloudant_.
#. Create tables::

    thd_facilities
    thd_inspections
    thd_violations

#. Set environment variable::

    export COUCHDB_URL=https://user:pass@localhost

.. _CouchDB: http://wiki.apache.org/couchdb/Installation
.. _Cloudant: https://cloudant.com/

MongoDB
-------

#. Install MongoDB_, or use MongoHQ_ (run by a Tulsa expatriate!).
#. Set environment variable::

    export MONGODB_URI=mongodb://user:pass@localhost:29817/database_name
    export MONGODB_DATABASE=database_name

.. _MongoDB: http://www.mongodb.org/
.. _MongoHQ: https://mongohq.com/
