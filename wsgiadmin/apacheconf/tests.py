# -*- coding: utf-8 -*-
import datetime
from django.contrib.auth.models import User

from django.core.urlresolvers import reverse
#from django.utils import unittest
import unittest
from django.test.client import RequestFactory
from wsgiadmin.apacheconf.views import apache, restart, reload, update_wsgi, add_wsgi, remove_site, update_static, add_static
from wsgiadmin.clients.models import Machine, Address, Parms

class basicCase(unittest.TestCase):
	def setUp(self):
		u = User.objects.create_user("testuser", "info@localhost", "******")
		u.is_active = False
		#u.save()
		# adresa
		a = Address()
		a.company				= "xxx"
		a.residency_name		= "xxx"
		a.residency_street		= "xxx"
		a.residency_city		= "xxx"
		a.residency_city_num	= "56301"
		a.residency_ic			= "1234"
		a.residency_dic			= "CZ1234"
		a.residency_email		= "info@localhost"
		a.residency_phone		= "+420123456789"
		#a.save()
		# machine
		m = Machine()
		m.ipv6 = "::1"
		m.ipv4 = "127.0.0.1"
		m.domain = "localhost"
		m.name = "Localhost"
		#m.save()
		# parms
		p = Parms()
		p.home		    = "/home/testuser"
		p.note		    = ""
		p.uid		    = 1000
		p.gid		    = 1000
		p.discount	    = 0
		p.address	    = a
		p.web_machine	= m
		p.mail_machine	= m
		p.mysql_machine	= m
		p.pgsql_machine	= m
		p.user		    = u
		#p.save()

		self.user = u
		self.parms = p
		self.machine = m
		self.address = a

		self.factory = RequestFactory()
		self.basic_request = self.factory.get("/")
		self.basic_request.user = self.user
		self.basic_request.session = {}

	def tearDown(self):
		"""FIX THIS SOMEHOW: DatabaseError: cannot delete from a view
		HINT:  You need an unconditional ON DELETE DO INSTEAD rule.
		"""
		#self.user.delete()
		#self.parms.delete()
		#self.machine.delete()
		#self.address.delete()
		pass

class apacheCase(basicCase):
	def setUp(self):
		super(apacheCase, self).setUp()

		self.site_uwsgi = Site()
		self.site_uwsgi.pub_date		= datetime.datetime.today()
		self.site_uwsgi.end_date		= None
		self.site_uwsgi.type            = "uwsgi"
		self.site_uwsgi.domains         = "test.cz"
		self.site_uwsgi.documentRoot	= "/"
		self.site_uwsgi.allow_ips	    = ""
		self.site_uwsgi.deny_ips	    = ""
		self.site_uwsgi.script		    = "/foo.wsgi"
		self.site_uwsgi.owner			= self.user
		
		self.site_static = Site()
		self.site_static.pub_date		= datetime.datetime.today()
		self.site_static.end_date		= None
		self.site_static.type            = "static"
		self.site_static.domains         = "test.cz"
		self.site_static.documentRoot	= "/"
		self.site_static.allow_ips	    = ""
		self.site_static.deny_ips	    = ""
		self.site_static.script		    = "/foo.wsgi"
		self.site_static.owner			= self.user

	def tearDown(self):
		super(apacheCase, self).tearDown()

		#self.site_static.delete()
		#self.site_uwsgi.delete()

	def test_apache(self):
		response = apache(self.basic_request)
		self.assertEqual(response.status_code, 200)

	def test_add_static(self):
		response = add_static(self.basic_request, php="0")
		self.assertEqual(response.status_code, 200)

	#def test_update_static(self):
	#	response = update_static(self.basic_request, self.site_static.id)
	#	self.assertEqual(response.status_code, 200)

	#def test_remove_site(self):
	#	response = remove_site(self.basic_request,self.site_static.id)
	#	self.assertEqual(response.status_code, 200)

	#def test_add_wsgi(self):
	#	response = add_wsgi(self.basic_request)
	#	self.assertEqual(response.status_code, 200)

	#def test_update_wsgi(self):
	#	response = update_wsgi(self.basic_request, self.site_uwsgi.id)
	#	self.assertEqual(response.status_code, 200)

	#def test_reload(self):
	#	response = reload(self.basic_request, self.site_uwsgi.id)
	#	self.assertEqual(response.status_code, 200)

	#def test_restart(self):
	#	response = restart(self.basic_request, self.site_uwsgi.id)
	#	self.assertEqual(response.status_code, 200)
