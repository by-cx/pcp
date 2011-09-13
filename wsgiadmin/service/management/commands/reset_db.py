"""
originally from http://www.djangosnippets.org/snippets/828/ by dnordberg

"""

from django.conf import settings
from django.core.management.base import CommandError, BaseCommand
from django.db import connection, DEFAULT_DB_ALIAS
import logging
from optparse import make_option

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--noinput', action='store_false',
                    dest='interactive', default=True,
                    help='Tells Django to NOT prompt the user for input of any kind.'),
        make_option('--no-utf8', action='store_true',
                    dest='no_utf8_support', default=False,
                    help='Tells Django to not create a UTF-8 charset database'),
        make_option('--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS, help='Nominates a database to reset. '
                'Defaults to the "default" database.'),
    )
    help = "Resets the database for this project."

    def handle(self, *args, **options):
        """
        Resets the database for this project.

        Note: Transaction wrappers are in reverse as a work around for
        autocommit, anybody know how to do this the right way?
        """
        verbosity = int(options.get('verbosity', 1))
        database = options.get('database')


        try:
            db = settings.DATABASES[database]
        except KeyError:
            raise Exception('Given database (%s) not found in settings' % database)

        if options.get('interactive'):
            confirm = raw_input("""
You have requested a database reset.
This will IRREVERSIBLY DESTROY
ALL data in the database "%s".
Are you sure you want to do this?

Type 'yes' to continue, or 'no' to cancel: """ % (db['NAME'],))
        else:
            confirm = 'yes'

        if confirm != 'yes':
            print "Reset cancelled."
            return

        engine = db['ENGINE'].split('.')[-1]

        if engine == 'sqlite3':
            import os
            try:
                logging.info("Unlinking sqlite3 database")
                os.unlink(db['NAME'])
            except OSError:
                pass
        elif engine == 'mysql':
            import MySQLdb as Database
            kwargs = {
                'user': db['USER'],
                'passwd': db['PASSWORD'],
            }
            if db['HOST'].startswith('/'):
                kwargs['unix_socket'] = db['HOST']
            else:
                kwargs['host'] = db['HOST']
            if 'PORT' in db and db['PORT']:
                kwargs['port'] = int(db['PORT'])
            connection = Database.connect(**kwargs)
            drop_query = 'DROP DATABASE IF EXISTS %s' % db['NAME']

            charset = ''
            if 'OPTIONS' in db:
                if 'init_command' in db['OPTIONS']:
                    connection.query(db['OPTIONS']['init_command'])

                if 'charset' in db['OPTIONS']:
                    charset = 'CHARACTER SET %s' % db['OPTIONS']['charset']

            create_query = 'CREATE DATABASE %s %s' % (db['NAME'], charset)
            logging.info('Executing... "' + drop_query + '"')
            connection.query(drop_query)
            logging.info('Executing... "' + create_query + '"')
            connection.query(create_query)
        elif engine in ('postgresql', 'postgresql_psycopg2'):
            if engine == 'postgresql':
                import psycopg as Database
            elif engine == 'postgresql_psycopg2':
                import psycopg2 as Database

            if db['NAME'] == '':
                from django.core.exceptions import ImproperlyConfigured
                raise ImproperlyConfigured, "You need to specify NAME of db in your Django settings file."
            if 'USER' in db:
                conn_string = "user=%s" % (db['USER'])
            if 'PASSWORD' in db:
                conn_string += " password='%s'" % db['PASSWORD']
            if 'HOST' in db:
                conn_string += " host=%s" % db['HOST']
            if 'PORT' in db:
                conn_string += " port=%s" % db['PORT']
            connection = Database.connect(conn_string)
            connection.set_isolation_level(0) #autocommit false
            cursor = connection.cursor()
            drop_query = 'DROP DATABASE %s' % db['NAME']
            logging.info('Executing... "' + drop_query + '"')

            try:
                cursor.execute(drop_query)
            except Database.ProgrammingError, e:
                logging.info("Error: "+str(e))

            # Encoding should be SQL_ASCII (7-bit postgres default) or prefered UTF8 (8-bit)
            create_query = ("""
CREATE DATABASE %s
    WITH OWNER = %s
        ENCODING = 'UTF8'
        TABLESPACE = pg_default;
""" % (settings.DATABASE_NAME, settings.DATABASE_USER))
            logging.info('Executing... "' + create_query + '"')
            cursor.execute(create_query)

        else:
            raise CommandError, "Unknown database engine %s", engine

        if verbosity >= 2:
            print "Reset successful."
