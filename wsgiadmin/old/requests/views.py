# -*- coding: utf-8 -*-
from threading import Thread
import time

from django.http import HttpResponse

from wsgiadmin.old.requests.request import SSHHandler


class _commit(Thread):
    def run(self):
        # sleep because of web server restart/reload
        time.sleep(10)
        
        sh = SSHHandler(None, None)
        sh.commit()

        f = open("/tmp/committest", "w")
        f.write("ready")
        f.close()

def commit(request):
    object = _commit()
    object.start()

    return HttpResponse("OK")
