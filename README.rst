DD-node
=======

Django site that provides a reference implementation for the Digital Delta API spec.

* `Install <INSTALL.rst>`_

Based on Django Rest Framework and PostGIS.


Search
------

Search is based on PostgreSQL's full-text search capabilities via
`django-watson <https://github.com/etianen/django-watson>`_.
To build a search index, follow these steps::

    1. bin/django migrate (once, creates a database table)
    2. bin/django installwatson (once, creates a database trigger)
    3. bin/django buildwatson (periodically, indexes your existing data)

Inserts, updates and deletes of registered assets will automatically update the
search index (except for bulk operations). For reasons of performance, this
is not the case for related objects. These will be handled by scheduling a
:code:`buildwatson` at convenient times.
