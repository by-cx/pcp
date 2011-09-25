from tempfile import gettempdir
from os.path import join, dirname, abspath
import unit_project

FILE_ROOT = dirname(unit_project.__file__)

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS


DEBUG = True
TEMPLATE_DEBUG = DEBUG
DISABLE_CACHE_TEMPLATE = DEBUG


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': join(gettempdir(), 'pcp_unit_project.db'),
        'TEST_NAME': join(gettempdir(), 'test_unit_project.db'),
    },
}

TIME_ZONE = 'Europe/Prague'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'xxx'
