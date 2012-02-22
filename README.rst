WSGIAdmin
=========

Web interface for your server, based on Django and Python.
It can handle a Python's applications through uWSGI and PHP
applications throw Apache and mod_fcgid. It's not complete
yet, but we use it in production. We are working hard to make
wsgiadmin to be the best solution for servers.

.. image:: https://github.com/creckx/pcp/raw/master/stuff/screen1.png
   :width: 450 px

TODO
====

* e-mail redirects
* master panel with cool things
* VPS manager
* Remove address from model, connect via JSONRPC with PCP-Invoices
* Remove clients app, merge it with users
* Provision system

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

DEPS
=====

project dependencies:
* see requirements.txt

external dependencies:
* uWSGI
* Python 2.6, 2.7
* PostgreSQL 8.x (9.x not tested) or MySQL


Developers
==========

* Adam Štrauch - cx@initd.cz (e-mail/jabber)
* Jiří Suchan - @yedpodtrzitko
* Pavel Buben

You are welcome to join us, just click on the fork button up there.

--
Adam 'cx' Strauch
cx@initd.cz
