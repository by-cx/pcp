from tempfile import gettempdir
from os.path import join, dirname, abspath
import integrate_project

FILE_ROOT = dirname(integrate_project.__file__)

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
        'NAME': join(gettempdir(), 'pcp_integrate_project.db'),
        'TEST_NAME': join(gettempdir(), 'pcp_integrate_project.db'),
    },
}


TIME_ZONE = 'Europe/Prague'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# Make this unique, and don't share it with anybody.
SECRET_KEY = '8TNI#WUTbi4w3tbwuitbowabn3ronIOU!BIUB$R2irniurrwwB'

CURRENCY = (("czk", "CZK"), ("eur", "EUR"), ("usd", "USD"),)
BANK = 'bank'
BANK_ACCOUNT = '1/2'

APPEND_SLASH = True

LOGIN_URL = "/login/"
LOGOUT_URL = "/logout/"
LOGIN_REDIRECT_URL = "/"
