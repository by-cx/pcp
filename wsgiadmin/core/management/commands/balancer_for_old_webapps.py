import logging
from django.core.management.base import BaseCommand, CommandError
from wsgiadmin.core.backend_base import Script
from wsgiadmin.core.utils import get_load_balancers
from wsgiadmin.old.apacheconf.models import UserSite


class Command(BaseCommand):
    args = ""
    help = "Load balancers regeneration for old webapps"

    def handle(self, *args, **options):
        print "... removing old config and ssl certificates/keys"

        scripts = [Script(server) for server in get_load_balancers()]
        for app in UserSite.objects.all():
            if app.ssl_mode == "both":
                for script in scripts:
                    self.save_ssl_cert_key(app, script)
                    script.commit(no_thread=True)
            for script in scripts:
                script.add_cmd("mkdir -p /etc/nginx/proxy.d/")
                script.add_file("/etc/nginx/proxy.d/app_%.5d.conf" % app.id, "\n".join(self.gen_config(app) + self.gen_ssl_config(app)))
        for script in scripts:
            script.reload_nginx()
            script.commit(no_thread=True)

    def save_ssl_cert_key(self, app, script, rm_certs=False):
        if app.ssl_crt and app.ssl_key and not rm_certs:
            script.add_cmd("mkdir -p /etc/nginx/ssl/")
            script.add_file("/etc/nginx/ssl/oldapp_%.5d.cert.pem" % app.id, app.ssl_crt)
            script.add_file("/etc/nginx/ssl/oldapp_%.5d.key.pem" % app.id, app.ssl_key)
        else:
            script.add_cmd("rm -f /etc/nginx/ssl/app_%.5d.cert.pem" % app.id)
            script.add_cmd("rm -f /etc/nginx/ssl/app_%.5d.key.pem" % app.id)

    def gen_ssl_config(self, app):
        content = []
        if self.app.ssl_cert and app.ssl_key:
            content.append("server {")
            content.append("\tlisten       [::]:443 ssl;")
            content.append("\tserver_name  %s;" % app.domains)
            content.append("\tssl_certificate      /etc/nginx/ssl/oldapp_%.5d.cert.pem" % app.id)
            content.append("\tssl_certificate_key  /etc/nginx/ssl/oldapp_%.5d.key.pem" % app.id)
            content.append("\tlocation / {")
            content.append("\t\tproxy_pass         http://%s/;" % app.core_server.ip)
            content.append("\t\tproxy_redirect     off;")
            content.append("\t}")
            content.append("}\n")
        return content

    def gen_config(self, app):
        content = []
        content.append("server {")
        content.append("\tlisten       [::]:80;")
        content.append("\tserver_name  %s;" % app.domains)
        content.append("\tlocation / {")
        content.append("\t\tproxy_pass         http://%s/;" % app.core_server.ip)
        content.append("\t\tproxy_redirect     off;")
        content.append("\t}")
        content.append("}\n")
        return content