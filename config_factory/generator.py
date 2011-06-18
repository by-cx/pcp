# -*- coding: utf-8 -*-

from django.template.loader import render_to_string

def nginx(sites):
	conf = ""

	for site in sites:
		
		wsgi = True
		try:
			site.wsgi
		except:
			wsgi = False

		if wsgi:
			statics = []
			for static in [x.strip().split(" ") for x in site.wsgi.static.split("\n") if not "#" in x]:
				statics.append({"url": static[0], "path": site.owner.parms.home+static[1]})

			conf += render_to_string("nginx_uwsgi.conf", {
				"domains": site.serverName+" "+site.serverAlias,
			    "sock": site.wsgi.socket(),
			    "statics": statics,
			    "access_log": "/var/log/webx/access_%s.log combined" % site.serverName,
				"error_log": "/var/log/webx/error_%s.log" % site.serverName,
			})
			conf += "\n\n"
			
		elif not wsgi:
			conf += render_to_string("nginx_proxy.conf", {
					"domains": site.serverName+" "+site.serverAlias,
					"access_log": "/var/log/webx/access_%s.log combined" % site.serverName,
					"error_log": "/var/log/webx/error_%s.log" % site.serverName,
				})
			conf += "\n\n"

	return conf
