# -*- coding: utf-8 -*-

"""Zpracování requestů z mongodb"""

#TODO:Remove (put into settings or another solve)
IP = "95.82.174.87"

RESTART = False # Stačí restartovat jednou

import os,sys
sys.path.append('/home/cx/co/')
sys.path.append('/home/cx/co/rosti')
os.environ['DJANGO_SETTINGS_MODULE'] = 'rosti.settings'

import logging, MySQLdb
from requests.tools import request
from subprocess import Popen,PIPE
from django.conf import settings

info = logging.info

def do_mysql_query(query):
	db = MySQLdb.connect(host=settings.MYSQL_HOST, user=settings.MYSQL_USER, passwd=settings.MYSQL_PASSWORD, db="mysql")
	cur = db.cursor()

	#TODO:Make it more secure
	try:
		cur.execute(query)
		if settings.DEBUG: info(query)
		info("MySQL query ok")
	except MySQLdb.Error, e:
		info(query)
		info("Error %d: %s" % (e.args[0], e.args[1]))
		return False

	data = cur.fetchall()

	cur.close()
	db.close()

	return True

def run(cmds, comment="", stdin=None):
	if stdin:
		p = Popen(cmds,stdout=PIPE,stderr=PIPE,stdin=PIPE)
		data_raw = p.communicate(stdin)
		data_out = data_raw[0]
		data_err = data_raw[1]
		p.wait()
	else:
		p = Popen(cmds,stdout=PIPE,stderr=PIPE)
		data_out = p.stdout.read()
		data_err = p.stderr.read()
		p.wait()

	info("Run \"%s\" with comment \"%s\""%(" ".join(cmds), comment))
	if data_out:
		info("Stdout: "+data_out)
	if data_err:
		info("Stderr: "+data_err)

