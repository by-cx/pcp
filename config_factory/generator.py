# -*- coding: utf-8 -*-

def nginx(sites):
	conf = ""

	for site in sites:
		
		wsgi = True
		try:
			site.wsgi
		except:
			wsgi = False

		#...
