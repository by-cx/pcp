WSGIAdmin
=========

Web interface for your server, based on Django and Python.
It can handle a Python's applications through uWSGI and PHP
applications throw Apache and mod_fcgid. It's not complete
yet, but we use it in production. We are working hard to make
wsgiadmin to be the best solution for servers.

.. image:: https://github.com/creckx/pcp/raw/master/stuff/screen1.png
   :width: 450 px

TODO for v0.3
=============

* New design
* Stable nginx support
* Configuration to database (constance)
* Translating in-code texts into english
* Clean, clean, clean
* Fix, fix, fix

TODO for v0.4
=============

* rework invoice system
* fix some bugs
* e-mail redirects
* master panel with cool things
* brand new and external invoice system (PCP-Invoices) - https://github.com/creckx/PCP-Invoices

Main features
=============

* Great Python support with virtualenv (Django, CherryPy and much more)
* Less great PHP support - forced evil
* Nice static sites support
* PostgreSQL, MySQL support
* Bind support
* Email via courier and postfix
* FTP via pure-ftpd
* Simple invoice system
* IPv6 support

DEPTS
=====


* uWSGI
* Python 2.6, 2.7
* PostgreSQL 8.x (9.x not tested)


* South
* psycopg2
* django >= 1.3
* django-uniform
* django-debug-toolbar
* anyjson
* django-constance
* django-picklefield


Developers
==========

* Adam Štrauch - cx@initd.cz (e-mail/jabber)
* Jiří Suchan
* Pavel Buben

You are welcome to join us, just click on the fork button up there.

--
Adam 'cx' Strauch
cx@initd.cz
