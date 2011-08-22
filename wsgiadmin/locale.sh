#!/bin/sh

APPS="useradmin bills invoices clients domains emails web ftps pgs mysql users apacheconf keystore"

for app in $APPS; do
	mkdir -p $app/locale/en
	cd $app
	python ../manage.py makemessages -l en
	python ../manage.py compilemessages
	cd ..
done
