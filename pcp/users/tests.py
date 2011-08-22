# -*- coding: utf-8 -*-

from django.contrib.auth.models import User as user
from clients.models import address, machine, parms
from domains.models import domain

def setUpUser():
	# user
	us = user.objects.filter(username="testuser")
	if us:
		u = us[0]
	else:
		u = user.objects.create_user("testuser","cx@initd.cz","testpass")
		u.is_active = True
		u.is_superuser = True
		u.is_staff = True
		u.save()

	# adresa
	ads = address.objects.filter(company="Test Company")
	if ads:
		a = ads[0]
	else:
		a = address()
		a.company				= "Test Company"
		a.residency_name		= "John Doe"
		a.residency_street		= "Teststreet 123"
		a.residency_city		= "Whooo"
		a.residency_city_num	= "56710"
		a.residency_ic			= "7456565163"
		a.residency_dic			= "CZ45454152415"
		a.residency_email		= "cx@initd.cz"
		a.residency_phone		= "+420777636388"
		a.save()

	# machine
	ms = machine.objects.filter(name="Testserver")
	if ms:
		m = ms[0]
	else:
		m = machine()
		m.name="Testserver"
		m.ip="127.0.0.1"
		m.domain="localhost"
		m.save()

	# parms
	ps = parms.objects.filter(home="/home/testuser")
	if not ps:
		p = parms()
		p.home		= "/home/testuser"
		p.note		= ""
		p.uid		= 1000
		p.gid		= 1000
		p.discount	= 50
		p.address	= a
		p.machine	= m
		p.user		= u
		p.save()

	#domain
	ds = domain.objects.filter(name="example.com")
	if not ds:
		d = domain()
		d.name		= "example.com"
		d.serial	= 0
		d.dns		= True
		d.mail		= True
		d.owner		= u
		d.save()

	return u
