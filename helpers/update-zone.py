#!/usr/bin/python
# -*- coding: utf-8 -*-

import os,sys,datetime
sys.path.append('/home/cx/co/')
sys.path.append('/home/cx/co/rosti')
os.environ['DJANGO_SETTINGS_MODULE'] = 'rosti.settings'

from settings import *
from domains.models import *

try:
	inputDomain = sys.argv[1]
except:
	print "Nezadaná doména"
	sys.exit(1)

d = domain.objects.filter(name=inputDomain)

if not d:
	print "Doména nenalezena"
	sys.exit(1)
else:
	d = d[0]
	dateNow = datetime.date.today()
	num = 0
	if len(str(d.serial)) == 10:
		ye   = int(str(d.serial)[0:4])
		mo   = int(str(d.serial)[4:6])
		da   = int(str(d.serial)[6:8])
		num = int(str(d.serial)[8:10])

		if dateNow == datetime.date(ye,mo,da):
			num += 1
	
	serial = int("%.4d%.2d%.2d%.2d"%(dateNow.year,dateNow.month,dateNow.day,num))

	zone = ""
	zone += "$TTL 600s\n"
	zone += "@	IN	SOA	ns1.rosti.cz. info.rosti.cz.  (\n"
	zone += "					%d	; Serial\n"%serial
	zone += "					3600		; Refresh\n"
	zone += "					1800		; Retry\n"
	zone += "					604800		; Expire - 1 week\n"
	zone += "					300 )		; Minimum\n"
	zone += "@	IN		NS	ns1.rosti.cz.\n"
	zone += "@	IN		NS	ns2.rosti.cz.\n"
	zone += "@	IN		MX 10	mail.rosti.cz.\n"
	zone += "@	IN		A	%s\n"%d.owner.parms.web_machine.ip
	zone += ";	IN		AAAA	%s\n"%d.owner.parms.web_machine.ipv6
	zone += "www	IN		CNAME	@\n"
	zone += "*	IN		CNAME	@\n"

	d.serial = serial
	d.save()

	print zone
