import logging
from django.core.management.base import BaseCommand, CommandError
from wsgiadmin.apps.models import App
from wsgiadmin.apps.backend import PythonApp, AppBackend, typed_object, ProxyObject
from wsgiadmin.core.backend_base import BaseScript
from wsgiadmin.core.utils import get_load_balancers
from wsgiadmin.emails.models import Message

class Command(BaseCommand):
    args = ""
    help = "Load balancers regeneration"

    def handle(self, *args, **options):
        print "... removing old config and ssl certificates/keys"
        for server in get_load_balancers():
            script = BaseScript(server)
            script.add_cmd("rm -f /etc/nginx/ssl/*")
            script.add_cmd("rm -f /etc/nginx/proxy.d/*")
            script.commit()
            print "%s cleaned" % server.ip

        print "... generating new config"
        for app in App.objects.all():
            if not app.domains: continue
            print "proxy for %s app set" % ("app_%.5d" % app.id)
            balancer = ProxyObject(app)
            balancer.setup(reload_nginx=False)

        print "... reloading nginxes"
        for server in get_load_balancers():
            script = BaseScript(server)
            script.reload_nginx()
            script.commit()
            print "nginx on %s reloaded" % server.ip

