# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.

from setuptools import setup
import monkeypatch_setuptools  # NOQA

version = '0.9.0dev'

long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CREDITS.rst').read(),
    open('CHANGES.rst').read(),
])

install_requires = [
    'Django',
    'Jinja2',
    'Markdown',
    'Werkzeug',
    'ciso8601',
    'configparser',
    'dealer',
    'django-cachalot',
    'django-celery',
    'django-cors-headers',
    'django-debug-toolbar',
    'django-extensions',
    'django-filter',
    'django-json-field',
    'django-logutils',
    'django-redis',
    'django-stored-messages',
    'django-tls',
    'djangorestframework',
    'djangorestframework-filters >= 0.5.0',
    'djangorestframework-gis',
    'drf-nested-routers',
    'gevent',
    'gunicorn',
    'hiredis',  # C implementation
    'python-magic',
    'pandas',
    'pyproj',
    'python-logstash',
    'python-mimeparse',
    'pytz',
    'raven',
    'redis',  # TileStache, raster-server
    'requests',
    'shapely',
    'sitesetup',
    'dogslow',
    'django-watson',
    'openpyxl',
],

tests_require = [
]

setup(name='dd-node',
      version=version,
      description="API for DD node",
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Programming Language :: Python',
                   'Framework :: Django',
                   ],
      keywords=[],
      author='nens',
      author_email='info@nelen-schuurmans.nl',
      url='',
      license='closed source',
      packages=['dd_node'],
      zip_safe=False,
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require={'test': tests_require},
      entry_points={
          'console_scripts': [
          ]},
      )
