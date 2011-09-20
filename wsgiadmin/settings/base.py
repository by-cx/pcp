# -*- coding: utf-8 -*-.
# Django settings for manager project.

_ = lambda x: x

import os, sys

sys.path.append("/home/cx/co/pcp/")

from os.path import join, abspath, pardir, dirname

ROOT = abspath(join(dirname(__file__), pardir))

DEBUG = False
TEMPLATE_DEBUG = DEBUG
DEBUG_TOOLBAR = DEBUG
ENABLE_DEBUG_URLS = DEBUG

APPEND_SLASH = True

ADMINS = ()

MANAGERS = ADMINS

INTERNAL_IPS = ('127.0.0.1', '89.111.104.66')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'rosti'
    }
}

## Faktury

BANK = "mBank"
BANK_ACCOUNT = "670100-2206514444/6210"
MY_ADDRESS_ID = 1
STAMP_SIGN = join(ROOT, "m", "razitko.png")
STAMP_NOSIGN = join(ROOT, "m", "razitko-nosign.png")

CURRENCY = (("czk", "CZK"), ("eur", "EUR"), ("usd", "USD"),)

##########

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Prague'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'cs'

LANGUAGES = (
('cs', u'Česky'),
('en', 'English'),
    )

#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False
#USE_L10N = True

STATIC_ROOT = join(ROOT, "m")
STATIC_URL = "/m/"

LOGIN_URL = "/login/"
LOGOUT_URL = "/logout/"
LOGIN_REDIRECT_URL = "/"

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'l=!i_!9q8tc9@jn@m*n*z6zri01$kvjdh94v^1_bzw!8ja5z=*'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
)

ROOT_URLCONF = 'wsgiadmin.urls'

TEMPLATE_DIRS = (
    join(ROOT, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "wsgiadmin.useradmin.context.rosti_context"
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',

    'uni_form',
    'south',

    'wsgiadmin.requests',
    'wsgiadmin.useradmin',
    'wsgiadmin.bills',
    'wsgiadmin.invoices',
    'wsgiadmin.clients',
    'wsgiadmin.domains',
    'wsgiadmin.emails',
    'wsgiadmin.ftps',
    'wsgiadmin.db',
    'wsgiadmin.users',
    'wsgiadmin.apacheconf',
    'wsgiadmin.keystore',
    'wsgiadmin.service',
)

PCP_SETTINGS = {
    "mode": "apache", # main web server, (apache/nginx)
    "primary_dns": None,
    "secondary_dns": None,
    "ipv6": True,
    "fastcgi_wrapper_dir": "/var/www/%s/php5-wrap",

    "nginx_conf": "/etc/nginx/sites-enabled/99_auto.conf",
    "nginx_init_script": "/etc/init.d/nginx",

    "apache_conf": "/etc/apache2/vhosts.d/99_auto.conf",
    "apache_url": "127.0.0.1:8080", # for nginx as proxy
    "apache_init_script": "/etc/init.d/apache2",
    "apache_user": 'www-data', # 'apache' in gentoo

    "uwsgi_conf": "/etc/uwsgi/config.xml",
    "uwsgi_pidfile": "/var/run/uwsgi/app_%d.pid",

    "bind_conf": "/etc/bind/named.pandora.auto",
    "bind_zone_conf": "/etc/bind/pri_auto/%s.zone",
    "bind_init_script": "/etc/init.d/bind9",
    "maildir": "/var/mail",
    "handle_dns": True,
    "dns": {
        #"master": "87.236.194.121",
        #"slave": "89.111.104.70",
        "master": "89.111.104.66",
        "slave": "89.111.104.66",
        "ns1": "ns1.rosti.cz",
        "ns2": "ns2.rosti.cz",
        "mx": "mail.rosti.cz",
        "email": "info.rosti.cz",
        "Refresh": 3600,
        "Retry": 1800,
        "Expire": 604800,
        "Minimum": 30,
        },
    }

VIRTUALENVS_DIR = 'virtualenvs'
LOG_DIR = '/var/log/webs/' #trailing slash required!


## Logování
import logging

try:
    logging.basicConfig(level=logging.INFO, filename='/var/log/pcp.log', format='%(asctime)s %(levelname)s %(message)s')
except IOError:
    pass


