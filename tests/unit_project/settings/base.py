from os.path import dirname, join, normpath, pardir

USE_I18N = True

FILE_ROOT = normpath(join(dirname(__file__), pardir))

STATIC_ROOT = join(FILE_ROOT, 'm')

STATIC_URL = '/m/'

ADMIN_MEDIA_PREFIX = '/admin_media/'


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'unit_project.template_loader.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'unit_project.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    join(FILE_ROOT, 'templates'),

)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.media',
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
)

INSTALLED_APPS = (
    # main apps
    'django.contrib.contenttypes',
    'django.contrib.sites',
)
