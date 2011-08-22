# -*- coding: utf-8 -*-
import re,syslog

from settings import ROOT

from subprocess import Popen,PIPE

def run_on_machine(cmd,u,as_user="root",stdin=None):
	"""
		Spustí příkaz na správném serveru (obvykle root)
		
		cmd - array
		u - user model
		as_user - spustit jako uživatel as_user - default root
	"""
	
	ip = u.parms.web_machine.ip

	# local IPs
	#p = Popen(["ip","a"],stdout=PIPE,stderr=PIPE)
	#data = p.stdout.read()
	#p.wait()
	
	#ips = re.findall("inet ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})",data)

	#if ip in ips:
	#	prefix = ["/usr/bin/sudo","su",as_user]
	#else:
	#	prefix = ["ssh",as_user+"@"+ip]
	
	prefix = ["ssh",as_user+"@"+ip]

	if stdin:
		p = Popen(prefix+cmd,stdout=PIPE,stderr=PIPE,stdin=PIPE)
		data_raw = p.communicate(stdin)
		data = data_raw[0]
		data_err = data_raw[1]
		p.wait()
	else:
		p = Popen(prefix+cmd,stdout=PIPE,stderr=PIPE)
		data = p.stdout.read()
		data_err = p.stderr.read()
		p.wait()

	#syslog.syslog(syslog.LOG_DEBUG, data)
	#syslog.syslog(syslog.LOG_DEBUG, data_err)
	#syslog.openlog(logopt=syslog.LOG_PID, facility=syslog.LOG_DAEMON)
	syslog.syslog(" ".join(prefix+cmd))
	if data: syslog.syslog(data)
	if data_err: syslog.syslog(data_err)
	
	return data,data_err

def size_format(b):
	sizes_int = [1,1024,1024**2,1024**3,1024**4,1024**5,1024**6]
	sizes_s = ["B","kB","MB","GB","TB","PB"]
	i = 0
	for size in sizes_s:
		if b < sizes_int[i+1]:
			return "%.2f %s"%(float(b)/float(sizes_int[i]),size)
		i += 1
	return "%.2f %s"%(float(b)/float(sizes_int[i]),size)

def sc(s,color="nc"):
	"""Shell Color
	"""
	
	colors = {
		"red"	: '\x1b[0;31m',
		"red2"	: '\x1b[1;31m',
		"blue"	: '\x1b[0;34m',
		"blue2"	: '\x1b[1;34m',
		"cyan"	: '\x1b[0;36m',
		"cyan2"	: '\x1b[1;36m',
		"nc"	: '\x1b[0m', # No Color
	}
	
	return "%s%s%s"%(colors[color],s,colors["nc"])
	
	
