# -*- coding: utf-8 -*-.
# Django settings for manager project.

#from django.utils.translation import ugettext_lazy as _

import os,sys
sys.path.append("/home/cx/co/pcp/")
ROOT = os.path.realpath(os.path.dirname(__file__))+"/"

DEBUG = True
TEMPLATE_DEBUG = DEBUG

#APPEND_SLASH = True

ADMINS = ()

MANAGERS = ADMINS

INTERNAL_IPS = ('127.0.0.1','89.111.104.66')

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
STAMP_SIGN = ROOT+"m/razitko.png"
STAMP_NOSIGN = ROOT+"m/razitko-nosign.png"

CURRENCY = (("czk","CZK"), ("eur","EUR"), ("usd","USD"),)

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
	('cs', 'Česky'),
	('en', 'English'),
)

#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False
#USE_L10N = True

MEDIA_ROOT = ROOT+"m/"
MEDIA_URL = "/m/"

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
	'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = 'wsgiadmin.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = (
	"django.contrib.auth.context_processors.auth",
	"django.core.context_processors.debug",
	"django.core.context_processors.i18n",
	"django.core.context_processors.media",
	"django.core.context_processors.static",
	"django.contrib.messages.context_processors.messages",
	"useradmin.context.rosti_context"
)


INSTALLED_APPS = (
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.admin',
	'debug_toolbar',
#	'rosetta',
	'requests',
	'useradmin',
	'uni_form',
	'bills',
	'invoices',
	'clients',
	'domains',
	'emails',
	'ftps',
	'pgs',
	'mysql',
	'users',
	'apacheconf',
	'keystore',
)

DEBUG_TOOLBAR_PANELS = (
	'debug_toolbar.panels.version.VersionDebugPanel',
	'debug_toolbar.panels.timer.TimerDebugPanel',
	'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
	'debug_toolbar.panels.headers.HeaderDebugPanel',
	'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
	'debug_toolbar.panels.template.TemplateDebugPanel',
	'debug_toolbar.panels.sql.SQLDebugPanel',
	'debug_toolbar.panels.signals.SignalDebugPanel',
	'debug_toolbar.panels.logger.LoggingPanel',
)

DEBUG_TOOLBAR_CONFIG = {
	'INTERCEPT_REDIRECTS': False,
}

PCP_SETTINGS = {
	"mode": "apache", # main web server, (apache/nginx)
	"primary_dns": None,
	"secondary_dns": None,
	"ipv6": True,
	"apache_conf": "/etc/apache2/sites-enabled/99_auto.conf",
    "fastcgi_wrapper_dir": "/var/www/%s/php5-wrap",
    "nginx": True,
    "dns": True,
    "apache_url": "127.0.0.1:8080", # for nginx as proxy
	"nginx_conf": "/etc/nginx/sites-enabled/99_auto.conf",
    "nginx_init_script": "/etc/init.d/nginx",
    "apache_init_script": "/etc/init.d/apache2",
	"uwsgi_conf": "/etc/uwsgi/config.xml",
	"uwsgi_pidfile": "/var/run/uwsgi/app_%d.pid",
    "bind_conf": "/etc/bind/named.pandora.auto",
    "bind_zone_conf": "/etc/bind/pri_auto/%s.zone",
    "bind_init_script": "/etc/init.d/bind9",
    "maildir": "/var/mail",
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

## Logování

import logging

logging.basicConfig(level=logging.INFO, filename='/var/log/pcp.log',  format = '%(asctime)s %(levelname)s %(message)s')

from wsgiadmin.mysettings import *
