#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,os
import reportlab.rl_config
from reportlab.pdfgen.canvas import Canvas

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm, mm, inch, pica
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from wsgiadmin.settings import *
from wsgiadmin.invoices.models import *
from wsgiadmin.clients.models import *

PROVIDER = parms.objects.filter(id=1)
if PROVIDER: PROVIDER = PROVIDER[0]

class genInvoice:
	def __init__(self,invoice,path):
		self.invoice = invoice
		self.TOP = 260
		self.LEFT = 20

		pdfmetrics.registerFont(TTFont('DejaVu', '/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf'))

		self.pdf = Canvas(path, pagesize = letter)
		self.pdf.setFont("DejaVu", 15)
		self.pdf.setStrokeColorRGB(0, 0, 0)

		# Horní lajna
		self.pdf.drawString(self.LEFT*mm, self.TOP*mm, "Faktura")
		self.pdf.drawString((self.LEFT+100)*mm, self.TOP*mm, "Variabilní symbol: %d"%self.invoice.payment_id)

		# Rámečky
		self.pdf.rect((self.LEFT)*mm, (self.TOP-68)*mm, (self.LEFT+156)*mm, 65*mm, stroke=True, fill=False)

		path = self.pdf.beginPath()
		path.moveTo((self.LEFT+88)*mm, (self.TOP-3)*mm)
		path.lineTo((self.LEFT+88)*mm, (self.TOP-68)*mm)
		self.pdf.drawPath(path, True, True)

		path = self.pdf.beginPath()
		path.moveTo((self.LEFT)*mm, (self.TOP-39)*mm)
		path.lineTo((self.LEFT+88)*mm, (self.TOP-39)*mm)
		self.pdf.drawPath(path, True, True)

		path = self.pdf.beginPath()
		path.moveTo((self.LEFT+88)*mm, (self.TOP-23)*mm)
		path.lineTo((self.LEFT+176)*mm, (self.TOP-23)*mm)
		self.pdf.drawPath(path, True, True)

	def odberatel(self,TOP,LEFT):
		self.pdf.setFont("DejaVu", 12)
		self.pdf.drawString((LEFT)*mm, (TOP)*mm, "Odběratel")
		self.pdf.setFont("DejaVu", 8)
		text = self.pdf.beginText((LEFT+2)*mm, (TOP-6)*mm)
		text.textLines(str(self.invoice.client_address.getInvoiceAddress()))
		self.pdf.drawText(text)
		text = self.pdf.beginText((LEFT+2)*mm, (TOP-28)*mm)
		text.textLines(self.invoice.client_address.getInvoiceContact())
		self.pdf.drawText(text)

	def dodavatel(self,TOP,LEFT):
		self.pdf.setFont("DejaVu", 12)
		self.pdf.drawString((LEFT)*mm, (TOP)*mm, "Dodavatel")
		self.pdf.setFont("DejaVu", 8)
		text = self.pdf.beginText((LEFT+2)*mm, (TOP-6)*mm)
		text.textLines(str(PROVIDER.address.getInvoiceAddress()))
		self.pdf.drawText(text)
		text = self.pdf.beginText((LEFT+40)*mm, (TOP-6)*mm)
		text.textLines(PROVIDER.address.getInvoiceContact())
		self.pdf.drawText(text)
		self.pdf.drawString((LEFT+2)*mm, (TOP-26)*mm, "Podnikatel zapsán v živ. rejstříku MÚ Lanškroun")

	def platba(self,TOP,LEFT):
		self.pdf.setFont("DejaVu", 11)
		self.pdf.drawString((LEFT)*mm, (TOP)*mm, "Údaje pro platbu")
		#self.pdf.setFillColorRGB(255, 0, 0)
		text = self.pdf.beginText((LEFT+2)*mm, (TOP-6)*mm)
		text.textLines("""%s
Číslo účtu: %s
Variabilní symbol: %s"""%(str(self.invoice.bank),str(self.invoice.bank_account),str(self.invoice.payment_id)))
		self.pdf.drawText(text)

	def polozky(self,TOP,LEFT):
		# fakturované věci
		path = self.pdf.beginPath()
		path.moveTo((LEFT)*mm, (TOP-4)*mm)
		path.lineTo((LEFT+176)*mm, (TOP-4)*mm)
		self.pdf.drawPath(path, True, True)
	
		self.pdf.setFont("DejaVu", 9)
		self.pdf.drawString((LEFT+1)*mm, (TOP-2)*mm, "Fakturuji vám:")

		i=9
		self.pdf.drawString((LEFT+100)*mm, (TOP-i)*mm, "Množství")
		self.pdf.drawString((LEFT+122)*mm, (TOP-i)*mm, "Cena za jedn.")
		self.pdf.drawString((LEFT+150)*mm, (TOP-i)*mm, "Cena celkem")
		i+=5

		# seznam
		total=0
		for x in self.invoice.item_set.all():
			self.pdf.drawString((LEFT+1)*mm, (TOP-i)*mm, x.name)
			i+=5
			self.pdf.drawString((LEFT+100)*mm, (TOP-i)*mm, "%d ks"%x.count)
			self.pdf.drawString((LEFT+122)*mm, (TOP-i)*mm, "%d,- kč"%x.price_per_one)
			self.pdf.drawString((LEFT+150)*mm, (TOP-i)*mm, "%d,- kč"%(x.price_per_one*x.count))
			i+=5
			total += x.price_per_one*x.count

		path = self.pdf.beginPath()
		path.moveTo((LEFT)*mm, (TOP-i)*mm)
		path.lineTo((LEFT+176)*mm, (TOP-i)*mm)
		self.pdf.drawPath(path, True, True)
	
		self.pdf.setFont("DejaVu", 12)
		self.pdf.drawString((LEFT+130)*mm, (TOP-i-10)*mm, "Celkem: %d ,- kč"%total)

		self.pdf.rect((LEFT)*mm, (TOP-i-17)*mm, (LEFT+156)*mm, (i+19)*mm, stroke=True, fill=False) #140,142

		if self.invoice.sign:
			self.pdf.drawImage(STAMP_SIGN, (LEFT+98)*mm, (TOP-i-72)*mm)
		else:
			self.pdf.drawImage(STAMP_NOSIGN, (LEFT+100)*mm, (TOP-i-68)*mm)

		path = self.pdf.beginPath()
		path.moveTo((LEFT+110)*mm, (TOP-i-70)*mm)
		path.lineTo((LEFT+164)*mm, (TOP-i-70)*mm)
		self.pdf.drawPath(path, True, True)

		self.pdf.drawString((LEFT+112)*mm, (TOP-i-75)*mm, "Vystavil: Adam Štrauch")

	
	def datumy(self,TOP,LEFT):
		self.pdf.setFont("DejaVu", 10)
		self.pdf.drawString((LEFT)*mm, (TOP+1)*mm, "Datum vystavení: %s"%self.invoice.date_exposure.strftime("%d.%m.%Y"))
		self.pdf.drawString((LEFT)*mm, (TOP-4)*mm, "Datum splatnosti: %s"%self.invoice.date_payback.strftime("%d.%m.%Y"))
		self.pdf.drawString((LEFT)*mm, (TOP-9)*mm, "Forma úhrady: "+self.invoice.paytype)

	def gen(self):
		# Texty	
		self.dodavatel(self.TOP-10,self.LEFT+3)
		self.odberatel(self.TOP-30,self.LEFT+91)
		self.platba(self.TOP-47,self.LEFT+3)
		self.polozky(self.TOP-80,self.LEFT)
		self.datumy(self.TOP-10,self.LEFT+91)

		#self.pdf.setFillColorRGB(0, 0, 0)

		self.pdf.showPage()
		self.pdf.save()

#g = genInvoice(invoice.objects.all()[0])
#g.gen()

