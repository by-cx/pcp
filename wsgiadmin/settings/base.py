# -*- coding: utf-8 -*-.
# Django settings for manager project.

_ = lambda x: x

#import os
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

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

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
USE_I18N = True
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
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',

    'uni_form',
    'south',
    'constance',
    'constance.backends.database',

    'wsgiadmin.requests',
    'wsgiadmin.useradmin',
    'wsgiadmin.clients',
    'wsgiadmin.domains',
    'wsgiadmin.emails',
    'wsgiadmin.ftps',
    'wsgiadmin.db',
    'wsgiadmin.users',
    'wsgiadmin.apacheconf',
    'wsgiadmin.keystore',
    'wsgiadmin.service',
    'wsgiadmin.stats',
)

CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"

CONSTANCE_CONFIG = {
    "email": ("info@rosti.cz", "Your e-mail"),

    "mode": ("apache", "apache or nginx"), # main web server, (apache/nginx)
    "ipv6": (True, "Turn on/off support for IPv6"),
    "maildir": ("/var/mail", "Directory with maildirs"),

    "nginx_conf": ("/etc/nginx/sites-enabled/99_auto.conf", "Nginx's config file"),
    "nginx_init_script": ("/etc/init.d/nginx", "Nginx's init script"),
    "nginx_listen": ("[::]:80", "Listen config directive"),
    "nginx_ssl_listen": ("[::]:443", "Listen config directive"),
    "nginx_log_dir": ("/var/log/webx/", "NGINX log directory"),

    "apache_conf": ("/etc/apache2/vhosts.d/99_auto.conf", "Apache's config file"),
    "apache_url": ("127.0.0.1:8080", "Apache proxy URL (for nginx)"), # for nginx as proxy
    "apache_ssl_listen": ("127.0.0.1:443", "Apache listen for SSL"),
    "apache_init_script": ("/etc/init.d/apache2", "Apache's init script"),
    "apache_user": ('www-data', "Apache's user"), # 'apache' in gentoo
    "apache_log_dir": ("/var/log/webs/", "Apache log directory"),
    "fastcgi_wrapper_dir": ("/var/www/%s/php5-wrap", "PATH to fastcgi wrapper (user will be filled)"),

    "uwsgi_conf": ("/etc/uwsgi/config.xml", "uWSGI's XML config file"),
    "uwsgi_pidfile": ("/var/run/uwsgi/app_%d.pid", "uWSGI's app pidfile"),
    "uwsgi_memory": (192, "Memory for uWSGI app"),

    "bind_conf": ("/etc/bind/named.pandora.auto", "BIND's config"),
    "bind_zone_conf": ("/etc/bind/pri_auto/%s.zone", "BIND's zone file"),
    "bind_init_script": ("/etc/init.d/bind9", "BIND's init script"),

    "handle_dns": (False, "Use BIND"),
    "dns_master": ("", "Master NS server (IP)"),
    "dns_slave": ("", "Slave NS server (IP)"),
    "dns_ns1": ("ns1.example.com", "NS1 domain"),
    "dns_ns2": ("ns2.example.com", "NS2 domain"),
    "dns_mx": ("mail.example.com", "MX server"),
    "dns_email": ("info.example.com", "Admin of DNS"),
    "dns_refresh": (3600, "Refresh"),
    "dns_retry": (1800, "Retry"),
    "dns_expire": (604800, "Expire"),
    "dns_minimum": (30, "Minimum"),

    "default_web_machine": ("localhost", "Default web machine for new accounts. (must be in Machines table)"),
    "default_mail_machine": ("localhost", "Default mail machine for new accounts. (must be in Machines table)"),
    "default_mysql_machine": ("localhost", "Default mysql machine for new accounts. (must be in Machines table)"),
    "default_pgsql_machine": ("localhost", "Default pgsql machine for new accounts. (must be in Machines table)"),

    "mysql_bind": ("localhost", "Host for mysql's users"),

    "email_uid": (117, "Email UID"),
    "email_gid": (117, "Email GID"),

    "credit_wsgi": (1.0, "Credits for WSGI"),
    "credit_wsgi_proc": (0.2, "Credits for extra WSGI process"),
    "credit_php": (1.0, "Credits for PHP"),
    "credit_static": (0.25, "Credits for STATIC"),
    "credit_fee": (3.0, "Credits for VM"),
    "credit_bm": (8.0, "Credits for VM"),
    "credit_description": ("1 cr. = 2 Kč", "Credit description"),
    "credit_250_bonus": (1.0, "250 credits bonus (credits * this number)"),
    "credit_500_bonus": (1.1, "500 credits bonus (credits * this number)"),
    "credit_750_bonus": (1.1, "750 credits bonus (credits * this number)"),
    "credit_1000_bonus": (1.2, "500 credits bonus (credits * this number)"),
    "credit_currency": ("0.5,12.5,9.5", "CZK, EUR, USD"),

    "terms_url": ("", "Terms URL"),

    "find_directory_deep":(2, "Finding directory deep"),
    }

VIRTUALENVS_DIR = 'virtualenvs'
LOG_DIR = '/var/log/webs/' #trailing slash required!

PAYMENT_CHOICES = (
    ("per_web", _("Per application (60 CZK/app/month)")),
    ("fee", _("Constant fee (200 CZK/196 MB RAM)")),
)

## Logování
import logging

try:
    logging.basicConfig(level=logging.INFO, filename='/var/log/pcp.log', format='%(asctime)s %(levelname)s %(message)s')
except IOError:
    pass


