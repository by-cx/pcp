# -*- coding: utf-8 -*-

from django.test import TestCase

from keystore.tools import *

class keystore_test(TestCase):
	def testBasic(self):
		print "Testuju keystore úložiště"
		self.assertEquals(kset("test","ttt"),True)
		self.assertEquals(kget("test"),"ttt")
		self.assertEquals(kset("test","ttt2"),True)
		self.assertEquals(kget("test"),"ttt2")
		self.assertEquals(krm("test"),True)
