import logging
from django.core.management.base import BaseCommand, CommandError
from wsgiadmin.core.backend_base import Script
from wsgiadmin.core.models import Server
from wsgiadmin.core.utils import get_load_balancers
from wsgiadmin.old.apacheconf.models import UserSite


class Command(BaseCommand):
    args = ""
    help = "Load balancers regeneration for old webapps"

    def handle(self, *args, **options):
        scripts = [Script(server) for server in get_load_balancers()]
        server = self.choose_server()
        for app in UserSite.objects.all():
            print "...", app.main_domain.name
            app.core_server = server
            if app.ssl_mode == "both":
                for script in scripts:
                    self.save_ssl_cert_key(server, app, script)
                    script.commit(no_thread=True)
            for script in scripts:
                script.add_cmd("mkdir -p /etc/nginx/proxy.d/")
                script.add_file("/etc/nginx/proxy.d/oldapp_%.5d.conf" % app.id, "\n".join(self.gen_config(app, script.server_object.os) + self.gen_ssl_config(app, script.server_object.os)))
        for script in scripts:
            script.reload_nginx()
            script.commit(no_thread=True)

    def choose_server(self):
        server_map = {}
        for server in Server.objects.all():
            print "ID %d - %s" % (server.id, server.name)
            server_map[server.id] = server
        server_id = raw_input("What ID do you want to use? ")
        print server_map
        print "You choose %s" % server_map[int(server_id)].name
        return server_map[int(server_id)]

    def get_cert_key(self, server, crtfile, keyfile):
        script = Script(server)
        crt = script.run("cat %s" % crtfile)["stdout"]
        key = script.run("cat %s" % keyfile)["stdout"]
        return crt, key

    def save_ssl_cert_key(self, server, app, script, rm_certs=False):
        crt, key = self.get_cert_key(server, app.ssl_crt, app.ssl_key)
        if app.ssl_crt and app.ssl_key and not rm_certs:
            script.add_cmd("mkdir -p /etc/nginx/ssl/")
            script.add_file("/etc/nginx/ssl/oldapp_%.5d.cert.pem" % app.id, crt)
            script.add_file("/etc/nginx/ssl/oldapp_%.5d.key.pem" % app.id, key)
        else:
            script.add_cmd("rm -f /etc/nginx/ssl/oldapp_%.5d.cert.pem" % app.id)
            script.add_cmd("rm -f /etc/nginx/ssl/oldapp_%.5d.key.pem" % app.id)

    def gen_ssl_config(self, app, os):
        content = []
        if app.ssl_crt and app.ssl_key:
            content.append("server {")
            if os in ("archlinux", ):
                content.append("\tlisten       *:443 ssl;")
            else:
                content.append("\tlisten       [::]:443 ssl;")
            content.append("\tserver_name  %s;" % app.domains)
            content.append("\tssl_certificate      /etc/nginx/ssl/oldapp_%.5d.cert.pem;" % app.id)
            content.append("\tssl_certificate_key  /etc/nginx/ssl/oldapp_%.5d.key.pem;" % app.id)
            content.append("\tlocation / {")
            content.append("\t\tproxy_pass         http://%s/;" % app.core_server.ip)
            content.append("\t\tproxy_redirect     off;")
            content.append("\t}")
            content.append("}\n")
        return content

    def gen_config(self, app, os):
        content = []
        content.append("server {")
        if os in ("archlinux", ):
            content.append("\tlisten       *:80;")
        else:
            content.append("\tlisten       [::]:80;")
        content.append("\tserver_name  %s;" % app.domains)
        content.append("\tlocation / {")
        content.append("\t\tproxy_pass         http://%s/;" % app.core_server.ip)
        content.append("\t\tproxy_redirect     off;")
        content.append("\t}")
        content.append("}\n")
        return content
