import json
from django.conf import settings
import os
import re
from wsgiadmin.apps.models import App, Log
from wsgiadmin.apps.tools import Script


class AppException(Exception): pass


class AppObject(App):

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(AppObject, self).__init__(*args, **kwargs)
        self.script = Script(self.server.hostname)

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
                "domains": " ".join(self.domains_list)
            }
        )
        return parms

    def install(self):
        parms = self.get_parmameters()
        self.script.add_cmd("/usr/sbin/groupadd %(group)s" % parms)
        self.script.add_cmd("/usr/sbin/useradd -m -d %(home)s -g %(group)s %(user)s -s /bin/bash" % parms)
        self.script.add_cmd("/usr/sbin/usermod -G %s(group)s www-data" % parms)
        self.script.add_cmd("mkdir -p %(home)s/logs" % parms, user=self.get_user())
        self.script.add_cmd("mkdir -p %(home)s/app" % parms, user=self.get_user())
        self.script.add_cmd("mkdir -p %(home)s/.ssh" % parms, user=self.get_user())
        self.script.add_cmd("chmod 750 %(home)s" % parms)
        self.installed = True
        self.save()

    def commit(self):
        self.script.commit()

    def disable(self):
        parms = self.get_parmameters()
        self.script.add_cmd("chmod 000 %(home)s" % parms, user=self.get_user())

    def enable(self):
        parms = self.get_parmameters()
        self.script.add_cmd("chmod 750 %(home)s" % parms, user=self.get_user())

    def uninstall(self):
        parms = self.get_parmameters()
        self.script.add_cmd("/usr/sbin/userdel %(user)s" % parms)
        #self.script.add_cmd("/usr/sbin/groupdel %(group)s" % parms)
        self.script.add_cmd("rm -rf %(home)s" % parms)
        self.script.add_cmd("rm /etc/security/limits.d/%(user)s.conf" % parms)

    def update(self):
        parms = self.get_parmameters()
        limits = "%(user)s         hard    nproc           64\n"
        limits += "%(user)s         hard    as          262144\n"
        self.script.add_file("/etc/security/limits.d/%(user)s.conf" % parms, limits)

    def get_logs(self):
        parms = self.get_parmameters()
        logfiles = []
        for logfile in self.script.run("ls \"%(home)s/logs/\"" % parms)["stdout"].split():
            if re.match(".*\.log$", logfile):
                path = os.path.join("%(home)s/logs/" % parms, logfile.strip())
                logfiles.append((path, self.script.run("tail -n 60 %s" % path)["stdout"]))
        return logfiles

    def passwd(self, password):
        self.script.add_cmd("/usr/sbin/chpasswd", stdin="%s:%s" % (self.get_user(), password))


class PythonApp(AppObject):

    class Meta:
        proxy = True

    def get_parmameters(self):
        parms = super(PythonApp, self).get_parmameters()
        parms["virtualenv_cmd"] = settings.PYTHON_INTERPRETERS.get(parms.get("python", "python2.7"))
        return parms

    def install(self):
        super(PythonApp, self).install()
        parms = self.get_parmameters()
        self.script.add_cmd("cd; %(virtualenv_cmd)s %(home)s/venv" % parms, user=self.get_user())

    def disable(self):
        super(PythonApp, self).disable()
        parms = self.get_parmameters()
        self.stop()
        self.script.add_cmd("rm /etc/nginx/apps.d/%(user)s.conf" % parms)
        self.script.reload_nginx()
        self.disabled = True
        self.save()

    def enable(self):
        super(PythonApp, self).enable()

    def uninstall(self):
        super(PythonApp, self).uninstall()
        parms = self.get_parmameters()
        self.stop()
        self.script.add_cmd("rm /etc/supervisor/conf.d/%(user)s.conf" % parms)
        self.script.add_cmd("rm /etc/nginx/apps.d/%(user)s.conf" % parms)

    def update(self):
        super(PythonApp, self).update()
        parms = self.get_parmameters()
        self.script.add_file("%(home)s/requirements.txt" % parms, "uwsgi\n" + parms.get("virtualenv"), owner="%(user)s:%(group)s" % parms)
        self.script.add_cmd("%(home)s/venv/bin/pip install -r %(home)s/requirements.txt" % parms, user=self.get_user())
        self.script.add_file("%(home)s/requirements.txt" % parms, "uwsgi\n" + parms.get("virtualenv"), owner="%(user)s:%(group)s" % parms)
        self.script.add_file("%(home)s/app.wsgi" % parms, parms.get("virtualenv"), owner="%(user)s:%(group)s" % parms)
        self.script.add_file("/etc/supervisor/conf.d/%(user)s.conf" % parms, self.gen_supervisor_config())
        self.script.add_file("/etc/nginx/apps.d/%(user)s.conf" % parms, self.gen_nginx_config())
        self.script.reload_nginx()

    def gen_supervisor_config(self):
        parms = self.get_parmameters()
        config = []
        config.append("[program:%(user)s]" % parms)
        config.append(("command=%(home)s/venv/bin/uwsgi " % parms) + self.gen_uwsgi_parms())
        config.append("directory=%(home)s/app" % parms)
        config.append("process_name=%(user)s" % parms)
        config.append("user=%(user)s" % parms)
        config.append("group=%(group)s" % parms)
        config.append("stdout_logfile=%(home)s/logs/stdout.log" % parms)
        config.append("stdout_logfile_maxbytes=2MB")
        config.append("stdout_logfile_backups=5")
        config.append("stdout_capture_maxbytes=2MB")
        config.append("stdout_events_enabled=false")
        config.append("stderr_logfile=%(home)s/logs/stderr.log" % parms)
        config.append("stderr_logfile_maxbytes=2MB")
        config.append("stderr_logfile_backups=5")
        config.append("stderr_capture_maxbytes=2MB")
        config.append("stderr_events_enabled=false\n")
        return "\n".join(config)

    def gen_uwsgi_parms(self):
        parms = self.get_parmameters()
        config = []
        config.append("--master")
        config.append("--no-orphans")
        config.append("--processes %s" % parms.get("procs", "2"))
        config.append("--home %(home)s/venv")
        config.append("--limit-as 256")
        config.append("--chmod-socket=660")
        config.append("--uid %(user)s")
        config.append("--gid %(group)s")
        config.append("--pidfile %(home)s/app.pid")
        config.append("--socket %(home)s/app.sock")
        config.append("--wsgi-file %(home)s/app.wsgi")
        config.append("--daemonize %(home)s/logs/uwsgi.log")
        config.append("--chdir %(home)s")
        config.append("--pythonpath %(home)s/app")
        return " ".join(config)

    def gen_nginx_config(self):
        parms = self.get_parmameters()
        config = []
        config.append("server {")
        config.append("\tlisten       [::]:80;")
        config.append("\tserver_name  %(domains)s;" % parms)
        config.append("\taccess_log %(home)s/logs/access.log;"% parms)
        config.append("\terror_log %(home)s/logs/error.log;"% parms)
        config.append("\tlocation / {")
        config.append("\t\tuwsgi_pass unix://%(home)s/app.sock;"% parms)
        config.append("\t\tinclude        uwsgi_params;")
        config.append("\t}")
        if parms.get("static_maps"):
            for location, directory in [(x.split()[0].strip(), x.split()[1].strip()) for x in parms.get("static_maps").split("\n") if len(x.split()) == 2]:
                if re.match("/[a-zA-Z0-9_\-\.]*/", location) and re.match("/[a-zA-Z0-9_\-\.]*/", directory):
                    config.append("\tlocation %s {" % location)
                    config.append("\t\talias %s;" % os.path.join(parms.get("home"), "app", directory))
                    config.append("\t}")
        config.append("}\n")
        return "\n".join(config)

    def start(self):
        parms = self.get_parmameters()
        self.script.add_cmd("supervisorctl reread")
        self.script.add_cmd("supervisorctl update")
        self.script.add_cmd("supervisorctl start %(user)s" % parms)

    def restart(self):
        parms = self.get_parmameters()
        self.script.add_cmd("supervisorctl reread")
        self.script.add_cmd("supervisorctl update")
        self.script.add_cmd("supervisorctl restart %(user)s" % parms)

    def stop(self):
        parms = self.get_parmameters()
        self.script.add_cmd("supervisorctl stop %(user)s" % parms)
