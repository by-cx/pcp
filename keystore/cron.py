# -*- coding: utf-8 -*-

import logging,datetime

from keystore.models import *

#TODO:implementovat jinak
class expire_keystore:
	"""
		Cron Job, která maže expirované klíče
	"""

	# run every 1 day
	#run_every = 86400
	run_every = 7200
                
	def job(self):
		logging.info("Hledání expirovaných klíčů")
		for x in store.objects.all():
			if x.expire > 0:
				enddate = x.date_write+datetime.timedelta(0,x.expire*60)
				if datetime.datetime.now() > endtime:
					logging.info("Expiroval klíč %s"%x.key)
					x.delete()
