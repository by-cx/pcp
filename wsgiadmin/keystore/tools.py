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

## Nový přístup do redisu

#r = redis.Redis(
#					host=settings.REDIS_HOST,
#					port=settings.REDIS_PORT,
#					db=settings.REDIS_DB,
#					password=settings.REDIS_PASSWORD,
#				)
#
#def kget(key,default=None):
#	"""
#		Vrací hodnotu uloženou pod klíčem a nebo default
#	"""
#	
#	value = r.get(key)
#	if not value:
#		return default
#	return value
#

#def kset(key,value,expire=0):
#	"""
#		Nastavuje hodnotu pod klíč
#		
#		expirace v minutách
#	"""
#	
#	r.set(key, value)
#	
#	if expire:
#		r.expire(key,expire*60)
#	
#	return True


#def krm(key):
#	"""
#		Smaže klíč
#	"""
#	
#	r.delete(key)
#	
#	return True
#

#def klist(pattern="*"):
#	"""
#		List uložených klíčů
#	"""
#	
#	return r.keys(pattern)
#

#def knative():
#	"""
#		Vrací spojení k redisu
#	"""
#	
#	return r
#
##TODO Mongo keystore

#db = settings.get_db()

## Starý přístup do DB

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


def from_old_to_new():
	for key in klist_old():
		kset(key,kget_old(key))
