import json
from django.conf import settings
import os
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
                "domains": self.domains_list
            }
        )
        return parms

    def install(self):
        parms = self.get_parmameters()
        self.script.add_cmd("/usr/sbin/groupadd %(group)s" % parms)
        self.script.add_cmd("/usr/sbin/useradd -m -d %(home)s -g %(group)s %(user)s" % parms)
        self.script.add_cmd("/usr/sbin/usermod -G %s(group)s www-data" % parms)
        self.script.add_cmd("mkdir -p %(home)s/logs" % parms, user=self.get_user())
        self.script.add_cmd("mkdir -p %(home)s/app" % parms, user=self.get_user())
        self.script.add_cmd("mkdir -p %(home)s/.ssh" % parms, user=self.get_user())
        self.script.add_cmd("chmod 750 %(home)s" % parms, user=self.get_user())
        self.installed = True
        self.save()


    def uninstall(self):
        parms = self.get_parmameters()
        self.script.add_cmd("/usr/sbin/userdel %(user)s" % parms)
        #self.script.add_cmd("/usr/sbin/groupdel %(group)s" % parms)
        self.script.add_cmd("rm -rf %(home)s" % parms)

    def update(self):
        limits = "%(user)s         hard    nproc           64\n"
        limits += "%(user)s         hard    as          262144\n"
        self.script.add_file("/etc/security/limits.d/%(user)s.conf", limits)


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
        self.script.add_cmd("%(virtualenv_cmd)s --no-site-packages %(home)s/venv" % parms, user=self.get_user())

    def uninstall(self):
        super(PythonApp, self).uninstall()

    def update(self):
        super(PythonApp, self).update()
        parms = self.get_parmameters()
        self.script.add_file("%(home)s/requirements.txt" % parms, "uwsgi\n" + parms.get("virtualenv"), owner="%(user)s:%(group)s" % parms)
        self.script.add_cmd("%(home)s/venv/bin/pip install -r %(home)s/requirements.txt" % parms, user=self.get_user())
        self.script.add_file("%(home)s/requirements.txt" % parms, "uwsgi\n" + parms.get("virtualenv"), owner="%(user)s:%(group)s" % parms)
        self.script.add_file("%(home)s/app.wsgi" % parms, parms.get("virtualenv"), owner="%(user)s:%(group)s" % parms)
        self.script.add_file("/etc/supervisor/conf.d/%(user)s.conf" % parms, self.gen_supervisor_config())


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
        config.append("stderr_events_enabled=false")
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
        return " ".join(config)

    def commit(self):
        message = self.script.commit()
        log = Log()
        log.app = self
        log.content = json.dumps(message)
        log.save()

    def start(self):
        pass

    def restart(self):
        pass

    def stop(self):
        pass