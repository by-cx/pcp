import logging


logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s %(levelname)s %(message)s',
)

logging.disable(logging.DEBUG)


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'rosti',
        'TEST_NAME': 'test_rosti',
        'USERNAME': 'yed',
        'PASSWORD': 'heslo',
        'HOST': 'localhost',
    },
}


DEFAULT_MYSQL_COMMAND = 'mysql -uroot -pdbpwd'
