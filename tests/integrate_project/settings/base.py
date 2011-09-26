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
    'django.core.context_processors.media',
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
)

INSTALLED_APPS = (
    # main apps
    'wsgiadmin.apacheconf',
    'wsgiadmin.domains',
    'wsgiadmin.useradmin',
    'wsgiadmin.users',
    'wsgiadmin.clients',
    'wsgiadmin.db',

    # django contrib apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.redirects',
    'django.contrib.admin',
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
