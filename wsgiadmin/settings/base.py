# -*- coding: utf-8 -*-.
# Django settings for manager project.
import os

_ = lambda x: x

from os.path import join, abspath, pardir, dirname
ROOT = abspath(join(dirname(__file__), pardir))

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEBUG_TOOLBAR = DEBUG
ENABLE_DEBUG_URLS = DEBUG

APPEND_SLASH = True

MANAGERS = ADMINS = ()

INTERNAL_IPS = ('127.0.0.1', '89.111.104.66')
ALLOWED_HOSTS = (
    "localhost",
    "localhost:8000"
)

DATABASES = {}

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# User logs

USERLOG_FILENAME = "%s/logs/%s.log"

## Faktury

BANK = "mBank"
BANK_ACCOUNT = "670100-2206514444/6210"
MY_ADDRESS_ID = 1
STAMP_SIGN = join(ROOT, "static", "razitko.png")
STAMP_NOSIGN = join(ROOT, "static", "razitko-nosign.png")

CURRENCY = (
    ("czk", "CZK"),
    ("eur", "EUR"),
    ("usd", "USD"),
)

GOPAY = False
FIO_TOKEN = ""


##########

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}

APPS_HOME = "/home/apps"

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
USE_I18N = True
#USE_L10N = True

LOCALE_PATHS = (
    join(ROOT, "locale")
)

STATIC_ROOT = join(ROOT, "..", "static")
STATIC_URL = "/static/"

STATICFILES_DIRS = (
    join(ROOT, 'static'),
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)


LOGIN_URL = "/login/"
LOGOUT_URL = "/logout/"
LOGIN_REDIRECT_URL = "/"

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'l=!i_!9q8tc9@jn@m*n*z6zri01$kvjdh94v^1_bzw!8ja5z=*'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
#    'integrate_project.template_loader.load_template_source',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
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
    "wsgiadmin.useradmin.context.rosti_context",
    'constance.context_processors.config',
    'wsgiadmin.core.context.django_settings',
    "wsgiadmin.core.context.capabilities",
)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.admin',

    'djcelery',
    'rosetta',
    'crispy_forms',
    'south',
    'constance',
    'constance.backends.database',
    'raven.contrib.django',
    # not necessarly, make it optional
    'djcelery',

    'wsgiadmin.useradmin',
    'wsgiadmin.clients',
    'wsgiadmin.dns',
    'wsgiadmin.emails',
    'wsgiadmin.users',
    'wsgiadmin.service',
    'wsgiadmin.stats',
    'wsgiadmin.core',
    'wsgiadmin.apps',
]

PYTHON_INTERPRETERS = {
    "python2.7": "/usr/bin/virtualenv",
}

VIRTUALENVS_DIR = 'virtualenvs'

PAYMENT_CHOICES = (
    ("per_web", _("Per application (60 CZK/app/month)")),
    ("fee", _("Constant fee (200 CZK/196 MB RAM)")),
)

LOCALE_PATHS = (
    join(ROOT, "locale"),
)

# support for old style apps/emails/ftp/.. implementation
OLD = False

BROKER_URL = 'redis://localhost/'

SSH_PRIVATEKEY = join(os.environ.get('HOME', "/"), ".ssh", "id_dsa")
SSH_HOSTKEYS = join(os.environ.get('HOME', "/"), ".ssh", "known_hosts")

VIRT = False

## Logování
import logging

if not os.path.isdir(join(ROOT, "logs")):
    os.makedirs(join(ROOT, "logs"))

try:
    logging.basicConfig(level=logging.INFO, filename=join(ROOT, "logs", 'pcp.log'), format='%(asctime)s %(levelname)s %(message)s')
except IOError:
    pass


