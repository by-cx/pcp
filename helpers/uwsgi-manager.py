#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, shlex, time, errno, sys
from xml.etree.ElementTree import XMLParser
from subprocess import Popen, PIPE, call
from optparse import OptionParser

class manager:
	config_file = "/etc/uwsgi/config.xml"
	config_tree = None
	config = {}

	def __init__(self):
		f = open(self.config_file)
		xml_src = f.read()
		f.close()

		parser = XMLParser()
		parser.feed(xml_src)
		self.config_tree = parser.close()

		self.parse()

	def parse(self):
		for element in self.config_tree:
			web_id = int(element.get("id"))
			self.config[web_id] = {}
			for subelement in element:
				self.config[web_id][subelement.tag] = subelement.text

	############################
	## Process manipulation
	############################

	def run_cmd(self, cmd):
		return_code = call(shlex.split(cmd))

		if not return_code:
			return True
		else:
			print "Error: '%s' return %d" % (cmd, return_code)
			return False

	def send_signal(self, id, signal):
		if not os.path.isfile(self.config[id]["pidfile"]):
			return False
		try:
			os.kill(self.get_pid(id), signal)
		except OSError, err:
	 		if err.errno == errno.ESRCH:
				return False
	 		elif err.errno == errno.EPERM:
				print pid
	 			print "No permission to signal this process!"
				sys.exit(1)
	 		else:
				print pid
	 			print "Unknown error"
				sys.exit(1)
		else:
			return True


	def running_check(self, id):
		return self.send_signal(id, 0)

	def get_pid(self, id):
		f = open(self.config[id]["pidfile"])
		pid = int(f.read().strip())
		f.close()
		return pid

	def check_id(self, id):
		if not id in self.config:
			print "ID not found"
			sys.exit(1)

	#{'43': {'wsgi-file': '/home/cx/co/sexflirt/sexflirt.wsgi', 'processes': '1', 'uid': 'cx', 'pythonpath': '/home/cx/co/', 'limit-as': '48', 'chmod-socket': '660', 'gid': 'cx', 'master': None, 'home': '/home/cx/virtualenvs/default', 'optimize': '1', 'socket': '/home/cx/uwsgi/sexflirt.cz.sock'}}

	## Actions it selfs

	def start(self, id):
		self.check_id(id)
		if not self.running_check(id):
			cmd = "su %s -c 'uwsgi -x %s:%d'" % (self.config[id]["uid"], self.config_file, id)
			self.run_cmd(cmd)

	def startall(self):
		for web in self.config:
			self.start(web)

	def stop(self, id):
		self.check_id(id)
		if self.running_check(id):
			if not self.send_signal(id, 3): #QUIT signal
				print "Error"
		else:
			print "Error: app %d doesn't run" % id

	def stopall(self):
		for web in self.config:
			self.stop(web)
		
	def restart(self, id):
		self.check_id(id)
		if self.running_check(id):
			self.stop(id)
			time.sleep(2)
		if not self.running_check(id):
			self.start(id)

	def restartall(self):
		for web in self.config:
			self.restart(web)

	def reload(self, id):
		self.check_id(id)
		if self.running_check(id):
			return self.send_signal(id, 1)
		else:
			self.start(id)

	def brutal_reload(self, id):
		self.check_id(id)
		if self.running_check(id):
			return self.send_signal(id, 15)
		else:
			self.start(id)

	def brutal_reloadall(self):
		for web in self.config:
			self.brutal_reload(web)

	def check(self, id):
		self.check_id(id)
		if self.running_check(id):
			print "Aplikace běží"
		else:
			print "Aplikace neběží"

	def list(self):
		for app in self.config:
			prefix = "run"
			if not self.running_check(app):
				prefix = "not"
			print "%s %d: %s (%s)" % (prefix ,app, self.config[app]["wsgi-file"], self.config[app]["uid"])

if __name__ == "__main__":
	if not os.getuid() == 0:
		print "You have to be root :-("
		sys.exit(1)

	m = manager()

	parser = OptionParser()
	parser.add_option("-s", "--start", dest="start", help="Start app", metavar="ID", action="store")
	parser.add_option("-S", "--stop", dest="stop", help="Stop app (sig 9)", metavar="ID", action="store")
	parser.add_option("-r", "--reload", dest="reload", help="Reload app (sig 1)", metavar="ID", action="store")
	parser.add_option("-b", "--brutal-reload", dest="brutalreload", help="Brutal reload app (sig 15)", metavar="ID", action="store")
	parser.add_option("-R", "--restart", dest="restart", help="Restart app", metavar="ID", action="store")
	parser.add_option("-c", "--check", dest="check", help="Check state of app", metavar="ID", action="store")
	parser.add_option("-a", "--start-all", dest="startall", help="Start all apps", action="store_true")
	parser.add_option("-A", "--stop-all", dest="stopall", help="Stop all apps", action="store_true")
	parser.add_option("-w", "--reload-all", dest="reloadall", help="Reload all apps", action="store_true")
	parser.add_option("-W", "--restart-all", dest="restartall", help="Restart all apps", action="store_true")
	parser.add_option("-B", "--brutal-reload-all", dest="brutalreloadall", help="Brutal reload all apps", action="store_true")
	parser.add_option("-l", "--list", dest="list", help="Print state of all apps", action="store_true")
	

	(options, args) = parser.parse_args()
	
	if options.start: m.start(int(options.start))
	elif options.stop: m.stop(int(options.stop))
	elif options.restart: m.restart(int(options.restart))
	elif options.reload: m.reload(int(options.reload))
	elif options.brutalreload: m.brutal_reload(int(options.brutalreload))
	elif options.check: m.check(int(options.check))


	elif options.startall: m.startall()
	elif options.stopall: m.stopall()
	elif options.reloadall: m.reloadall()
	elif options.brutalreloadall: m.brutal_reloadall()
	elif options.restartall: m.restartall()
	elif options.list: m.list()

	else: parser.print_help()
	
	
