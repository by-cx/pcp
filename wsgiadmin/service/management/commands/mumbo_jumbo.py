from django.core.management.base import NoArgsCommand
from optparse import make_option
from django.db import DEFAULT_DB_ALIAS

FIXTURES_SITES = (
    'users',
    'clients',
)

class Command(NoArgsCommand):
    help = 'mypage initial command'
    option_list = NoArgsCommand.option_list + (
        make_option('--noinput', action='store_false', dest='interactive', default=True,
            help='Tells Django to NOT prompt the user for input of any kind.'),
        make_option('--coresyncdb', action='store_true', dest='coresyncdb', default=False,
            help='Use non patched django.core syncdb.'),
        make_option('--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS, help='Nominates a database to synchronize. '
                'Defaults to the "default" database.'),
    )

    def handle(self, *args, **options):
        from django.core.management.commands import syncdb
        from django.core.management import call_command
        from django.conf import settings

        interactive = options.get('interactive')
        verbosity = options.get('verbosity')
        use_core_syncdb = options.get('coresyncdb')
        database = options.get('database')

        if database != DEFAULT_DB_ALIAS:# and not use_core_syncdb:
            # see http://code.djangoproject.com/ticket/16039
            print "django does not handle different database sync, I give up"
            return


        if interactive:
            try:
                db = settings.DATABASES[database]
            except KeyError:
                raise Exception('Given database (%s) not found in settings' % database)

            confirm = raw_input('\n'.join((
                'You have requested a database reset.',
                'This will IRREVERSIBLY DESTROY',
                'ALL data in the database "%s".' % db['NAME'],
                'Are you sure you want to do this?',
                '',
                "Type 'yes' to continue, or 'no' to cancel: ")))
        else:
            confirm = 'yes'

        if confirm != 'yes':
            print "Reset cancelled."
            return

        if verbosity >= 1:
            print ''
            print 'Running database reset (drop&create database)'
        call_command('reset_db', verbosity=verbosity, interactive=False, database=database)

        if use_core_syncdb:
            #za tohle pujdu do pekla
            from wsgiadmin.bills.models import balance
            balance._meta.managed = True
            syncdb.Command().execute(**options)
            balance._meta.managed = False
        else:
            call_command('syncdb', verbosity=verbosity, interactive=interactive, migrate=True)


        if verbosity >= 1:
            print ''
            print 'Loading project initial data: '

        for fixt in FIXTURES_SITES:
            if verbosity >= 1:
                print "    %s" % fixt
            call_command('loaddata', fixt, verbosity=verbosity, database=database)
