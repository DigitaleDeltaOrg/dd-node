Install
=======

Buildout
--------

**NOTE:** if you use vagrant, first login to your box::

    vagrant ssh
    cd /vagrant
    ln -s buildout/development.cfg buildout.cfg
    python buildout/bootstrap.py
    bin/buildout

If you're installing on a pristine Ubuntu Precise box, running bin/buildout may enter an infinite loop. In this case, comment or delete the following line in buildout/base.cfg and retry::

    zc.buildout = 2.2.3

When updating, you may have to remove \*.pyc files (or you get a "ImportError: No module named magic")::

    find . -name '*.pyc' -exec rm {} \;

Setup database
--------------

Start with an empty database, then generate some tables::

    bin/django syncdb

Start server
------------

Start the server::

    bin/django runserver 0.0.0.0:8000
