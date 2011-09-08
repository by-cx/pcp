# -*- coding: utf-8 -*-.

#Local settings

DEBUG=True

ADMINS = (
	('Adam Strauch', 'cx@initd.cz'),
)

DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.postgresql_psycopg2',
			'NAME': 'rosti'
		}
}

EMAIL_FROM = "info@rosti.cz"
EMAIL_HOST = "tresnovec.net"

NODE_KEY = "qpS7GkX3tWTRe+EWzLTACofEYRQf4dPROPGWb3lTL"

WIKI_URL = "http://wiki.rosti.cz"
CONTRACT_URL = "http://rosti.cz/text/podminky"
SERVER_NAME = "Roští.cz"

IPv6 = True

DEFAULT_WEB_MACHINE = "Pandora"
DEFAULT_MAIL_MACHINE = "Pandora"
DEFAULT_MYSQL_MACHINE = "Pandora"
DEFAULT_PGSQL_MACHINE = "Pandora"

PAYMENT_WSGI   = {"czk": 60, "usd": 0, "eur": 0}
PAYMENT_PHP    = {"czk": 60, "usd": 0, "eur": 0}
PAYMENT_STATIC = {"czk": 10, "usd": 0, "eur": 0}
PAYMENT_FEE    = {"czk": 200, "usd": 11, "eur": 8}
