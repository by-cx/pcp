# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

class store(models.Model):
	key			= models.CharField(_(u"Klíč"),max_length=250,unique=True)
	value		= models.CharField(_(u"Hodnota"),max_length=250)
	expire		= models.IntegerField(_(u"Expirace"),help_text=_(u"v minutách"),default=0)
	date_read	= models.DateTimeField(auto_now_add=True,blank=True,null=True)
	date_write	= models.DateTimeField(auto_now_add=True,blank=True,null=True)
	
	def __unicode__(self):
		return "%s: '%s'"%(self.key,self.value)
