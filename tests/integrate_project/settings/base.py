from os.path import dirname, join, normpath, pardir
from tempfile import gettempdir
import wsgiadmin

USE_I18N = True

FILE_ROOT = normpath(join(dirname(__file__), pardir))

STATIC_ROOT = join(FILE_ROOT, 'm')

STATIC_URL = '/m/'

ADMIN_MEDIA_PREFIX = '/admin_media/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': join(gettempdir(), 'pcp_integrate_project.db'),
        'TEST_NAME': join(gettempdir(), 'pcp_integrate_project.db'),
    },
}


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'integrate_project.template_loader.load_template_source',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'integrate_project.urls'

TEMPLATE_DIRS = (
    join(dirname(wsgiadmin.__file__), 'templates'),
    join(FILE_ROOT, 'templates'),
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

    'crispy_forms',
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
    'wsgiadmin.cron',
    'wsgiadmin.users',
    'wsgiadmin.apacheconf',
    'wsgiadmin.keystore',
    'wsgiadmin.service',
    'wsgiadmin.stats',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '%(asctime)s %(levelname)7s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },
    'handlers': {
        'console': {
            '()': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'INFO',
            },
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
            },

        },
    'root': {
        'handlers': ['console', ],
        'level': 'INFO',
        },
    'django': {
        'handlers': ['console', ],
        'level': 'INFO',
        },
    'django.db.backends': {
        'handlers': ['console', ],
        'level': 'INFO',
        },
    }

DEFAULT_MYSQL_COMMAND = 'mysql -uroot'

VIRTUALENVS_DIR = 'virtualenvs'

CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"

CONSTANCE_CONFIG = {
    "mode": ("apache", "apache or nginx"), # main web server, (apache/nginx)
    "ipv6": (True, "Turn on/off support for IPv6"),
    "maildir": ("/var/mail", "Directory with maildirs"),

    "nginx_conf": ("/etc/nginx/sites-enabled/99_auto.conf", "Nginx's config file"),
    "nginx_init_script": ("/etc/init.d/nginx", "Nginx's init script"),

    "apache_conf": ("/etc/apache2/vhosts.d/99_auto.conf", "Apache's config file"),
    "apache_url": ("127.0.0.1:8080", "Apache proxy URL (for nginx)"), # for nginx as proxy
    "apache_init_script": ("/etc/init.d/apache2", "Apache's init script"),
    "apache_user": ('www-data', "Apache's user"), # 'apache' in gentoo
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
    "find_directory_deep":(2, "Finding directory deep"),
    }
