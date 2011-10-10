# -*- coding: utf-8 -*-.
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
EMAIL_HOST = "localhost"

PAYMENT_WSGI   = {"czk": 60, "usd": 0, "eur": 0}
PAYMENT_PHP    = {"czk": 60, "usd": 0, "eur": 0}
PAYMENT_STATIC = {"czk": 10, "usd": 0, "eur": 0}
PAYMENT_FEE    = {"czk": 200, "usd": 11, "eur": 8}

DEFAULT_MYSQL_COMMAND = 'mysql -uroot'
