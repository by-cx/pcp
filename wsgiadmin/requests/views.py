from django.http import HttpResponse
from django.contrib.auth.models import User
from wsgiadmin.clients.models import Machine
from wsgiadmin.requests.request import SSHHandler

def commit(request):
    m = Machine.objects.all()[0]
    u = User.objects.all()[0]

    sh = SSHHandler(u, m)
    sh.commit()

    return HttpResponse("OK")
