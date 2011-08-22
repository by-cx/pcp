#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,os,SOAPpy,unicodedata,random,time,logging

from django.contrib.auth.models import User as user
from wsgiadmin.clients.models import parms

from wsgiadmin.keystore.tools import *

class web4u:
	def __init__(self):
		self.adm_address = user.objects.filter(username="cx")[0].parms.address
		self.ns1 = "87.236.194.121"
		self.ns2 = "89.111.104.70"
		
		self.gw = "http://www.web4u.cz/cp/wsdl/Web4uGateway.wsdl"
		self.wp = SOAPpy.WSDL.Proxy(self.gw)
		self.user = "Creckx"
		self.passwd = "yero.dema8"
		self.tech_contact = "WEB4U_KKGDGEGYUSMFG"
		self.main_nsset = "ROSTICZ"

	def pure(self,field):
		return "".join(aChar for aChar in unicodedata.normalize("NFD", unicode(field)) if "COMBINING" not in unicodedata.name(aChar))
	
	def domain_service_id(self):
		try:
			self.wp.checkDomain(self.user,self.passwd)
		except SOAPpy.Types.faultType as e:
			s = str(e).split("\n")
			for x in s:
				if "Sprava domen" in x:
					x = x.split()
					return x[0]

		return False

	def find(self,domain):
		"""Ověření obsazenosti domény"""
		sid = self.domain_service_id()
		if sid:
			r = self.wp.checkDomain(self.user,self.passwd,sid,domain)
			return r
		
		return False
	
	
	###############################################################
	## CZ domény
	###############################################################
	
	def cz_get_sid(self,sid=None):
		"""Získá servise ID
		
		@param sid: Pokud již nějaký existuje vyplňte, pokud nefunguje, vytvoří se nový
		
		@return: Vrací service ID
		
		"""
		if not sid:
			
			sid = self.domain_service_id()
			
			if not sid:
				logging.error("Nepodařilo se získat identifikátor služby - uživatel %s"%(u.username))
				return False
			
		return sid
	
	def cz_reg_contact(self,u,sid=None,passwd=None,validate=False):
		""" Registrace CZ kontaktu
		
			@param u: uživatel djanga
			@param validate: jenom validace nebo provést požadavek
			@param sid: servis id
			@param passwd: transfer heslo
			
			@return: Vrací string s ID kontaktu
			
			from domains.api import *;w = web4u();from django.contrib.auth.models import User as user;u = user.objects.all()[1];w.cz_reg_contact(u);
		"""
	
		sid = self.cz_get_sid(sid)
		if not sid:
			return False
	
		contact_id = kget("domain:contact:cz:%s"%u.username)

		if not contact_id:
			contact_id = "ROSTICONTEST%.5d"%u.parms.address.id
			try:
				logging.info("Registruju kontakt %s"%contact_id)
				logging.info("Jméno: %s"%u.parms.address.residency_name)
				logging.info("Email: %s"%u.parms.address.residency_email)
				logging.info("Ulice: %s"%u.parms.address.residency_street)
				logging.info("Město: %s"%u.parms.address.residency_city)
				logging.info("PSČ: %s"%unicode(u.parms.address.residency_city_num).replace(" ",""))
				logging.info("Země: %s"%"CZ")
				logging.info("Společnost: %s"%u.parms.address.company)
				logging.info("Telefon: %s"%u.parms.address.residency_phone)
				logging.info("DIČ: %s"%u.parms.address.residency_dic)
				
				r = self.wp.czContactNew(
										self.user,
										self.passwd,
										sid,
										contact_id,
										u.parms.address.residency_name,		#jmeno a prijmeni
										u.parms.address.residency_email,	#emailova adresa
										u.parms.address.residency_street,	#ulice
										u.parms.address.residency_city,		#mesto
										unicode(u.parms.address.residency_city_num).replace(" ",""),	#PSC
										"CZ",								#zeme
										None,								#address2 - dalsi radek pro adresu
										None,								#address3 - dalsi radek pro adresu
										u.parms.address.company,			#company  - jmeno spolecnosti
										None,								#state    - stat
										passwd,								#transfer_auth - heslo pro pristi transfer
										u.parms.address.residency_phone,	#phone - telefon
										None,								#fax   - fax
										None,								#disclose [voice,fax,email,vat,ident,notify_email] - ktere udaje se mohou verejne zobrazovat
										u.parms.address.residency_dic,		#vat   - DIC
										None,								#ident_value - cislo prukazu
										None, 								#ident_type [op,passport,mpsv,ico,birthday] - typ prukazu
										None,		 						#notify_email - notifikacni email
									)

				kset("domain:contact:cz:%s"%u.username,contact_id)
			except SOAPpy.Types.faultType as e:
				logging.error("Chyba při registraci kontaktu (%s) - uživatel %s"%(str(e),u.username))
				return False
		
		logging.info("Kontakt %s registrován/získán"%contact_id)
		return contact_id
	
	def cz_reg_transfer(self,u,d,ip_info,years=1,passwd=None,validate=False):
		""" Registrace CZ domény
		
			@param u: uživatel djanga
			@param d: název domény včetně .cz (.cocz)
			@param ip_info: IP adresa a hostname uživatele souhlasícího s pravidly
			@param years: počet let pro zaplacení
			@param passwd: transfer heslo
			@param validate: jenom validace nebo provést požadavek
			
			@return: False či True při úspěchu nebo problému (detaily v logu)
			
			Testování: 
			from domains.api import *;w = web4u();from django.contrib.auth.models import User as user;u = user.objects.all()[1];w.cz_reg_transfer(u,"test-blablabla.cz","89.111.104.66, Delorean");
		"""
		
		logging.info("Začínám registrovat/transferovat doménu - doména %s, uživatel %s"%(d,u.username))
		
		# Servise id
		sid = self.cz_get_sid()
		if not sid:
			return False
		
		logging.info("Získávám aktuální verzi pravidel - uživatel %s"%(u.username))
		try:
			version = self.wp.czRulesActualVersion(self.user,self.passwd,sid)
		except SOAPpy.Types.faultType as e:
			logging.error("Nepodařilo se získat verzi pravidel (%s) - doména %s, uživatel %s"%(str(e),d,u.username))
			return False
		
		logging.info("Verze pravidel je %s"%(version))
		
		# Kontrola zabranosti domény
		r = self.wp.checkDomain(self.user,self.passwd,sid,d)
		if not r:
			logging.error("Doména je registrovaná, pokouším se transferovat - doména %s, uživatel %s"%(d,u.username))
			transfer = True
		else:
			logging.error("Doména není registrovaná, pokouším se registrovat - doména %s, uživatel %s"%(d,u.username))
			transfer = False
		
		contact_id = self.cz_reg_contact(u,sid)
		if not contact_id: return False
		
		if transfer:
			fce = self.wp.czDomainTransfer
		else:
			fce = self.wp.czDomainCreate
		
		try:
			r = fce(
						self.user,
						self.passwd,
						sid,
						d,									# Doména
 						contact_id,							# ID kontaktu
 						self.main_nsset,					# identifikator NSSetu
				 		years,								# delka predplatneho obdobi v rocich
						self.tech_contact,					# administrativni kontakt
						passwd,								# transfer_auth_new
						u.parms.address.residency_name,		# adr_name - jmeno opravnene osoby (pouze nazev drzitele domeny)
						"1",								# adr_agreement [true|false] - potvrzeni | nepotvrzeni
						ip_info,							# adr_host_data - informace z jake IP + nazev hostitele PC ze ktereho uzivatel souhlas potvrdil min 15 znaku
						version,							# adr_version - verze potvrzenych pravidel (vzdy pouze aktualni pravidla)
					)

		except SOAPpy.Types.faultType as e:
			logging.error("Chyba při registraci domény (%s) - doména %s, uživatel %s"%(str(e),d,u.username))
			return False
		
		logging.info("Doména registrována - doména %s, uživatel %s"%(d,u.username))
		return True
 	
	def cz_renew(self,u,d,validate=False):
		"""Prodloužení domény CZ domény
		
			@param u: uživatel djanga
			@param d: název domény včetně .cz (.cocz)
			@param validate: jenom validace nebo provést požadavek
		"""
	
	###############################################################
	## EU domény
	###############################################################
	
	def eu_reg(self):
		pass
	
	def eu_transfer(self):
		pass
	
	def eu_renew(self):
		pass
	
	
	def euStates():
		pass
	
	def euLanguages():
		pass
	
	def euDomainNew():
		pass
	
	def euDomainTransfer():
		pass
	
	def euDomainRenew():
		pass
	
	###############################################################
	## Generické domény
	###############################################################

	def get_country(self):
		"""Vrací seznam států
		
		from domains.api import *;w = web4u();from django.contrib.auth.models import User as user;u = user.objects.all()[1];w.get_country()
		"""
		
		# Servise id
		sid = self.cz_get_sid()
		if not sid:
			return False
		
		try:
			codes = self.wp.genericStates(self.user,self.passwd,sid)
		except SOAPpy.Types.faultType as e:
			logging.error("Chyba při získávání seznamu států (%s) - uživatel %s"%(str(e),u.username))
			return False
		
		res = {}
		
		for code in codes:
			for c in code:
				res[c["key"]] = c["value"]
		return res
	
	def get_state(self,state):
		"""Vrací seznam krajů
		
		from domains.api import *;w = web4u();from django.contrib.auth.models import User as user;u = user.objects.all()[1];w.get_state("CZ")
		"""
		
		# Servise id
		sid = self.cz_get_sid()
		if not sid:
			return False
		
		try:
			codes = self.wp.genericCountries(self.user,self.passwd,sid,state)
		except SOAPpy.Types.faultType as e:
			logging.error("Chyba při získávání seznamu krajů (%s) - uživatel %s"%(str(e),u.username))
			return False
		
		res = {}
		
		states = {}
		
		for key,value in codes[0]:
			if key == "states":
				for k,v in value["item"]:
					states[v] = k

		return states

	def gen_reg(self,u,d,years=1,validate=False):
		""" Registrace generické domény
		
			@param u: uživatel djanga
			@param d: název domény včetně .cz (.cocz)
			@param years: počet let pro zaplacení
			@param validate: jenom validace nebo provést požadavek
			
			@return: False či True při úspěchu nebo problému (detaily v logu)
			
			Testování: 
			from domains.api import *;w = web4u();from django.contrib.auth.models import User as user;u = user.objects.all()[1];w.cz_reg_transfer(u,"test-blablabla.cz","89.111.104.66, Delorean");
		"""
		
		logging.info("Začínám registrovat/transferovat generickou doménu - doména %s, uživatel %s"%(d,u.username))
		
		# Servise id
		sid = self.cz_get_sid()
		if not sid:
			return False
		
		# Kontrola zabranosti domény
		r = self.wp.checkDomain(self.user,self.passwd,sid,d)
		if not r:
			logging.error("Doména je registrovaná, pokouším se transferovat - doména %s, uživatel %s"%(d,u.username))
			transfer = True
		else:
			logging.error("Doména není registrovaná, pokouším se registrovat - doména %s, uživatel %s"%(d,u.username))
			transfer = False
		
		if transfer:
			fce = self.wp.genericDomainTransfer
			try:
				r = fce(
						self.user,
						self.passwd,
						sid,
						d,									# Doména

					)

			except SOAPpy.Types.faultType as e:
				logging.error("Chyba při transferu domény (%s) - doména %s, uživatel %s"%(str(e),d,u.username))
				return False
		else:
			try:
				fce = self.wp.genericDomainNew
				r = fce(
						self.user,
						self.passwd,
						sid,
						d,									# Doména
						years, # $period
						u.address.residency_name, # $reg_c_name     - jmeno a prijmeni
						u.address.residency_street, # $reg_c_address1 - adresa
						u.address.residency_city, # $reg_c_city     - mesto
						str(u.address.residency_city_num).replace(" ",""), # $reg_c_zip      - PSC
						None, # $reg_c_state    - kod statu
						"CZ", # $reg_c_country  - ciselny kod kraje
						u.address.residency_phone, # $reg_c_phone    - telefon
						u.address.residency_email, # $reg_c_email    - email
						u.address.company, # $reg_c_company  - jmeno spolecnosti
						None, # $reg_c_address2 - dalsi radek adresy
						None, # $reg_c_address3 - dalsi radek adresy
						None, # $reg_c_fax      - fax
						self.adm_address.residency_name, # $adm_c_name
						self.adm_address.residency_street, # $adm_c_address1
						self.adm_address.residency_city, # $adm_c_city
						str(self.adm_address.residency_city_num).replace(" ",""), # $adm_c_zip
						"Pardubicky kraj", # $adm_c_state
						"CZ", # $adm_c_country
						self.adm_address.residency_phone, # $adm_c_phone
						self.adm_address.residency_email, # $adm_c_email
						"Rosti.cz", # $adm_c_company
						None, # $adm_c_address2
						None, # $adm_c_address3
						None, # $adm_c_fax
						self.ns1, # $ns_1 - nameserver
						self.ns2, # $ns_2
						None, # $ns_3
						None, # $ns_4	
					)

			except SOAPpy.Types.faultType as e:
				logging.error("Chyba při registraci domény (%s) - doména %s, uživatel %s"%(str(e),d,u.username))
				return False
		
		logging.info("Doména registrována - doména %s, uživatel %s"%(d,u.username))
		return True
	
	def gen_transfer(self):
		pass
	
	def gen_renew(self):
		pass

	def genericStates():
		pass
	
	def genericCountries():
		pass
	
	def genericDomainNew():
		pass
	
	def genericDomainRenew():
		pass
	
	def genericDomainRenewValidate():
		pass
	
	def genericDomainTransfer():
		pass


if __name__ == "__main__":
	w = web4u()
	try:
		if w.find("initd.cz"):
			print "Doména je volná"
		else:
			print "Doména je obsazená"
	except SOAPpy.Types.faultType:
		print "Při vykonávání požadavku došlo k chybě, zkuste to prosím znovu."
