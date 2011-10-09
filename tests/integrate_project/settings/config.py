from os.path import join, dirname, abspath
import integrate_project

FILE_ROOT = dirname(integrate_project.__file__)

USERS_FIXTURE = join(FILE_ROOT, 'data', 'users.json')
APPS_FIXTURE = join(FILE_ROOT, 'data', 'apps.json')

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DISABLE_CACHE_TEMPLATE = DEBUG

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

LIVE_SERVER_PORT = '9001'
