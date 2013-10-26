import os
import re
from django.conf import settings
from wsgiadmin.apps.backend.main import AppBackend
from wsgiadmin.core.exceptions import ScriptException


class PythonApp(AppBackend):

    class Meta:
        proxy = True

    def get_parmameters(self):
        parms = super(PythonApp, self).get_parmameters()
        interpreters = self.core_server.pythoninterpreter_set.filter(name=parms.get("python", "Python 2.7"))
        if len(interpreters) == 1:
            parms["virtualenv_cmd"] = interpreters[0].virtualenv
        else:
            raise ScriptException("Error: badly configured python interpreters on %s" % self.core_server.name)
        return parms

    def install(self):
        super(PythonApp, self).install()
        parms = self.get_parmameters()
        self.script.add_cmd("cd; %(virtualenv_cmd)s %(home)s/venv" % parms, user=self.get_user())
        self.script.add_cmd("tee -a %(home)s/.bashrc" % parms, user=self.get_user(), stdin="\n\nsource ~/venv/bin/activate")
        self.script.add_file("%(home)s/requirements.txt" % parms, "uwsgi\n" + parms.get("virtualenv"), owner="%(user)s:%(group)s" % parms)
        self.script.add_cmd("%(home)s/venv/bin/pip install -r %(home)s/requirements.txt" % parms, user=self.get_user())

    def disable(self):
        super(PythonApp, self).disable()
        parms = self.get_parmameters()
        self.stop()
        self.script.add_cmd("rm /etc/nginx/apps.d/%(user)s.conf" % parms)
        self.script.reload_nginx()

    def enable(self):
        super(PythonApp, self).enable()

    def uninstall(self):
        super(PythonApp, self).uninstall()
        parms = self.get_parmameters()
        self.stop()
        self.script.add_cmd("rm /etc/supervisor/apps.d/%(user)s.conf" % parms)
        self.script.add_cmd("rm /etc/nginx/apps.d/%(user)s.conf" % parms)
        self.script.add_cmd("supervisorctl reread")
        self.script.add_cmd("supervisorctl update")

    def update(self):
        super(PythonApp, self).update()
        parms = self.get_parmameters()
        self.script.add_file("%(home)s/requirements.txt" % parms, "uwsgi\n" + parms.get("virtualenv"), owner="%(user)s:%(group)s" % parms)
        self.script.add_file("%(home)s/app.wsgi" % parms, parms.get("script"), owner="%(user)s:%(group)s" % parms)
        self.script.add_file("/etc/supervisor/apps.d/%(user)s.conf" % parms, self.gen_supervisor_config())
        self.script.add_file("/etc/nginx/apps.d/%(user)s.conf" % parms, self.gen_nginx_config())
        self.script.reload_nginx()

    def gen_supervisor_config(self):
        parms = self.get_parmameters()
        content = []
        content.append("[program:%(user)s]" % parms)
        content.append(("command=%(home)s/venv/bin/uwsgi " % parms) + self.gen_uwsgi_parms())
        content.append("directory=%(home)s/app" % parms)
        content.append("process_name=%(user)s" % parms)
        content.append("user=%(user)s" % parms)
        content.append("group=%(group)s" % parms)
        content.append("stdout_logfile=%(home)s/logs/stdout.log" % parms)
        content.append("stdout_logfile_maxbytes=2MB")
        content.append("stdout_logfile_backups=5")
        content.append("stdout_capture_maxbytes=2MB")
        content.append("stdout_events_enabled=false")
        content.append("stderr_logfile=%(home)s/logs/stderr.log" % parms)
        content.append("stderr_logfile_maxbytes=2MB")
        content.append("stderr_logfile_backups=5")
        content.append("stderr_capture_maxbytes=2MB")
        content.append("stderr_events_enabled=false\n")
        return "\n".join(content)

    def gen_uwsgi_parms(self):
        parms = self.get_parmameters()
        content = []
        content.append("--master")
        content.append("--no-orphans")
        content.append("--processes %s" % parms.get("procs", "2"))
        content.append("--home %(home)s/venv" % parms)
        content.append("--limit-as %s" % parms.get("memory", "256"))
        content.append("--harakiri 600")
        content.append("--chmod-socket=660")
        content.append("--uid %(user)s" % parms)
        content.append("--gid %(group)s" % parms)
        content.append("--pidfile %(home)s/app.pid" % parms)
        content.append("--socket %(home)s/app.sock" % parms)
        content.append("--wsgi-file %(home)s/app.wsgi" % parms)
        content.append("--chdir %(home)s" % parms)
        content.append("--pythonpath %(home)s/app" % parms)
        content.append("--env PYTHON_EGG_CACHE=~/.python-eggs")
        return " ".join(content)

    def gen_nginx_config(self):
        parms = self.get_parmameters()
        content = []
        content.append("server {")
        if self.core_server.os in ("archlinux", ):
            content.append("\tlisten       *:80;")
        else:
            content.append("\tlisten       [::]:80;")
        content.append("\tserver_name  %(domains)s;" % parms)
        content.append("\taccess_log %(home)s/logs/access.log;"% parms)
        content.append("\terror_log %(home)s/logs/error.log;"% parms)
        content.append("\tlocation / {")
        content.append("\t\tuwsgi_pass unix://%(home)s/app.sock;"% parms)
        content.append("\t\tinclude        uwsgi_params;")
        content.append("\t}")
        if parms.get("static_maps"):
            for location, directory in [(x.split()[0].strip(), x.split()[1].strip()) for x in parms.get("static_maps").split("\n") if len(x.split()) == 2]:
                if re.match("/[a-zA-Z0-9_\-\.]*/", location) and re.match("/[a-zA-Z0-9_\-\.]*/", directory):
                    content.append("\tlocation %s {" % location)
                    content.append("\t\talias %s;" % os.path.join(parms.get("home"), "app", directory[1:]))
                    content.append("\t}")
        content.append("}\n")
        return "\n".join(content)

    def start(self):
        parms = self.get_parmameters()
        self.script.add_cmd("supervisorctl reread")
        self.script.add_cmd("supervisorctl update")
        # should be needed, but for sure in some cases
        self.script.add_cmd("supervisorctl start %(user)s" % parms)

    def restart(self):
        parms = self.get_parmameters()
        self.script.add_cmd("supervisorctl reread")
        self.script.add_cmd("supervisorctl update")
        self.script.add_cmd("supervisorctl restart %(user)s" % parms)

    def stop(self):
        parms = self.get_parmameters()
        self.script.add_cmd("supervisorctl stop %(user)s" % parms)


class PythonGunicornApp(PythonApp):

    def get_port(self):
        return settings.GUNICORN_PROXY_PORT + self.id

    def install(self):
        AppBackend.install(self)
        parms = self.get_parmameters()
        self.script.add_cmd("cd; %(virtualenv_cmd)s %(home)s/venv" % parms, user=self.get_user())
        self.script.add_cmd("tee -a %(home)s/.bashrc" % parms, user=self.get_user(), stdin="\n\nsource ~/venv/bin/activate")
        self.script.add_file("%(home)s/requirements.txt" % parms, "gunicorn\n" + parms.get("virtualenv"), owner="%(user)s:%(group)s" % parms)
        self.script.add_cmd("%(home)s/venv/bin/pip install -r %(home)s/requirements.txt" % parms, user=self.get_user())

    def update(self):
        AppBackend.update(self)
        parms = self.get_parmameters()
        self.script.add_file("%(home)s/requirements.txt" % parms, "gunicorn\n" + parms.get("virtualenv"), owner="%(user)s:%(group)s" % parms)
        self.script.add_file("%(home)s/app.py" % parms, parms.get("script"), owner="%(user)s:%(group)s" % parms)
        self.script.add_file("/etc/supervisor/apps.d/%(user)s.conf" % parms, self.gen_supervisor_config())
        self.script.add_file("/etc/nginx/apps.d/%(user)s.conf" % parms, self.gen_nginx_config())
        self.script.reload_nginx()

    def gen_gunicorn_parms(self):
        parms = self.get_parmameters()
        gunicorn = []
        gunicorn.append("-w %d" % parms.get("procs", "2"))
        gunicorn.append("-b 127.0.0.1:%d" % self.get_port())
        gunicorn.append("app")
        return " ".join(gunicorn)

    def gen_nginx_config(self):
        parms = self.get_parmameters()
        content = []
        content.append("server {")
        if self.core_server.os in ("archlinux", ):
            content.append("\tlisten       *:80;")
        else:
            content.append("\tlisten       [::]:80;")
        content.append("\tserver_name  %(domains)s;" % parms)
        content.append("\taccess_log %(home)s/logs/access.log;"% parms)
        content.append("\terror_log %(home)s/logs/error.log;"% parms)
        content.append("\tlocation / {")
        content.append("\t\tproxy_pass         http://127.0.0.1:%d/;" % self.get_port())
        content.append("\t\tproxy_redirect     off;")
        content.append("\t}")
        if parms.get("static_maps"):
            for location, directory in [(x.split()[0].strip(), x.split()[1].strip()) for x in parms.get("static_maps").split("\n") if len(x.split()) == 2]:
                if re.match("/[a-zA-Z0-9_\-\.]*/", location) and re.match("/[a-zA-Z0-9_\-\.]*/", directory):
                    content.append("\tlocation %s {" % location)
                    content.append("\t\talias %s;" % os.path.join(parms.get("home"), "app", directory[1:]))
                    content.append("\t}")
        content.append("}\n")
        return "\n".join(content)

    def gen_supervisor_config(self):
        parms = self.get_parmameters()
        content = []
        content.append("[program:%(user)s]" % parms)
        content.append("command=%(home)s/venv/bin/gunicorn " + self.gen_uwsgi_parms())
        content.append("directory=%(home)s/app" % parms)
        content.append("process_name=%(user)s" % parms)
        content.append("user=%(user)s" % parms)
        content.append("group=%(group)s" % parms)
        content.append("stdout_logfile=%(home)s/logs/stdout.log" % parms)
        content.append("stdout_logfile_maxbytes=2MB")
        content.append("stdout_logfile_backups=5")
        content.append("stdout_capture_maxbytes=2MB")
        content.append("stdout_events_enabled=false")
        content.append("stderr_logfile=%(home)s/logs/stderr.log" % parms)
        content.append("stderr_logfile_maxbytes=2MB")
        content.append("stderr_logfile_backups=5")
        content.append("stderr_capture_maxbytes=2MB")
        content.append("stderr_events_enabled=false\n")
        return "\n".join(content)