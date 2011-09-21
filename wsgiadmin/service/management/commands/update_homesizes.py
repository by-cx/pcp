import logging
from django.core.management.base import BaseCommand
from wsgiadmin.keystore.tools import kset
from django.contrib.auth.models import User
from wsgiadmin.requests.tools import RawRequest

class Command(BaseCommand):
    help = "Update user homes size"

    def handle(self, *args, **options):
        for iu in User.objects.all():
            try:
                iu.parms
            except Exception, e:
                logging.info(u"Chybí parms uživatele %s" % iu.username)
                logging.warning("^ catch only %s, pls" % type(e))
                continue

            homedir = iu.parms.home
            if not homedir:
                logging.info(u"Chybí home uživatele %s" % iu.username)
                continue

            rr = RawRequest(iu.parms.web_machine.ip)
            data = rr.run("du -s %s" % homedir)["stdout"]

            if data:
                raw = data.strip()
                if not raw:
                    logging.info(u"Chybí home uživatele %s" % iu.username)
                    continue

                kset("%s:homesize" % iu.username, str(int(raw.split("\t")[0]) * 1024), 4320)
            else:
                logging.info(u"Chybí home uživatele %s" % iu.username)
