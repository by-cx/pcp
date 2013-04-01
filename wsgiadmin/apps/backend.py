import json
from django.conf import settings
import os
import re
from wsgiadmin.apps.models import App, Db
from constance import config
from wsgiadmin.core.backend_base import Script


class AppException(Exception): pass


class AppBackend(App):

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(AppBackend, self).__init__(*args, **kwargs)
        self.script = Script(self.core_server)

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

    def commit(self, no_thread=False):
        self.script.commit(no_thread)

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
        limits += "%(user)s         hard    as          393216\n"
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


class PHPApp(AppBackend):
    class Meta:
        proxy = True

    def install(self):
        super(PHPApp, self).install()
        parms = self.get_parmameters()
        self.script.add_cmd("mkdir -p %(home)s/fcgid" % parms, user=self.get_user())
        self.script.add_cmd("mkdir -p /var/www/%(user)s/" % parms)
        self.script.add_cmd("chown %(user)s:%(group)s /var/www/%(user)s/" % parms)

    def disable(self):
        super(PHPApp, self).disable()
        parms = self.get_parmameters()
        self.script.add_cmd("rm /etc/apache2/apps.d/%(user)s.conf" % parms)
        self.script.add_cmd("rm /etc/nginx/apps.d/%(user)s.conf" % parms)
        self.script.reload_apache()
        self.script.reload_nginx()
        self.disabled = True
        self.save()

    def enable(self):
        super(PHPApp, self).enable()

    def uninstall(self):
        super(PHPApp, self).uninstall()
        parms = self.get_parmameters()
        self.script.add_cmd("rm /etc/apache2/apps.d/%(user)s.conf" % parms)
        self.script.add_cmd("rm /etc/nginx/apps.d/%(user)s.conf" % parms)
        self.script.add_cmd("rm /var/www/%(user)s/ -r" % parms)
        self.script.reload_apache()
        self.script.reload_nginx()

    def update(self):
        super(PHPApp, self).update()
        parms = self.get_parmameters()
        self.script.add_file("/etc/apache2/apps.d/%(user)s.conf" % parms, self.gen_apache_config())
        self.script.add_file("/etc/nginx/apps.d/%(user)s.conf" % parms, self.gen_nginx_config())
        self.script.add_file("/var/www/%(user)s/php-wrap" % parms, self.gen_php_wrap(), owner=self.get_user())
        self.script.add_file("/var/www/%(user)s/php.ini" % parms, self.gen_php_ini(), owner=self.get_user())
        self.script.add_cmd("chmod 555 /var/www/%(user)s/php-wrap" % parms)
        self.script.add_cmd("chown %(user)s:%(group)s /var/www/%(user)s/php-wrap" % parms)
        self.script.add_cmd("chmod 444 /var/www/%(user)s/php.ini" % parms)
        self.script.add_cmd("chown %(user)s:%(group)s /var/www/%(user)s/php.ini" % parms)
        self.script.reload_nginx()
        self.script.reload_apache()

    def gen_php_wrap(self):
        parms = self.get_parmameters()
        content = []
        content.append("#!/bin/sh")
        content.append("PHP_FCGI_CHILDREN=2")
        content.append("export PHP_FCGI_CHILDREN")
        content.append("PHP_FCGI_MAX_REQUESTS=400")
        content.append("export PHP_FCGI_MAX_REQUESTS")
        content.append("PHPRC=/var/www/%(user)s/php.ini" % parms)
        content.append("export PHPRC")
        content.append("exec /usr/bin/php-cgi\n")
        return "\n".join(content)

    def gen_php_ini(self):
        parms = self.get_parmameters()
        content = []
        content.append("%s" % self.script.run("cat /etc/php5/cgi/php.ini")["stdout"])
        content.append("error_log = %(home)s/logs/php.log" % parms)
        content.append("memory_limit = %s" % parms.get("memory_limit", "32M"))
        content.append("post_max_size = %s" % parms.get("post_max_size", "32M"))
        content.append("upload_max_filesize = %s" % parms.get("upload_max_filesize", "10"))
        content.append("max_file_uploads = %s" % parms.get("max_file_uploads", "10"))
        content.append("max_execution_time = %s" % parms.get("max_execution_time", "20"))
        content.append("allow_url_fopen = %s" % ("On" if parms.get("allow_url_fopen") else "Off"))
        content.append("display_errors = %s\n" % ("On" if parms.get("display_errors") else "Off"))
        return "\n".join(content)

    def gen_apache_config(self):
        parms = self.get_parmameters()
        content = []
        content.append("<VirtualHost %s>" % config.apache_url)
        content.append("\tSuexecUserGroup %(user)s %(group)s" % parms)
        content.append("\tServerName %(main_domain)s" % parms)
        if parms.get("misc_domains"):
            content.append("\tServerAlias %(misc_domains)s" % parms)
        content.append("\tDocumentRoot %(home)s/app/" % parms)
        content.append("\tCustomLog %(home)s/logs/access.log combined" % parms)
        content.append("\tErrorLog %(home)s/logs/error.log" % parms)
        content.append("\t<Directory %(home)s/app/>" % parms)
        content.append("\t\tOptions +ExecCGI %s" % "+Indexes" if parms.get("flag_index") else "")
        content.append("\t\tAllowOverride All")
        content.append("\t\tAddHandler fcgid-script .php")
        content.append("\t\tFCGIWrapper /var/www/%(user)s/php-wrap .php" % parms)
        content.append("\t\tOrder deny,allow")
        content.append("\t\tAllow from all")
        content.append("\t</Directory>")
        content.append("\tIPCCommTimeout 360")
        content.append("</VirtualHost>\n")
        return "\n".join(content)

    def gen_nginx_config(self):
        parms = self.get_parmameters()
        content = []
        content.append("server {")
        content.append("\tlisten       %s;" % config.nginx_listen)
        content.append("\tserver_name  %(domains)s;" % parms)
        content.append("\taccess_log %(home)s/logs/access.log;"% parms)
        content.append("\terror_log %(home)s/logs/error.log;"% parms)
        content.append("\tlocation / {")
        content.append("\t\tproxy_pass         http://%s/;" % config.apache_url)
        content.append("\t\tproxy_redirect     off;")
        content.append("\t}")
        content.append("}\n")
        return "\n".join(content)


class StaticApp(AppBackend):

    class Meta:
        proxy = True

    def disable(self):
        super(StaticApp, self).disable()
        parms = self.get_parmameters()
        self.script.add_cmd("rm /etc/nginx/apps.d/%(user)s.conf" % parms)
        self.script.reload_nginx()
        self.disabled = True
        self.save()

    def enable(self):
        super(StaticApp, self).enable()

    def uninstall(self):
        super(StaticApp, self).uninstall()
        parms = self.get_parmameters()
        self.script.add_cmd("rm /etc/nginx/apps.d/%(user)s.conf" % parms)
        self.script.reload_nginx()

    def update(self):
        super(StaticApp, self).update()
        parms = self.get_parmameters()
        self.script.add_file("/etc/nginx/apps.d/%(user)s.conf" % parms, self.gen_nginx_config())
        self.script.reload_nginx()

    def gen_nginx_config(self):
        parms = self.get_parmameters()
        content = []
        content.append("server {")
        content.append("\tlisten       %s;" % config.nginx_listen)
        content.append("\tserver_name  %(domains)s;" % parms)
        content.append("\taccess_log %(home)s/logs/access.log;"% parms)
        content.append("\terror_log %(home)s/logs/error.log;"% parms)
        content.append("\troot %(home)s/app;"% parms)
        if parms.get("flag_index"):
            content.append("\tautoindex on;")
        else:
            content.append("\tautoindex off;")
        content.append("\tindex index.html index.htm default.html default.htm;")
        content.append("}\n")
        return "\n".join(content)


class PythonApp(AppBackend):

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
        self.script.add_cmd("rm /etc/supervisor/apps.d/%(user)s.conf" % parms)
        self.script.add_cmd("rm /etc/nginx/apps.d/%(user)s.conf" % parms)
        self.script.add_cmd("supervisorctl reread")
        self.script.add_cmd("supervisorctl update")

    def update(self):
        super(PythonApp, self).update()
        parms = self.get_parmameters()
        self.script.add_file("%(home)s/requirements.txt" % parms, "uwsgi\n" + parms.get("virtualenv"), owner="%(user)s:%(group)s" % parms)
        self.script.add_cmd("%(home)s/venv/bin/pip install -r %(home)s/requirements.txt" % parms, user=self.get_user())
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
        content.append("--limit-as 256")
        content.append("--chmod-socket=660")
        content.append("--uid %(user)s" % parms)
        content.append("--gid %(group)s" % parms)
        content.append("--pidfile %(home)s/app.pid" % parms)
        content.append("--socket %(home)s/app.sock" % parms)
        content.append("--wsgi-file %(home)s/app.wsgi" % parms)
        content.append("--chdir %(home)s" % parms)
        content.append("--pythonpath %(home)s/app" % parms)
        return " ".join(content)

    def gen_nginx_config(self):
        parms = self.get_parmameters()
        content = []
        content.append("server {")
        content.append("\tlisten       %s;" % config.nginx_listen)
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
        self.script.add_cmd("supervisorctl start %(user)s" % parms)

    def restart(self):
        parms = self.get_parmameters()
        self.script.add_cmd("supervisorctl reread")
        self.script.add_cmd("supervisorctl update")
        self.script.add_cmd("supervisorctl restart %(user)s" % parms)

    def stop(self):
        parms = self.get_parmameters()
        self.script.add_cmd("supervisorctl stop %(user)s" % parms)


class DbObject(Db):

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(DbObject, self).__init__(*args, **kwargs)
        if self.db_type == "mysql":
            self.script = self.script = Script(config.mysql_server)
        elif self.db_type == "pgsql":
            self.script = self.script = Script(config.pgsql_server)

    def install(self):
        if self.db_type == "mysql":
            self.script.add_cmd("mysql -u root", stdin="CREATE DATABASE %s;" % self.name)
            self.script.add_cmd("mysql -u root", stdin="CREATE USER '%s'@'%%' IDENTIFIED BY '%s';" % (self.name, self.password))
            self.script.add_cmd("mysql -u root", stdin="GRANT ALL PRIVILEGES ON %s.* TO '%s'@'%%' WITH GRANT OPTION;" % (self.name, self.name))
        elif self.db_type == "pgsql":
            self.script.add_cmd("createuser -D -R -S %s" % self.name)
            self.script.add_cmd("createdb -O %s %s" % (self.name, self.name))

    def passwd(self, password):
        if self.db_type == "mysql":
            self.script.add_cmd("mysql -u root", stdin="UPDATE mysql.user SET Password=PASSWORD('%s') WHERE User = '%s';" % (password, self.name))
            self.script.add_cmd("mysql -u root", stdin="FLUSH PRIVILEGES;")
        elif self.db_type == "pgsql":
            sql = "ALTER USER %s WITH PASSWORD '%s';" % (self.name, password)
            self.script.add_cmd("psql template1", stdin=sql)

    def uninstall(self):
        if self.db_type == "mysql":
            self.script.add_cmd("mysql -u root", stdin="DROP DATABASE %s;" % self.name)
        elif self.db_type == "pgsql":
            self.script.add_cmd("dropdb %s" % self.name)
            self.script.add_cmd("dropuser %s" % self.name)

    def commit(self, no_thread=False):
        self.script.commit(no_thread)


def typed_object(app):
    if app.app_type == "python":
        app = PythonApp.objects.get(id=app.id)
    elif app.app_type == "php":
        app = PHPApp.objects.get(id=app.id)
    elif app.app_type == "static":
        app = StaticApp.objects.get(id=app.id)
    else:
        app = AppBackend.objects.get(id=app.id)
    return app
