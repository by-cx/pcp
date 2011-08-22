# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
#from django.utils import unittest
import unittest, os
from django.test.client import Client
from wsgiadmin.users.tests import setUpUser

class apacheCase(unittest.TestCase):
	def setUp(self):
		self.u = setUpUser()

		self.c = Client()
		self.c.login(username='testuser', password='testpass')

	def test_sitelist(self):
		print "apacheconf: Sitelist test"
		response = self.c.get(reverse("apacheconf.views.apache"))
		self.assertEqual(response.status_code, 200)


	def test_addwsgi(self):
		os.system("sudo mkdir /home/testuser")
		os.system("sudo touch /home/testuser/test.wsgi")

		print "apacheconf: add_wsgi - show"
		response = self.c.get(reverse('apacheconf.views.addWsgi'))
		self.assertEqual(response.status_code, 200)

		data = {"serverName": "wsgi.example.com", "serverAlias": "www.wsgi.example.com",
		        "script": "/home/testuser/test.wsgi", "append": "Django"}

		print "apacheconf: add_wsgi - add"
		response = self.c.post(reverse('apacheconf.views.addWsgi'),data,follow=True)
		self.assertEqual(response.status_code, 200)
		self.assertEqual("Úpravy byly provedeny úspěšně" in response.content,True)

		os.system("sudo rm /home/testuser/test.wsgi")
		os.system("sudo rmdir /home/testuser")

	def test_add_static(self):
		os.system("sudo mkdir /home/testuser")
		os.system("sudo mkdir /home/testuser/teststatic")

		print "apacheconf: addStatic - static"
		response = self.c.get(reverse("apacheconf.views.addStatic",args=[0]))
		self.assertEqual(response.status_code, 200)

		print "apacheconf: addStatic - php"
		response = self.c.get(reverse("apacheconf.views.addStatic",args=[1]))
		self.assertEqual(response.status_code, 200)

		print "apacheconf: addStatic - add static web"
		data = {"serverName": "static.example.com", "serverAlias": "www.static.example.com",
		        "documentRoot": "/home/testuser/teststatic"}
		response = self.c.post(reverse("apacheconf.views.addStatic",args=[0]),data, follow=True)

		self.assertEqual(response.status_code, 200)
		self.assertEqual("Úpravy byly provedeny úspěšně" in response.content,True)

		print "apacheconf: addStatic - add php web"
		data = {"serverName": "php.example.com", "serverAlias": "www.php.example.com",
		"documentRoot": "/home/testuser/teststatic"}
		response = self.c.post(reverse("apacheconf.views.addStatic",args=[1]),data, follow=True)
		self.assertEqual(response.status_code, 200)
		self.assertEqual("Úpravy byly provedeny úspěšně" in response.content,True)

		os.system("sudo rmdir /home/testuser/teststatic")
		os.system("sudo rmdir /home/testuser")



