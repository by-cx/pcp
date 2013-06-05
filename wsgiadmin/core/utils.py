from wsgiadmin.core.exceptions import PCPException
from wsgiadmin.core.models import Server, Capability


def server_chooser(capname, hidden=True):
    capability = Capability.objects.get(name=capname)
    if hidden:
        return Server.objects.filter(capabilities__in=[capability.id]).order_by("priority")
    else:
        return Server.objects.filter(capabilities__in=[capability.id], hide=False).order_by("priority")


def get_mail_server():
    servers = server_chooser("mail")
    if len(servers) > 1:
        raise PCPException("Error: more than one mail server is not allowed")
    elif len(servers) == 0:
        raise PCPException("Error: no mail server found")
    else:
        return servers[0]


def get_virt_servers():
    servers = server_chooser("virt")
    return servers


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
    return servers
    #if len(servers) == 0:
    #    raise PCPException("Error: no loadbalancer found")
    #else:
    #    return servers

def get_mysql_server():
    servers = server_chooser("mysql")
    if len(servers) == 0:
        raise PCPException("Error: no MySQL server found")
    else:
        return servers

def get_pgsql_server():
    servers = server_chooser("pgsql")
    if len(servers) == 0:
        raise PCPException("Error: no PostgreSQL server found")
    else:
        return servers
