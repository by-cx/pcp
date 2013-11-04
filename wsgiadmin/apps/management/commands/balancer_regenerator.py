import logging
from django.core.management.base import BaseCommand, CommandError
from wsgiadmin.apps.models import App
from wsgiadmin.apps.backend import typed_object
from wsgiadmin.apps.backend.main import AppBackend, ProxyObject
from wsgiadmin.apps.backend.python import PythonApp
from wsgiadmin.core.backend_base import Script
from wsgiadmin.core.utils import get_load_balancers
from wsgiadmin.emails.models import Message

class Command(BaseCommand):
    args = ""
    help = "Load balancers regeneration"

    def handle(self, *args, **options):
        print "... removing old config and ssl certificates/keys"
        for server in get_load_balancers():
            script = Script(server)
            script.add_cmd("rm -f /etc/nginx/ssl/*")
            script.add_cmd("rm -f /etc/nginx/proxy.d/*")
            script.commit(no_thread=True)
            print "%s cleaned" % server.ip

        print "... generating new config"
        for app in App.objects.filter(disabled=False):
            if not app.domains: continue
            print "proxy for %s app set" % ("app_%.5d" % app.id)
            balancer = ProxyObject(app)
            balancer.setup(reload_nginx=False, no_thread=True)

        print "... reloading nginxes"
        for server in get_load_balancers():
            script = Script(server)
            script.reload_nginx()
            script.commit(no_thread=True)
            print "nginx on %s reloaded" % server.ip

