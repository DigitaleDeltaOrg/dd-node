# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.

import os
import socket

"""Django 1.9 monkey patch for django-json-field.

See:

https://github.com/derek-schaefer/django-json-field/issues/42
https://github.com/derek-schaefer/django-json-field/pull/41

The django-json-field project is considered abandoned by its author, so we
should look out for alternatives.

"""
try:
    import django.forms.util  # NOQA
except ImportError:
    from django import forms
    forms.util = forms.utils

try:
    HOSTNAME = socket.gethostname()
except:
    HOSTNAME = 'localhost'

DEBUG = False

LOGIN_REDIRECT_URL = '/'

ALLOWED_HOSTS = []

PROTOCOL = 'https'

# make sure django treats requests as secure when forwarded from proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# SETTINGS_DIR allows media paths and so to be relative to this settings file
# instead of hardcoded to c:\only\on\my\computer.
SETTINGS_DIR = os.path.dirname(os.path.realpath(__file__))

# BUILDOUT_DIR is for access to the "surrounding" buildout, for instance for
# BUILDOUT_DIR/var/static files to give django-staticfiles a proper place
# to place all collected static files.
BUILDOUT_DIR = os.path.abspath(os.path.join(SETTINGS_DIR, '../..'))

ADMINS = ()
MANAGERS = ADMINS

FALLBACK_DOMAIN = 'https://demo.lizard.net/'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name although not all
# choices may be available on all operating systems.  If running in a Windows
# environment this must be set to the same as your system time zone.
TIME_ZONE = 'Europe/Amsterdam'
USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'nl-NL'
# For runtime language switching.  Note: they're shown in reverse order in
# the interface!
LANGUAGES = (
    ('en', 'English'),
    ('nl', 'Nederlands'),
)
# If you set this to False, Django will make some optimizations so as not to
# load the internationalization machinery.
USE_I18N = True

DATABASES = {}

# https://docs.djangoproject.com/en/1.10/ref/templates/upgrading/
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # insert your TEMPLATE_DIRS here
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# SSO
SSO_ENABLED = True
SSO_USE_V2_LOGIN = True
SSO_SERVER_API_START_URL = 'https://sso.lizard.net/api2/'
# A key identifying this client. Can be published.
SSO_KEY = 'random_generated_key_to_identify_the_portal'
# A *secret* shared between client and server. Used to sign the messages
# exchanged between them. Note: as long as the name of this setting
# contains "SECRET", it is hidden in the Django debug output.
SSO_SECRET = 'random_generated_secret_key_to_sign_exchanged_messages'
# Timeout for cached credentials with the SSOBackend Authentication Backend.
SSO_CREDENTIAL_CACHE_TIMEOUT_SECONDS = 60

# Absolute path to the directory that holds user-uploaded media.
MEDIA_ROOT = os.path.join(BUILDOUT_DIR, 'var', 'media')
# Absolute path to the directory where django-staticfiles'
# "bin/django build_static" places all collected static files from all
# applications' /media directory.
STATIC_ROOT = os.path.join(BUILDOUT_DIR, 'var', 'static')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
MEDIA_URL = '/media/'
# URL for the per-application /media static files collected by
# django-staticfiles.  Use it in templates like
# "{{ MEDIA_URL }}mypackage/my.css".
STATIC_URL = '/static/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'u6wj#ixa%37zp@p8ombitg!^ia_r5-%=_jsa!c&b%@=w&9z=a^'

ROOT_URLCONF = 'dd_node.urls'

MIDDLEWARE_CLASSES = (
    # BYRMAN 2013-11-08 : moved tls.TLSRequestMiddleWare up
    # the list to fix 'no object bound to request' errors
    # in combination with round robin access to reverse
    # proxy.
    'tls.TLSRequestMiddleware',
    # According to the Dogslow documentation: "For best results,
    # make it one of the first middlewares that is run".
    'dogslow.WatchdogMiddleware',
    'django_logutils.middleware.LoggingMiddleware',
    # Middleware that may change the response must appear before
    # CommonMiddleware (during the response phase, middleware
    # is applied in reverse order, from the bottom up).
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'dealer.contrib.django.Middleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

INSTALLED_APPS = (
    'django_extensions',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.gis',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'dd_node',  # Before rest_framework
    'rest_framework',
    'rest_framework_gis',
    'stored_messages',
    'corsheaders',
    'gunicorn',
    'djcelery',  # Celery
    'kombu.transport.django',  # Celery
    'cachalot',
    'watson',
)

CRISPY_TEMPLATE_PACK = 'bootstrap3'

# Needed for LoggingMiddleware, the second entry is for debug toolbar
INTERNAL_IPS = ('127.0.0.1', '10.0.3.1')

# Used by the @internal_ips_only decorator. These are IP prefixes.
INTERNAL_API_IPS = ('127.0.0.', '10.100.')

# Message framework + django-stored-messages
MESSAGE_STORAGE = 'stored_messages.storage.PersistentStorage'

# CORS
CORS_ORIGIN_WHITELIST = ()

# Timeseries data storage paths
EVENT_LOG_DIR = "var/timeseries/log"
EVENT_STORAGE_DIR = "var/timeseries/storage"
EVENT_LOG_HDFS_DIR = "var/timeseries/hdfs"
EVENT_FILE_DIR = "var/timeseries/files"

# Django rest framework
REST_FRAMEWORK = {
    'FORM_METHOD_OVERRIDE': None,
    'FORM_CONTENT_OVERRIDE': None,
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'dd_node.parsers.SimpleFileUploadParser',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework_filters.backends.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
        'rest_framework_gis.filters.InBBoxFilter',
        'rest_framework_gis.filters.DistanceToPointFilter'
    ),
    'DEFAULT_PAGINATION_CLASS': (
        'dd_node.pagination.LimitOffsetAndPageNumberPagination'
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon-burst': '25/second',
        'anon-sustained': '10000/day',
        'user-burst': '50/second',
    },
    'DEFAULT_VERSIONING_CLASS':
    'rest_framework.versioning.NamespaceVersioning',
}

CACHES = {
    'default': dict(
        BACKEND='django_redis.cache.RedisCache',
        LOCATION='redis://127.0.0.1:6379/1',
        OPTIONS={
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'SOCKET_CONNECT_TIMEOUT': 5,  # in seconds
            'SOCKET_TIMEOUT': 5,  # in seconds
        },
    ),
}

CACHALOT_UNCACHABLE_TABLES = frozenset([
    'django_migrations',
    'django_session',
])


# TileStache
TILESTACHE_CACHE = {"class": "dd_node.tilestache.Redis:CacheAuth"}

# Dealer is used to put git tag and revision info on the request.
DEALER_TYPE = 'git'

# Directory where uploaded files are stored.
UPLOAD_DIR = os.path.join(BUILDOUT_DIR, 'var', 'upload')

# Persistent connections (since Django 1.6)
CONN_MAX_AGE = 300

# client port to redirect to when in development
CLIENT_PORT = 80

POSTGIS_VERSION = (2, 1, 0)

# use ST_Estimated_Extent in Mapnik
MAPNIK_ESTIMATE_EXTENT = False

# Dogslow logs slow requests to Sentry.
DOGSLOW_LOGGER = 'dogslow'
DOGSLOW_LOG_TO_FILE = False
DOGSLOW_TIMER = 2
DOGSLOW_LOG_LEVEL = 'WARNING'
DOGSLOW_LOG_TO_SENTRY = True

# Mounted directory where scenario data is imported from. Probably a symlink
# to elsewhere.
SCENARIO_IMPORT_DIR = os.path.join(BUILDOUT_DIR, 'var', 'scenarios_import')
# Directory where scenario data will be stored. Probably a symlink to
# elsewhere.
SCENARIO_DATA_DIR = os.path.join(BUILDOUT_DIR, 'var', 'scenarios')

# URL to raster wms server.
RASTER_WMS_URL = 'https://raster.staging.lizard.net/wms'

# URL to LWM (Landelijk Meetnet Water) data.
LMW_URL = 'http://www.rijkswaterstaat.nl/rws/opendata/meetdata/meetdata.zip'
# LMW (Landelijk Meetnet Water) downloads are stored here.
LMW_DIR = os.path.join(BUILDOUT_DIR, 'var/data/lmw')

# For fetching pi xml. See: https://github.com/nens/fews-pi-service-client.
FEWS_PI_SERVICE_CLIENT = (
    '/opt/FewsPiServiceClient/dist/FewsPiServiceClient.jar')

EMAIL_HOST = '100-mail-c1.external-nens.local'
EMAIL_PORT = 25
EMAIL_FROM = 'noreply@lizard.net'

COMPENSATION = {
    'csv_path':
    '/path/to/compensation/waterheightcompensation.csv',
}

ALARM = {'timelag': '999999999'}

# Raster Server
RASTER_SERVER_REDIS_HOST = 'localhost'
RASTER_SERVER_REDIS_DB = 3
