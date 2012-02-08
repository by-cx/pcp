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

DEFAULT_MYSQL_COMMAND = 'mysql -uroot'
