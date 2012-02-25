===
Run
===

Activate virtualenv::

    source bin/activate

Run scraper::

    python thd_food_inspections/thd_food_inspections.py

=====
Store
=====

You can store the data to a number of destinations by setting environment
variables.

CSV Files
=========

Set environment variable::

    export STORE_TO_CSV=True

Will write the data to 3 files: ``thd_facilities.csv``, ``thd_inspections.csv``
, and ``thd_violations.csv``
