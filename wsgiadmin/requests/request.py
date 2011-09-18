# -*- coding: utf-8 -*-

import subprocess
from datetime import datetime, timedelta
import json
import shlex
from os.path import join
from django.db.models.query_utils import Q

from django.template.loader import render_to_string
from django.conf import settings

from wsgiadmin.apacheconf.models import UserSite
from wsgiadmin.domains.models import Domain
from wsgiadmin.requests.models import Request
from wsgiadmin.clients.models import Machine



class RequestException(Exception): pass


class SSHHandler(object):
    def __init__(self, user, machine):
        self.machine = machine
        self.user = user

        self.commit_machine = None

    def _server_name(self):
        if self.commit_machine:
            return self.commit_machine
        else:
            return str(self.machine.name)

    def _run(self, cmd, stdin=None):
        cmd = "ssh %s %s" % (self._server_name(), cmd)
        print cmd
        stdin_flag = subprocess.PIPE if stdin is not None else stdin
        p = subprocess.Popen(shlex.split(str(cmd)), stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=stdin_flag)
        stdout, stderr = p.communicate(stdin)
        return stdout, stderr, p.wait()

    def _write(self, filename, content):
        cmd = "tee %s" % filename

        stdout, stderr, retcode = self._run(cmd, stdin=content)

        return stdout, stderr, retcode

    def _unlink(self, filename):
        cmd = "rm %s" % filename

        stdout, stderr, retcode = self._run(cmd)

        return stdout, stderr, retcode

    def run(self, cmd, stdin=None, plan_to=None):
        """
        Add cmd into queue.
        """
        r = Request()

        r.action = "run"
        r.machine = self._server_name()
        r.data = json.dumps({"action": "run", "cmd": cmd, "stdin": stdin})
        r.user = self.user
        if plan_to: r.plan_to_date = plan_to
        r.save()

    def instant_run(self, cmd, stdin=None):
        """Run cmd and return result promptly. You can give stdin string too."""
        r = Request()

        r.action = "run"
        r.machine = self._server_name()
        r.data = json.dumps({"action": "run", "cmd": cmd, "stdin": stdin})
        r.user = self.user
        r.save()

        stdout, stderr, retcode = self._run(cmd, stdin)

        r.done_date = datetime.today()
        r.done = True
        r.stdout = stdout
        r.stderr = stderr

        r.save()

        return stdout, stderr, retcode

    def write(self, filename, content, plan_to=None):
        """
        Add request into queue to write the content into filename.
        """
        r = Request(action='write')
        r.machine = self._server_name()
        r.data = json.dumps({"action": "write", "filename": filename, "content": content})
        r.user = self.user
        if plan_to: r.plan_to_date = plan_to
        r.save()

    def unlink(self, filename, plan_to=None):
        """Add request into queue to unlink filename."""
        r = Request(action='unlink')
        r.machine = self._server_name()
        r.data = json.dumps({"action": "unlink", "filename": filename})
        r.user = self.user
        if plan_to: r.plan_to_date = plan_to
        r.save()

    def read(self, filename):
        """Read filename promtly."""
        cmd = "cat %s" % filename

        r = Request(action="read")
        r.machine = self._server_name()
        r.data = json.dumps({"action": "read", "cmd": cmd})
        r.user = self.user
        r.save()

        stdout, stderr, retcode = self._run(cmd)

        r.done_date = datetime.today()
        r.done = True
        r.stdout = stdout
        r.stderr = stderr
        r.retcode = retcode

        r.save()

        return stdout

    def isfile(self, filename):
        """Return true, if filename is exists."""
        cmd = "if [ `ls %s 2> /dev/null` ]; then echo 1; fi;" % filename

        r = Request(action="read")
        r.machine = self._server_name()
        r.data = json.dumps({"action": "isfile", "cmd": cmd})
        r.user = self.user
        r.save()

        stdout, stderr, retcode = self._run(cmd)

        r.done_date = datetime.today()
        r.done = True
        r.stdout = stdout
        r.stderr = stderr
        r.retcode = retcode

        r.save()

        return stdout.strip() == "1"

    def commit(self):
        """
        Process the queue and writes the result into db
        """
        for request in Request.objects. \
                filter(Q(plan_to_date__lte=datetime.today()) | Q(plan_to_date__isnull=True), done=False).\
                order_by("add_date"):
            self.commit_machine = request.machine

            data = json.loads(request.data)
            ret = None

            if request.action == "run":
                ret = self._run(data["cmd"])
            elif request.action == "write":
                ret = self._write(data["filename"], data["content"])
            elif request.action == "unlink":
                ret = self._unlink(data["filename"])

            if ret:
                request.done_date = datetime.today()
                request.done = True
                request.stdout = ret[0]
                request.stderr = ret[1]
                request.retcode = ret[2]

                request.save()

#class JSONRPCHandler(object): pass

class Service(SSHHandler):
    def __init__(self, user, machine, init_script):
        super(Service, self).__init__(user, machine)

        self.init_script = init_script

    def state(self):
        """Return state of service. True for running, False for oposite."""

    def start(self):
        """Start service"""

        self.run("%s start" % self.init_script)

    def stop(self):
        """Stop service"""

        self.run("%s stop" % self.init_script)

    def restart(self):
        """Restart service"""

        self.run("%s restart" % self.init_script)

    def reload(self):
        """Reload service"""

        self.run("%s reload" % self.init_script)


class UWSGIRequest(SSHHandler):

    def __init__(self, *args, **kwargs):
        super(UWSGIRequest, self).__init__(*args, **kwargs)

        self.config_location = settings.PCP_SETTINGS.get("uwsgi_conf", "/etc/uwsgi/config.xml")

    def mod_config(self):
        uwsgi = ["<rosti>"]

        sites = UserSite.objects.filter(type="uwsgi")
        for site in sites:
            uwsgi.append("<uwsgi id=\"%d\">" % site.id)
            home = site.owner.parms.home
            for pp in [join(home, x.strip()) for x in site.python_path.split("\n") if x.strip()]:
                uwsgi.append("\t<pythonpath>%s</pythonpath>" % pp)

            uwsgi.append("\t<master/>")
            uwsgi.append("\t<no-orphans/>")
            uwsgi.append("\t<processes>%s</processes>" % site.processes)
            uwsgi.append("\t<optimize>0</optimize>")
            uwsgi.append("\t<home>%s</home>" % site.virtualenv_path)
            uwsgi.append("\t<limit-as>128</limit-as>")
            uwsgi.append("\t<chmod-socket>660</chmod-socket>")
            uwsgi.append("\t<uid>%s</uid>" % site.owner.username)
            uwsgi.append("\t<gid>%s</gid>" % site.owner.username)
            uwsgi.append("\t<pidfile>%s</pidfile>" % site.pidfile)
            uwsgi.append("\t<socket>%s</socket>" % site.socket)
            uwsgi.append("\t<wsgi-file>%s</wsgi-file>" % site.script)
            uwsgi.append("\t<daemonize>%s</daemonize>" % site.logfile)
            uwsgi.append("\t<chdir>%s</chdir>" % home)

            uwsgi.append("</uwsgi>")

        uwsgi.append("</rosti>")
        self.write(self.config_location, "\n".join(uwsgi))

    def start(self, site):
        """Start site"""
        self.run("/usr/bin/uwsgi-manager.py -s %s" % str(site.id))

    def restart(self, site):
        """Restart site"""
        self.run("/usr/bin/uwsgi-manager.py -R %s" % str(site.id))

    def stop(self, site):
        """Stop site"""
        self.run("/usr/bin/uwsgi-manager.py -S %s" % str(site.id))

    def reload(self, site):
        """Reload site"""
        self.run("/usr/bin/uwsgi-manager.py -r %s" % str(site.id))


class NginxRequest(Service):
    def __init__(self, user, machine):
        super(NginxRequest, self).__init__(user, machine, settings.PCP_SETTINGS.get("nginx_init_script", "/etc/init.d/nginx"))
        self.config_location = settings.PCP_SETTINGS["nginx_conf"]

    def mod_vhosts(self):
        config = []
        sites = UserSite.objects.filter(removed=False, owner__parms__enable=True)
        for site in sites:
            if site.type in ("uwsgi", "modwsgi"):
                config.append(render_to_string("nginx_vhost_wsgi.conf", {
                    "site": site
                }))
            elif site.type == "php":
                # PHP always throw Apache
                config.append(render_to_string("nginx_vhost_proxy.conf", {
                    "site": site,
                    "proxy": settings.PCP_SETTINGS.get("apache_url"),
                }))
            elif site.type == "static":
                config.append(render_to_string("nginx_vhost_static.conf", {
                    "site": site
                }))
        self.write(self.config_location, "\n".join(config))


class ApacheRequest(Service):
    def __init__(self, user, machine):
        super(ApacheRequest, self).__init__(user, machine, settings.PCP_SETTINGS.get("apache_init_script", "/etc/init.d/apache"))

        self.config_location = settings.PCP_SETTINGS['apache_conf']


    def mod_vhosts(self):
        config = []
        sites = UserSite.objects.filter(removed=False, owner__parms__enable=True)
        for site in sites:
            if site.type in ("uwsgi", "modwsgi"):
                # Nginx mode cancel handling wsgi by Apache
                if settings.PCP_SETTINGS["mode"] != "apache": continue

                config.append(render_to_string("apache_vhost_wsgi.conf", {
                    "site": site,
                }))
            else:
                config.append(render_to_string("apache_vhost_%s.conf" % site.type, {
                    "site": site
                }))
        self.write(self.config_location, "\n".join(config))


class BindRequest(Service):

    def __init__(self, user, ns="master"):
        self.ns = ns

        try:
            machine = Machine.objects.get(ip=settings.PCP_SETTINGS["dns"][self.ns])
        except Machine.DoesNotExist:
            raise RequestException("Error: NS machine not found")

        super(Service, self).__init__(user, machine, settings.PCP_SETTINGS.get("bind_init_script", "/etc/init.d/bind9"))

    def mod_zone(self, domain):
        config = render_to_string("bind_zone.conf", {
            "domain": domain,
            "dns": settings.PCP_SETTINGS.get("dns"),
            })
        self.write(settings.PCP_SETTINGS["bind_zone_conf"] % domain.name, config)

    def remove_zone(self, domain):
        self.unlink(settings.PCP_SETTINGS["bind_zone_conf"] % domain.name)
        self.mod_config()

    def mod_config(self):
        if self.ns == "master":
            tmpl = "bind_primary.conf"
        else:
            tmpl = "bind_secondary.conf"
        config = render_to_string(tmpl, {
            "domains": Domain.objects.all(),
            "dns": settings.PCP_SETTINGS["dns"],
            })
        self.write(settings.PCP_SETTINGS["bind_conf"], config)


class EMailRequest(SSHHandler):
    def create_mailbox(self, email):
        homedir = join(settings.PCP_SETTINGS["maildir"], email.domain.name)
        maildir = join(homedir, email.login)

        self.run("/bin/mkdir -p %s" % homedir)
        self.run("/bin/chown email:email %s -R" % homedir)
        self.run("/usr/bin/maildirmake %s" % maildir)
        self.run("/bin/chown email:email %s -R" % maildir)
        self.run("/usr/bin/maildirmake %s" % maildir + ".Spam")
        self.run("/bin/chown email:email %s -R" % maildir + "/Spam")

    def remove_mailbox(self, email):
        homedir = settings.PCP_SETTINGS["maildir"] + "/" + email.domain.name + "/"
        maildir = homedir + email.login + "/"
        self.run("rm -rf %s" % maildir, plan_to=datetime.today() + timedelta(90))


class PostgreSQLRequest(SSHHandler):

    def add_db(self, db, password):
        self.run("createuser -D -R -S %s" % db)
        self.passwd_db(db, password)

    def remove_db(self, db):
        self.run("dropdb %s" % db)
        self.run("dropuser %s" % db)

    def passwd_db(self, db, password):
        sql = "ALTER USER %s WITH PASSWORD '%s';" % (db, password)
        self.run("psql template1", stdin=sql)


class MySQLRequest(SSHHandler):
    def add_db(self, db, password):
        sql = []

        sql.append("CREATE DATABASE %s;" % db)
        sql.append("CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';" % (db, password))
        sql.append("GRANT ALL PRIVILEGES ON %s.* TO '%s'@'localhost' WITH GRANT OPTION;" % (db, db))

        for x in sql:
            self.run("mysql -u root", stdin=x)

    def remove_db(self, db):
        sql = []

        sql.append("DROP DATABASE %s;" % db)
        sql.append("DROP USER '%s'@'localhost';" % db)

        for x in sql:
            self.run("mysql -u root", stdin=x)

    def passwd_db(self, db, password):
        sql = []

        sql.append("UPDATE mysql.user SET Password = PASSWORD('%s') WHERE User = '%s';" % (password, db))
        sql.append("FLUSH PRIVILEGES;")

        for x in sql:
            self.run("mysql -u root", stdin=x)


class SystemRequest(SSHHandler):
    def install(self, user):
        HOME = join("/home", user.username)

        self.run("useradd -m -s /bin/bash %s" % user.username)
        self.run("chmod 750 %s " % HOME)
        self.run("cp -R /var/www/cx /var/www/%s" % user.username)
        self.run("chown -R %s:%s /var/www/%s" % (user.username, user.username, user.username))
        self.run("usermod -G %s -a %s" % (user.username, user.username))
        self.run("usermod -G www-data -a %s" % user.username)
        self.run("usermod -G clients -a %s" % user.username)
        self.run("su %s -c \"mkdir -p ~/%s\"" % (user.username, settings.VIRTUALENVS_DIR))
        self.run("su %s -c  \"virtualenv ~/%s/default\"" % (user.username, settings.VIRTUALENVS_DIR))
        self.run("su %s -c \"mkdir -p ~/uwsgi\"" % user.username)

    def passwd(self, password):
        self.run("/usr/sbin/chpasswd", stdin="%s:%s" % (self.user.username, password))

#TODO:E-mail request

def main():
    """
    from wsgiadmin.requests.request import main
    main()
    """

    from wsgiadmin.clients.models import Machine, Parms

    m = Machine.objects.all()[0]
    u = Parms.objects.all()[0].user

    #nr = NginxRequest(u, m)
    #nr.restart()

    sh = SSHHandler(u, m)
    #print sh.instant_run("uptime")
    #sh._write("/tmp/writetest", "můj obsah")
    sh.commit()
