#!/usr/bin/python
# -*- coding: utf-8 -*-

import os,sys,httplib,socket
sys.path.append('/home/cx/co/')
sys.path.append('/home/cx/co/rosti')
os.environ['DJANGO_SETTINGS_MODULE'] = 'rosti.settings'

from settings import *
from apacheconf.models import *

from django.core.mail import send_mail

anyfail = False
out = ""
last = []

domains = site.objects.filter(removed=False)

if not os.path.isfile("/tmp/webtests"):
	f = open("/tmp/webtests","w")
	for s in domains:
		f.write(s.serverName+":200\n")
	f.close()
f = open("/tmp/webtests")
rls = f.readlines()
f.close()

for line in [l.strip() for l in rls if l]:
	last.append(line.split(":"))

def check(server,url="/"):
	h = httplib.HTTPConnection(server)
	h.request("GET",url)
	r = h.getresponse()
	h.close()
	return r

i = 0
for s in domains:
	print "%d/%d %s"%(i, len(domains), s.serverName)
	i += 1
	out += s.serverName+":"

	try:
		r = check(s.serverName)
		conn = True
	except socket.error:
		conn = False

	if r.status == 200 and conn:
		out += str(r.status)+"\n"
	elif r.status in (301,302,303) and conn:
		location = r.getheader("location")
		location = location.replace("http://"+s.serverName,"")
		if location[-1] != "/":
			location += "/"
		if location[0] != "/":
			location = "/"+location
		r = check(s.serverName,location)
		out += str(r.status)+"\n"
	elif conn:
		anyfail = True
		out += str(r.status)+"\n"
		print r.status
	else:
		anyfail = True
		out += "Down\n"
		print r.status

	if conn:
		if s.serverName in [rec[0] for rec in last if rec[1] != str(r.status) ]:
			send_mail('HTTP Code', s.serverName+":"+str(r.status), 'info@rosti.cz',['creckx@vodafonemail.cz'], fail_silently=False)
	else:
		if s.serverName in [rec[0] for rec in last if rec[1] != str(r.status) ]:
			send_mail('HTTP Code', s.serverName+":Down", 'info@rosti.cz',['creckx@vodafonemail.cz'], fail_silently=False)

if anyfail:
	print out

f = open("/tmp/webtests","w")
f.write(out)
f.close()
