import os
import re
from django.conf import settings
from wsgiadmin.apps.models import App
from wsgiadmin.core.backend_base import Script
from wsgiadmin.core.utils import get_load_balancers


class AppException(Exception): pass


class AppBackend(App):

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(AppBackend, self).__init__(*args, **kwargs)
        self.script = Script(self.core_server)
        self.proxy = ProxyObject(self)

    def get_user(self):
        return "app_%.5d" % self.id

    def get_group(self):
        return "app_%.5d" % self.id

    def get_home(self):
        home = os.path.join(settings.APPS_HOME, self.get_user())
        if home != settings.APPS_HOME:
            return home
        raise AppException("Wrong home directory")

    def get_parmameters(self):
        parms = {}
        if self.parameters:
            parms.update(self.parameters)
        parms.update(
            {
                "user": self.get_user(),
                "group": self.get_group(),
                "home": self.get_home(),
                "main_domain": self.main_domain,
                "misc_domains": " ".join(self.misc_domains_list),
                "domains": " ".join(self.domains_list)
            }
        )
        return parms

    def install(self):
        parms = self.get_parmameters()
        self.script.add_cmd("/usr/sbin/groupadd %(group)s" % parms)
        self.script.add_cmd("/usr/sbin/useradd -m -d %(home)s -g %(group)s %(user)s -s /bin/bash" % parms)
        self.script.add_cmd("/usr/sbin/usermod -G %(group)s -a www-data" % parms)
        self.script.add_cmd("mkdir -p %(home)s/logs" % parms, user=self.get_user())
        self.script.add_cmd("mkdir -p %(home)s/app" % parms, user=self.get_user())
        self.script.add_cmd("mkdir -p %(home)s/.ssh" % parms, user=self.get_user())
        self.script.add_cmd("chmod 770 %(home)s/logs" % parms)
        self.script.add_cmd("chmod 750 %(home)s" % parms)
        self.installed = True
        self.save()
        self.proxy.setup()

    def commit(self, no_thread=False):
        self.script.commit(no_thread)

    def disable(self):
        parms = self.get_parmameters()
        self.script.add_cmd("chmod 000 %(home)s" % parms, user=self.get_user())
        self.proxy.setdown()
        self.disabled = True
        self.save()

    def enable(self):
        parms = self.get_parmameters()
        self.script.add_cmd("chmod 750 %(home)s" % parms, user=self.get_user())
        self.proxy.setup()

    def uninstall(self):
        parms = self.get_parmameters()
        self.script.add_cmd("/usr/sbin/userdel %(user)s" % parms)
        self.script.add_cmd("/usr/sbin/groupdel %(group)s" % parms)
        self.script.add_cmd("rm -rf %(home)s" % parms)
        self.script.add_cmd("rm /etc/security/limits.d/%(user)s.conf" % parms)
        self.proxy.setdown()

    def update(self):
        parms = self.get_parmameters()
        limits = "%(user)s         hard    nproc           64\n" % parms
        limits += "%(user)s         hard    as          393216\n" % parms
        self.script.add_file("/etc/security/limits.d/%(user)s.conf" % parms, limits)
        self.proxy.setup()

    def get_logs(self):
        parms = self.get_parmameters()
        logfiles = []
        for logfile in self.script.run("ls \"%(home)s/logs/\"" % parms)["stdout"].split():
            if re.match(".*\.log$", logfile):
                path = os.path.join("%(home)s/logs/" % parms, logfile.strip())
                logfiles.append((path, self.script.run("tail -n 60 %s" % path)["stdout"]))
        return logfiles

    def get_directories(self):
        parms = self.get_parmameters()
        return [x.strip()[len(parms.get("home"))+1:] for x in self.script.run("find -L %s -maxdepth %d -type d" % (parms.get("home"), 3))["stdout"].split("\n")]

    def get_uid(self):
        return int(self.script.run("id -u %s" % self.get_user())["stdout"].strip())

    def get_gid(self):
        return int(self.script.run("id -g %s" % self.get_user())["stdout"].strip())

    def passwd(self, password):
        self.script.add_cmd("/usr/sbin/chpasswd", stdin="%s:%s" % (self.get_user(), password))


class ProxyObject(object):

    def __init__(self, app):
        self.app = app
        self.scripts = []
        self.setup_scripts()

    def setup_scripts(self):
        for server in self.get_servers():
            self.scripts.append((Script(server), server.os))

    def gen_ssl_config(self, os):
        content = []
        if self.app.ssl_cert and self.app.ssl_key:
            content.append("server {")
            if os in ("archlinux", "gentoo", ):
                content.append("\tlisten       *:443 ssl;")
            else:
                content.append("\tlisten       [::]:443 ssl;")
            content.append("\tserver_name  %s;" % self.app.domains)
            content.append("\tssl_certificate      /etc/nginx/ssl/app_%.5d.cert.pem;" % self.app.id)
            content.append("\tssl_certificate_key  /etc/nginx/ssl/app_%.5d.key.pem;" % self.app.id)
            content.append("\tlocation / {")
            content.append("\t\tproxy_pass         http://%s/;" % self.app.core_server.ip)
            content.append("\t\tproxy_redirect     off;")
            content.append("\t}")
            content.append("}\n")
        return content

    def save_ssl_cert_key(self, script, rm_certs=False):
        if self.app.ssl_cert and self.app.ssl_key and not rm_certs:
            script.add_cmd("mkdir -p /etc/nginx/ssl/")
            script.add_file("/etc/nginx/ssl/app_%.5d.cert.pem" % self.app.id, self.app.ssl_cert)
            script.add_file("/etc/nginx/ssl/app_%.5d.key.pem" % self.app.id, self.app.ssl_key)
        else:
            script.add_cmd("rm -f /etc/nginx/ssl/app_%.5d.cert.pem" % self.app.id)
            script.add_cmd("rm -f /etc/nginx/ssl/app_%.5d.key.pem" % self.app.id)

    def gen_config(self, os):
        content = []
        content.append("server {")
        if os in ("archlinux", "gentoo", ):
            content.append("\tlisten       *:80;")
        else:
            content.append("\tlisten       [::]:80;")
        content.append("\tserver_name  %s;" % self.app.domains)
        content.append("\tlocation / {")
        content.append("\t\tproxy_pass         http://%s/;" % self.app.core_server.ip)
        content.append("\t\tproxy_redirect     default;")
        content.append("\t\tproxy_set_header   X-Real-IP  $remote_addr;")
        content.append("\t\tproxy_set_header   Host       $host;")
        content.append("\t}")
        content.append("}\n")
        return content

    def get_servers(self):
        return get_load_balancers()

    def setup(self, reload_nginx=True, no_thread=False):
        for script, os in self.scripts:
            self.save_ssl_cert_key(script)
            script.add_cmd("mkdir -p /etc/nginx/proxy.d/")
            script.add_file("/etc/nginx/proxy.d/app_%.5d.conf" % self.app.id, "\n".join(self.gen_config(os) + self.gen_ssl_config(os)))
            if reload_nginx:
                script.reload_nginx()
            script.commit(no_thread)

    def setdown(self):
        for script, os in self.scripts:
            self.save_ssl_cert_key(script, rm_certs=True)
            script.add_cmd("rm -f /etc/nginx/proxy.d/app_%.5d.conf" % self.app.id)
            script.reload_nginx()
            script.commit()
