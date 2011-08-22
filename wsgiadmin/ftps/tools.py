# -*- coding: utf-8 -*-
from subprocess import Popen,PIPE
from wsgiadmin.requests.tools import request_raw

def user_directories(u):
	rr = request_raw(u.parms.web_machine.ip)
	dirs = rr.run("/usr/bin/find %s -maxdepth 2 -type d" % u.parms.home)["stdout"].split("\n")

	return [d.strip() for d in dirs if d and not "/." in d]
