#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, errno, sys

PID_DIR = "/var/run/"
IDENT = "rosti_web"
PID_FILE = PID_DIR+IDENT+"_%d.pid"


def get_pids():
	"""Načte seznam možných běžícíh pidů"""
	pids = []
	for pidfile in os.listdir(PID_DIR):
		if len(pidfile) > len(IDENT) and pidfile[0:len(IDENT)] == IDENT:
			web_id = int(pidfile[len(IDENT)+1:-4])

			f = open(PID_FILE % web_id)
			pid = int(f.read().strip())
			f.close()

			pids.append((web_id, pid))
	return pids

def filter_killed(pid):
	"""Filtrovací funkce na běžící procesy"""
	try:
		os.kill(pid, 0)
	except OSError, err:
		if err.errno == errno.ESRCH:
			return False
		elif err.errno == errno.EPERM:
			print "No permission to signal this process!"
			sys.exit(1)
		else:
			print "Unknown error"
			sys.exit(1)
	else:
		return True

print get_pids()
pids = filter(lambda x: filter_killed(x[1]),get_pids())
print pids
