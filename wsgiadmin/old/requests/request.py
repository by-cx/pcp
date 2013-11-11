# -*- coding: utf-8 -*-

import subprocess
import json
import shlex
from os.path import join
from datetime import datetime, timedelta, date

from constance import config
from django.db.models.query_utils import Q
from django.template.loader import render_to_string
from django.conf import settings

from wsgiadmin.old.apacheconf.models import UserSite
from wsgiadmin.old.domains.models import Domain
from wsgiadmin.old.requests.models import Request
from wsgiadmin.clients.models import Machine


class RequestException(Exception): pass


class SSHHandler(object):
    # raise exception if not overriden, maybe
    _default_cmd = ""

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
        server = self._server_name()
        if server != 'localhost':
            cmd = 'ssh %s "%s"' % (server, cmd)

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

    def run(self, cmd=None, stdin=None, plan_to=None, wipe=False, instant=False):
        """
        Add cmd into queue if instant is False, otherwise run instantly
        """
        cmd = cmd or self._default_cmd
        r = Request(action='run' if not wipe else 'run|wipe')
        r.machine = self._server_name()
        r.data = json.dumps({"action": "run", "cmd": cmd, "stdin": stdin})
        r.user = self.user

        if not instant:
            r.plan_to_date = plan_to
            r.save()

        else:
            stdout, stderr, retcode = self._run(cmd, stdin)

            r.done_date = datetime.now()
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

            if request.action in ("run", "run|wipe"):
                ret = self._run(data["cmd"], data['stdin'])
            elif request.action == "write":
                ret = self._write(data["filename"], data["content"])
            elif request.action == "unlink":
                ret = self._unlink(data["filename"])

            if ret:
                request.done_date = datetime.today()
                request.done = True
                request.stdout, request.stderr, request.retcode = ret[:3]
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

        self.config_path = config.uwsgi_conf

    def mod_config(self):
        uwsgi = ["<rosti>"]

        sites = UserSite.objects.filter(type="uwsgi")
        for site in sites:
            uwsgi.append("<uwsgi id=\"%d\">" % site.id)
            home = site.owner.parms.home

            uwsgi.append("\t<master/>")
            uwsgi.append("\t<no-orphans/>")
            uwsgi.append("\t<enable-threads/>")
            uwsgi.append("\t<processes>%s</processes>" % site.processes)
            uwsgi.append("\t<optimize>0</optimize>")
            uwsgi.append("\t<home>%s</home>" % site.virtualenv_path)
            uwsgi.append("\t<limit-as>%d</limit-as>" % config.uwsgi_memory)
            uwsgi.append("\t<chmod-socket>660</chmod-socket>")
            uwsgi.append("\t<uid>%s</uid>" % site.owner.username)
            uwsgi.append("\t<gid>%s</gid>" % site.owner.username)
            uwsgi.append("\t<pidfile>%s</pidfile>" % site.pidfile)
            uwsgi.append("\t<socket>%s</socket>" % site.socket)
            uwsgi.append("\t<wsgi-file>%s</wsgi-file>" % site.script)
            uwsgi.append("\t<daemonize>%s</daemonize>" % site.logfile)
            uwsgi.append("\t<chdir>%s</chdir>" % home)
            for pp in [join(home, x.lstrip("/")) for x in site.python_path.split("\n") if x.lstrip("/")]:
                uwsgi.append("\t<pythonpath>%s</pythonpath>" % pp.strip())

            uwsgi.append("</uwsgi>")

        uwsgi.append("</rosti>")
        self.write(self.config_path, "\n".join(uwsgi))

    def start(self, site, instant=False):
        """Start site"""
        self.run("/usr/bin/env uwsgi-manager -s %s" % str(site.id), instant=instant)

    def restart(self, site, instant=False):
        """Restart site"""
        self.run("/usr/bin/env uwsgi-manager -R %s" % str(site.id), instant=instant)

    def stop(self, site, instant=False):
        """Stop site"""
        self.run("/usr/bin/env uwsgi-manager -S %s" % str(site.id), instant=instant)

    def reload(self, site, instant=False):
        """Reload site"""
        self.run("/usr/bin/env uwsgi-manager -r %s" % str(site.id), instant=instant)


class NginxRequest(Service):
    def __init__(self, user, machine):
        super(NginxRequest, self).__init__(user, machine, config.nginx_init_script)
        self.config_path = config.nginx_conf

    def mod_vhosts(self):
        configfile = []
        sites = UserSite.objects.filter(owner__parms__enable=True)
        for site in sites:
            if not site.main_domain.enable: continue
            if site.type== "uwsgi":
                if site.ssl_mode in ("none", "both"):
                    configfile.append(render_to_string("nginx_vhost_wsgi.conf", {
                        "site": site,
                        'log_dir': config.nginx_log_dir,
                        "config": config,
                        "ssl": False,
                    }))
                if site.ssl_mode in ("both", "sslonly"):
                    configfile.append(render_to_string("nginx_vhost_wsgi.conf", {
                        "site": site,
                        'log_dir': config.nginx_log_dir,
                        "config": config,
                        "ssl": True,
                    }))
            elif site.type in ("php", "modwsgi"):
                # PHP always throw Apache
                if site.ssl_mode in ("none", "both"):
                    configfile.append(render_to_string("nginx_vhost_proxy.conf", {
                        "site": site,
                        "proxy": config.apache_url,
                        'log_dir': config.nginx_log_dir,
                        "config": config,
                        "ssl": False,
                    }))
                if site.ssl_mode in ("both", "sslonly"):
                    configfile.append(render_to_string("nginx_vhost_proxy.conf", {
                        "site": site,
                        "proxy": config.apache_url,
                        'log_dir': config.nginx_log_dir,
                        "config": config,
                        "ssl": True,
                    }))
            elif site.type == "static":
                if site.ssl_mode in ("none", "both"):
                    configfile.append(render_to_string("nginx_vhost_static.conf", {
                        "site": site,
                        'log_dir': config.nginx_log_dir,
                        "config": config,
                        "ssl": False,
                    }))
                if site.ssl_mode in ("both", "sslonly"):
                    configfile.append(render_to_string("nginx_vhost_static.conf", {
                        "site": site,
                        'log_dir': config.nginx_log_dir,
                        "config": config,
                        "ssl": True,
                    }))
        self.write(self.config_path, "\n".join(configfile))


class ApacheRequest(Service):
    def __init__(self, user, machine):
        super(ApacheRequest, self).__init__(user, machine, config.apache_init_script)

        self.config_path = config.apache_conf


    def mod_vhosts(self):
        configfile = []
        sites = UserSite.objects.filter(owner__parms__enable=True)
        for site in sites:
            if not site.main_domain.enable: continue
            if site.type in ("uwsgi", "modwsgi"):
                # Nginx mode cancel handling wsgi by Apache
                if "nginx" in config.mode and site.type == "uwsgi": continue

                configfile.append(render_to_string("apache_vhost_wsgi.conf", {
                    "listen": config.apache_url,
                    "site": site,
                    'log_dir': config.apache_log_dir,
                }))
            else:
                if "nginx" in config.mode and site.type == "static": continue
                configfile.append(render_to_string("apache_vhost_%s.conf" % site.type, {
                    "listen": config.apache_url,
                    "site": site,
                    'log_dir': config.apache_log_dir,
                }))
        self.write(self.config_path, "\n".join(configfile))


class BindRequest(Service):

    def __init__(self, user, ns="master"):
        self.ns = ns

        try:
            machine = Machine.objects.get(ip=getattr(config, "dns_%s" % self.ns))
        except Machine.DoesNotExist:
            raise RequestException("Error: NS machine not found")

        super(BindRequest, self).__init__(user, machine, config.bind_init_script)

    def mod_zone(self, domain):
        date_now = date.today()
        num = 0
        if len(str(domain.serial)) == 10 and str(domain.serial)[0:8] == "%.4d%.2d%.2d" % (date_now.year,date_now.month,date_now.day):
            ye  = int(str(domain.serial)[0:4])
            mo  = int(str(domain.serial)[4:6])
            da  = int(str(domain.serial)[6:8])
            num = int(str(domain.serial)[8:10])

            if date_now == date(ye, mo, da):
                num += 1

        serial = int("%.4d%.2d%.2d%.2d"%(date_now.year,date_now.month,date_now.day,num))

        configfile = render_to_string("bind_zone.conf", {
            "serial": serial,
            "domain": domain,
            "config": config,
            })
        self.write(config.bind_zone_conf % domain.domain_name, configfile)

    def remove_zone(self, domain):
        self.unlink(config.bind_zone_conf % domain.domain_name)
        self.mod_config()

    def mod_config(self):
        if self.ns == "master":
            tmpl = "bind_primary.conf"
        else:
            tmpl = "bind_secondary.conf"
            
        configfile = render_to_string(tmpl, {
            "domains": Domain.objects.filter(dns=True),
            "config": config,
            })
        self.write(config.bind_conf, configfile)


class EMailRequest(SSHHandler):
    def create_mailbox(self, email):
        homedir = join(config.maildir, email.domain.domain_name)
        maildir = join(homedir, email.login)

        self.run("mkdir -p %s" % homedir)
        self.run("chown email:email %s -R" % homedir)
        self.run("maildirmake %s" % maildir)
        self.run("chown email:email %s -R" % maildir)
        self.run("maildirmake %s" % join(maildir, '.Spam'))
        self.run("chown email:email %s -R" % join(maildir, 'Spam'))

    def remove_mailbox(self, email):
        #TODO - check if delete isn't nasty
        maildir = join(config.maildir, email.domain.domain_name, email.login)
        self.run("rm -rf %s" % maildir, plan_to=datetime.today() + timedelta(90))


class PostgreSQLRequest(SSHHandler):

    def add_db(self, db, password):
        self.run("createuser -D -R -S %s" % db, instant=True)
        self.run("createdb -O %s %s" % (db, db))
        self.passwd_db(db, password)

    def remove_db(self, db):
        self.run("dropdb %s" % db)
        self.run("dropuser %s" % db)

    def passwd_db(self, db, password):
        sql = "ALTER USER %s WITH PASSWORD '%s';" % (db, password)
        self.run("psql template1", stdin=sql, wipe=True, instant=True)


class MySQLRequest(SSHHandler):

    _default_cmd = settings.DEFAULT_MYSQL_COMMAND

    def add_db(self, db, password):
        self.run(stdin="CREATE DATABASE %s;" % db, instant=True)
        self.run(stdin="CREATE USER '%s'@'%s' IDENTIFIED BY '%s';" % (db, config.mysql_bind, password), wipe=True, instant=True)
        self.run(stdin="GRANT ALL PRIVILEGES ON %s.* TO '%s'@'localhost' WITH GRANT OPTION;" % (db, db), instant=True)
        self.passwd_db(db, password)

    def remove_db(self, db):
        self.run(stdin="DROP DATABASE %s;" % db)
        self.run(stdin="DROP USER '%s'@'localhost';" % db)

    def passwd_db(self, db, password):
        #TODO - escapovani (via django?)
        self.run(stdin="UPDATE mysql.user SET Password=PASSWORD('%s') WHERE User = '%s';" % (password, db), wipe=True, instant=True)
        self.run(stdin="FLUSH PRIVILEGES;", instant=True)


class SystemRequest(SSHHandler):
    def install(self, user):
        HOME = join("/home", user.username)

        self.run("useradd -m -s /bin/bash %s" % user.username)
        self.run("chmod 750 %s " % HOME)
        #TODO:This three lines needs more love - consider fastcgi_wrapper_dir killing, it's useless
        self.run("mkdir -p /var/www/%s" % user.username)
        self.run("cp %s %s" % ( join(settings.ROOT, 'service/www_data/php5_wrap'), config.fastcgi_wrapper_dir % user.username))
        self.run("chmod 755 %s" % (config.fastcgi_wrapper_dir % user.username))
        self.run("chown -R %(user)s:%(user)s /var/www/%(user)s" % dict(user=user.username))
        self.run("usermod -G %s -a %s" % (user.username, config.apache_user))
        self.run("usermod -G %s -a %s" % (config.apache_user, user.username))
        self.run("usermod -G clients -a %s" % user.username)
        self.run("su %s -c\'mkdir -p %s\'" % (user.username, join(HOME, settings.VIRTUALENVS_DIR)))
        self.run("su %s -c\'virtualenv %s\'" % (user.username, join(HOME, settings.VIRTUALENVS_DIR, 'default')))
        self.run("su %s -c\'mkdir %s\'" % (user.username, join(HOME, 'uwsgi')))

    def passwd(self, password):
        self.run("/usr/sbin/chpasswd", stdin="%s:%s" % (self.user.username, password), wipe=True, instant=True)

    def cron(self, user):
        """Crontab regeneration
        """
        cron_str = []
        update_cmd = "su %s -c 'crontab -'"
        clean_cmd = "su %s -c 'crontab -r'"

        for record in user.cron_set.all():
            cron_str.append("%s %s" % (record.cron_config, record.script))

        self.run(clean_cmd % user.username)
        self.run(update_cmd % user.username, stdin="\n".join(cron_str))
