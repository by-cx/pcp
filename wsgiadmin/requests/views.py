from django.http import HttpResponse
from wsgiadmin.requests.request import SSHHandler

def commit(request):
    sh = SSHHandler(None, None)
    sh.commit()

    return HttpResponse("OK")
