=====
Setup
=====

Requirements
============
* git
* Python 2.6

Getting the Code
==================

Grab the source from Github using::

    git clone git://github.com/tulsawebdevs/okdata.git

Installing the Packages
=======================

Create a virtualenv and install required libraries::

    cd okdata/python
    python ./make_bootstrap.py
    python ./bootstrap.py
    source bin/activate
    pip install -r requirements.txt
