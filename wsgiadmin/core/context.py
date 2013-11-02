from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from wsgiadmin.core.models import Server


def django_settings(request):
    return {'settings': settings}

def capabilities(request):
    capabilities_list = cache.get('server_capabilities')
    if not capabilities_list:
        capabilities_list = []
        if request.user.is_authenticated():
            servers = Server.objects.filter(Q(user=None)|Q(user=request.user))
        else:
            servers = Server.objects.filter(user=None)
        for server in servers:
            for capability in server.capabilities.all():
                if capability.name not in capabilities_list:
                    capabilities_list.append(capability.name)
        cache.set("server_capabilities", capabilities_list)
    return {'capabilities': capabilities_list}