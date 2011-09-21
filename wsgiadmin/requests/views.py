from django.http import HttpResponse
from django.contrib.auth.models import User
from wsgiadmin.clients.models import Machine
from wsgiadmin.requests.request import SSHHandler

def commit(request):
    sh = SSHHandler(None, None)
    sh.commit()

    return HttpResponse("OK")
