# -*- coding: utf-8 -*-

import subprocess, shlex, datetime, json
from django.template.loader import render_to_string
from wsgiadmin.apacheconf.models import Site
from wsgiadmin.domains.models import Domain
from wsgiadmin.requests.models import Request
from django.conf import settings

class RequestException(Exception): pass

class SSHHandler(object):
	def __init__(self, user, machine):
		self.machine = machine
		self.user = user

	def _serverName(self):
		return self.machine.name

	def _run(self, cmd, stdin=None):
		cmd = "ssh %s %s" % (self._serverName(), cmd)

		subprocess.POpen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout, stderr = subprocess.communicate(stdin)
		return stdout, stderr

	def _write(self, filename, content):
		cmd = "tee %s" % filename

		stdout, stderr = self._run(cmd, stdin=content)

		return stdout, stderr

	def _unlink(self, filename):
		cmd = "rm %s" % filename

		stdout, stderr = self._run(cmd)

		return stdout, stderr

	def run(self, cmd, stdin=None):
		r = Request()

		r.action = "run"
		r.data = json.dumps({"action": "run", "server": self._serverName(), "cmd": cmd, "stdin": stdin})
		r.user = self.user
		r.save()

	def instantRun(self, cmd, stdin=None):
		r = Request()

		r.action = "run"
		r.data = json.dumps({"action": "run", "server": self._serverName(), "cmd": cmd, "stdin": stdin})
		r.user = self.user
		r.save()

		stdout, stderr = self._run(cmd, stdin)

		r.done_date = datetime.datetime.today()
		r.done = True
		r.stdout = stdout
		r.stderr = stderr

		r.save()

		return stdout, stderr

	def write(self, filename, content):
		r = Request()

		r.action = "write"
		r.data = json.dumps({"action": "write", "server": self._serverName(), "filename": filename, "content": content})
		r.user = self.user
		r.save()

	def unlink(self, filename):
		r = Request()

		r.action = "unlink"
		r.data = json.dumps({"action": "unlink", "server": self._serverName(), "filename": filename})
		r.user = self.user
		r.save()

	def read(self, filename):
		cmd = "cat %s" % filename
		
		r = Request()

		r.action = "read"
		r.data = json.dumps({"action": "read", "server": self._serverName(), "cmd": cmd})
		r.user = self.user
		r.save()

		stdout, stderr = self._run(cmd)

		r.done_date = datetime.datetime.today()
		r.done = True
		r.stdout = stdout
		r.stderr = stderr

		r.save()

		return stdout

	def isfile(self, filename):
		cmd = "if [ `ls %s 2> /dev/null` ]; then echo 1; fi;" % filename

		r = Request()

		r.action = "read"
		r.data = json.dumps({"action": "isfile", "server": self._serverName(), "cmd": cmd})
		r.user = self.user
		r.save()

		stdout, stderr = self._run(cmd)

		r.done_date = datetime.datetime.today()
		r.done = True
		r.stdout = stdout
		r.stderr = stderr

		r.save()

		if stdout.strip() == "1":
			return True
		else:
			return False

	def commit(self):
		for request in Request.objects.filter(done=False).order_by("add_date"):
			data = json.loads(request.data)
			ret = None

			if request.action == "run":
				ret = self._run(data["cmd"])
			elif request.action == "write":
				ret = self._write(data["filename"], data["content"])
			elif request["action"] == "unlink":
				ret = self._unlink(data["filename"])

			if ret:
				request.done_date = datetime.datetime.today()
				request.done = True
				request.stdout = ret[0]
				request.stderr = ret[1]

				request.save()

#class JSONRPCHandler(object): pass

class Service(settings.HANDLER):
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

class UWSGIRequest(settings.HANDLER):
	def start(self, site):
		self.run("/usr/bin/uwsgi-manager.py -s %s" % str(site.id))
	def restart(self, site):
		self.run("/usr/bin/uwsgi-manager.py -R %s" % str(site.id))
	def stop(self, site):
		self.run("/usr/bin/uwsgi-manager.py -S %s" % str(site.id))
	def reload(self, site):
		self.run("/usr/bin/uwsgi-manager.py -r %s" % str(site.id))

class NginxRequest(Service):
	def modVHosts(self):
		config = []
		for site in Site.objects.filter(removed=False, owner__parms__enable=True):
			if site.type == "uwsgi" or site.type == "modwsgi":
				config.append(render_to_string("nginx_vhost_wsgi.conf", {
					"site": site
				}))
			elif site.type == "php":
				# PHP always throw Apache
				config.append(render_to_string("nginx_vhost_proxy.conf" % site.type, {
					"site": site
				}))
			elif site.type == "static":
				config.append(render_to_string("nginx_vhost_static.conf" % site.type, {
					"site": site
				}))
		self.write(settings.PCP_SETTINGS["nginx_conf"], "\n".join(config))

class ApacheRequest(Service):
	def modVHosts(self):
		config = []
		for site in Site.objects.filter(removed=False, owner__parms__enable=True):
			if site.type == "uwsgi" or site.type == "modwsgi":
				# Nginx mode cancel handling wsgi by Apache
				if settings.PCP_SETTINGS["mode"] != "apache": continue
				
				config.append(render_to_string("apache_vhost_wsgi.conf", {
					"site": site
				}))
			else:
				config.append(render_to_string("apache_vhost_%s.conf" % site.type, {
					"site": site
				}))
		self.write(settings.PCP_SETTINGS["apache_conf"], "\n".join(config))

class BindRequest(Service):
	def modZone(self, domain):
		config =render_to_string("bind_zone.conf", {
			"domain": domain
		})
		self.write(settings.PCP_SETTINGS["bind_zone_conf"] % domain.name, config)
	
	def removeZone(self, domain):
		self.unlink(settings.PCP_SETTINGS["bind_zone_conf"] % domain.name)
		self.modConfig()

	def modConfig(self):
		config =render_to_string("bind.conf", {
			"domains": Domain.objects.all(),
		    "dns": settings.PCP_SETTINGS["dns"],
		})
		self.write(settings.PCP_SETTINGS["bind_conf"], config)

class EMailRequest(settings.HANDLER):
	def CreateMailbox(self, email):
		homedir = settings.PCP_SETTINGS["maildir"]+"/"+email.domain.name+"/"
		maildir = homedir+email.login+"/"

		self.run("/bin/mkdir -p %s" % homedir)
		self.run("/bin/chown email:email %s -R" % homedir)
		self.run("/usr/bin/maildirmake %s" % maildir)
		self.run("/bin/chown email:email %s -R" % maildir)
		self.run("/usr/bin/maildirmake %s" % maildir+".Spam")
		self.run("/bin/chown email:email %s -R" % maildir+"/Spam")

class PostgreSQLRequest(settings.HANDLER):
	def addDb(self, db, password):
		self.run("createuser -D -R -S %s" % db)
		self.run("createdb -O %s %s" % (db, db))
		
		self.passwdDb(db, password)

	def removeDb(self, db):
		self.run("dropdb %s" % db)
		self.run("dropuser %s" % db)

	def passwdDb(self, db, password):
		sql = "ALTER USER %s WITH PASSWORD '%s';" % (db, password)
		self.run("psql template1", stdin=sql)

class MySQLRequest(settings.HANDLER):
	def addDb(self, db, password):
		sql = []

		sql.append("CREATE DATABASE %s;" % db)
		sql.append("CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';" % (db, password))
		sql.append("GRANT ALL PRIVILEGES ON %s.* TO '%s'@'localhost' WITH GRANT OPTION;" % (db,db))

		for x in sql:
			self.run("mysql -u root", stdin=x)

	def removeDb(self, db):
		sql = []

		sql.append("DROP DATABASE %s;" % db)
		sql.append("DROP USER '%s'@'localhost';" % db)

		for x in sql:
			self.run("mysql -u root", stdin=x)

	def passwdDb(self, db, password):
		sql = []

		sql.append("UPDATE mysql.user SET Password = PASSWORD('%s') WHERE User = '%s';" % (password, db))
		sql.append("FLUSH PRIVILEGES;")

		for x in sql:
			self.run("mysql -u root", stdin=x)

class SystemRequest(settings.HANDLER):
	def install(self, user):
		pass

	def passwd(self, password):
		self.run("/usr/sbin/chpasswd", stdin= "%s:%s" % (self.user.username, password))
