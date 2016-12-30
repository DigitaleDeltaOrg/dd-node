# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.

from __future__ import print_function

import sys

from .base import *  # NOQA
from .settingshelper import setup_logging

# user name extraction for HBASE
import getpass
username = getpass.getuser()

LOGGING = setup_logging(
    BUILDOUT_DIR,
    console_level='DEBUG',
    file_level='DEBUG',
    sql=False)

DEBUG = True

DEV_TEMPLATE = True

ALLOWED_HOSTS = ['localhost']

PROTOCOL = 'http'

# ENGINE: 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
# In case of geodatabase, prepend with:
# django.contrib.gis.db.backends.(postgis)
DATABASES['default'] = {
    # If you want to use another database, consider putting the database
    # settings in localsettings.py. Otherwise, if you change the settings in
    # the current file and commit them to the repository, other developers will
    # also use these settings whether they have that database or not.
    # One of those other developers is Jenkins, our continuous integration
    # solution. Jenkins can only run the tests of the current application when
    # the specified database exists. When the tests cannot run, Jenkins sees
    # that as an error.
    'NAME': 'dd_node',
    'ENGINE': 'django.contrib.gis.db.backends.postgis',
    'USER': 'vagrant',
    'PASSWORD': 'vagrant',
    'HOST': '127.0.0.1',  # empty string for localhost.
    'PORT': '',  # empty string for default.
}

# CORS
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = ('localhost:9000',)
CORS_ALLOW_CREDENTIALS = True

# Celery
BROKER_URL = 'django://'

# If set to False, disables SQL caching, but keeps invalidating to avoid stale
# cache.
CACHALOT_ENABLED = True

# For development, persistent connections are ignored
CONN_MAX_AGE = 0

CLIENT_PORT = 9000

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

try:
    from localsettings import *  # NOQA
    print('Using localsettings\n', file=sys.stderr)
except ImportError:
    print('Did not find localsettings.py\n', file=sys.stderr)
