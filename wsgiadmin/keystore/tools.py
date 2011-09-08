# -*- coding: utf-8 -*-
from wsgiadmin.keystore.models import *
import datetime,json

def ksez(input):
	"""Serializace - JSON
	"""
	
	return json.dumps(input)

def kdez(input):
	"""Deserializace - JSON
	"""

	return json.loads(input)

def kget(key,default=None):
	"""
		Vrací hodnotu uloženou pod klíčem a nebo default
	"""
	
	ik = store.objects.filter(key=key)
	if ik:
		ik[0].date_read = datetime.datetime.today()
		ik[0].save()
		return ik[0].value
	else:
		return default

def kset(key,value,expire=0):
	"""
		Nastavuje hodnotu pod klíč
	"""
	ik = store.objects.filter(key=key)
	if ik:
		ik[0].value = value
		ik.date_write = datetime.datetime.today()
		ik.expire = expire
		ik[0].save()
	else:
		ik = store()
		ik.key = key
		ik.value = value
		ik.expire = expire
		ik.save()
	return True
		
def krm(key):
	"""
		Smaže klíč
	"""
	ik = store.objects.filter(key=key)
	if ik:
		ik.delete()
		return True
	return False

def klist():
	"""
		List uložených klíčů
	"""

	return [x.key for x in store.objects.all()]
