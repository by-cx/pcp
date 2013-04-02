from wsgiadmin.core.exceptions import PCPException
from wsgiadmin.core.models import Server, Capability


def server_chooser(capname):
    capability = Capability.objects.get(name=capname)
    return Server.objects.filter(capabilities__in=[capability.id])


def get_mail_server():
    servers = server_chooser("mail")
    if len(servers) > 1:
        raise PCPException("Error: more than one mail server is not allowed")
    elif len(servers) == 0:
        raise PCPException("Error: no mail server found")
    else:
        return servers[0]


def get_primary_ns_server():
    servers = server_chooser("ns_primary")
    if len(servers) > 1:
        raise PCPException("Error: more than one primary NS server is not allowed")
    elif len(servers) == 0:
        raise PCPException("Error: no primary NS server found")
    else:
        return servers[0]

def get_secondary_ns_servers():
    servers = server_chooser("ns_secondary")
    if len(servers) == 0:
        raise PCPException("Error: no secondary NS server found")
    else:
        return servers

def get_load_balancers():
    servers = server_chooser("load_balancer")
    if len(servers) == 0:
        raise PCPException("Error: no loadbalancer found")
    else:
        return servers