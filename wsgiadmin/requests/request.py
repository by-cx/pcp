# -*- coding: utf-8 -*-

from django.conf import settings
import subprocess, shlex, datetime, json
from wsgiadmin.requests.models import Request

class RequestException(Exception): pass

class SSHHandler(object):
	def __init__(self, machine, user):
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

class JSONRPCHandler(object): pass

class Service(settings.HANDLER):
	def __init__(self, init_script):
		self.init_script = init_script

	def state(self):
		"""Return state of service. True for running, False for oposite."""

	def start(self):
		"""Start service"""

	def stop(self):
		"""Stop service"""

	def restart(self):
		"""Restart service"""

	def reload(self):
		"""Reload service"""

class UWSGIRequest(settings.HANDLER):
	"""uwsgi_config
	uwsgi_start
	uwsgi_restart
	uwsgi_stop
	uwsgi_reload"""

class NginxRequest(Service):
	def modVHost(self, site):
		pass

class ApacheRequest(Service):
	def modVHost(self, site):
		pass

class BindRequest(settings.HANDLER):
	def __init__(self, domain):
		self.domain = domain

	def _zoneFileName(self):
		pass

	def modZone(self, zone): pass
	
	def removeZone(self): pass

	def modConfig(self): pass

class EMailRequest(settings.HANDLER):
	def __init__(self, email):
		self.email = email

	def CreateMailbox(self):
		pass

class PostgreSQLRequest(settings.HANDLER):
	def __init__(self, db):
		self.db = db

	def addDb(self):
		pass

	def removeDb(self):
		pass

	def passwdDb(self, password):
		pass

class MySQLRequest(settings.HANDLER):
	def __init__(self, db):
		self.db = db

	def addDb(self):
		pass

	def removeDb(self):
		pass

	def passwdDb(self, password):
		pass

class PAMRequest(settings.HANDLER):
	def __init__(self, user):
		self.user = user

	def passwd(self, password):
		pass
