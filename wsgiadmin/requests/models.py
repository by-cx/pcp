# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User as user

from django.utils.translation import ugettext_lazy as _

class Request(models.Model):
	add_date = models.DateTimeField(_("Add date"), auto_now_add=True)
	done_date = models.DateTimeField(_("Done date"), default=None, null=True, blank=True)
	done = models.BooleanField(_("Done"), default=False)
	action = models.CharField(_("Action"), choices=["run", ""])
	data = models.TextField(_("Data"), blank=True)
	stdout = models.TextField(_("Stdout"), blank=True, null=True)
	stderr = models.TextField(_("Stderr"), blank=True, null=True)
	user = models.ForeignKey(user)

	def __unicode__(self):
		return ""
