======================
Restaurant Inspections
======================

Run
===

Activate virtualenv::

    source bin/activate

Adjust settings as needed::

    vim restaurant_inspections/tulsa.py

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

Note: startDate and endDate apparently have no affect for Tulsa; all records
come back anyway
    
Run scraper::

    python restaurant_inspections/tulsa.py

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

    heroku run python restaurant_inspections/tulsa.py

Note: Heroku cannot store files; using Cloudant and/or mongohq is suggested.
(See below)

.. _Heroku: http://heroku.com

Store
=====

The best way to store the data is to use the default CSV file.
