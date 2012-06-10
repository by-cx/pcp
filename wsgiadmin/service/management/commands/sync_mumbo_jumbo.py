from django.core.management.base import NoArgsCommand

FIXTURES_DATA = ()

class Command(NoArgsCommand):
    help = 'update triplet'

    def handle(self, *args, **options):
        from django.core.management import call_command

        verbosity = options.get('verbosity')

        commands = (
            ('syncdb',   'Syncing and migrating database.', (), {'migrate': False, 'interactive': False, 'verbosity': verbosity,}, ()),
            ('migrate',  'Run all migrations.',  (), {'merge': True, 'verbosity': verbosity,}, ()),
            ('loaddata', 'Loading fixtures.', FIXTURES_DATA, {'verbosity': verbosity,}, ()),
        )

        for command, message, args, kwargs, errors in commands:
            try:
                if verbosity >= 1:
                    print '\n%s' % message
                call_command(command, *args, **kwargs)
            except errors:
                pass
