# -*- coding: utf-8 -*-

from domains.models import domain
import datetime

def gen_zone_config(d):
	zone = ""

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
	if d.ipv4:
		zone += "@	IN		A	%s\n"%d.owner.parms.web_machine.ip
	if d.ipv6:
		zone += "@	IN		AAAA	%s\n"%d.owner.parms.web_machine.ipv6
	#zone += "www	IN		CNAME	@\n"
	zone += "*	IN		CNAME	@\n"

	d.serial = serial
	d.save()

	return zone

def gen_bind_config(side="pri"):
	config = ""
	for d in list(domain.objects.filter(dns=True)):
		if side == "sec":
			config += "zone \"%s\" IN {\n"%d.name
			config += "	type slave;\n"
			config += "	file \"sec_auto/%s.zone\";\n"%d.name
			config += "	allow-query { any; };\n"
			config += "	masters { 87.236.194.121; };\n"
			config += "};\n"
		else:
			config += "zone \"%s\" IN {\n"%d.name
			config += "	type master;\n"
			config += "	file \"pri_auto/%s.zone\";\n"%d.name
			config += "	allow-query { any; };\n"
			config += "	allow-transfer { 89.111.104.70; };\n"
			config += "	notify yes;\n"
			config += "};\n"
	return config

