from constance import config
from django.template.loader import render_to_string
from wsgiadmin.core.backend_base import Script
from wsgiadmin.core.utils import get_primary_ns_server, get_secondary_ns_servers
from wsgiadmin.dns.models import Domain


class DomainException(Exception): pass


class DomainObject(object):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(DomainObject, self).__init__(*args, **kwargs)
        self.script_master = Script(get_primary_ns_server())
        self.scripts_slaves = []
        for ns in get_secondary_ns_servers():
            self.scripts_slaves.append(Script(ns))

    def commit(self):
        self.script_master.commit()
        for slave in self.scripts_slaves:
            slave.commit()

    def reload(self):
        self.script_master.add_cmd("/etc/init.d/bind9 reload")
        for slave in self.scripts_slaves:
            slave.add_cmd("/etc/init.d/bind9 reload")

    def update(self, domain=None):
        if domain:
            self.script_master.add_file("%s/%s.zone" % (config.bind_master_zones_dir, domain.name), self.gen_zone(domain))
        self.script_master.add_file(config.bind_master_config_file, self.gen_master_config())
        for slave in self.scripts_slaves:
            slave.add_file(config.bind_slave_config_file, self.gen_slave_config())

    def uninstall(self, domain):
        self.script_master.add_cmd("rm %s/%s.zone" % (config.bind_master_zones_dir, domain.name))
        for slave in self.scripts_slaves:
            slave.add_cmd("rm %s/%s.zone" % (config.bind_slave_zones_dir, domain.name))

    def gen_zone(self, domain):
        domain.new_serial()
        records = []
        for ns in [get_primary_ns_server().domain] + [x.domain for x in get_secondary_ns_servers()]:
            records.append({"name": "@", "TTL": domain.ttl if domain.ttl else 86400, "type": "NS", "prio": "", "value": "%s." % ns})
        for record in domain.record_set.order_by("order_num"):
            records.append({
                "name": record.name,
                "TTL": record.ttl if record.ttl else 86400,
                "type": record.record_type,
                "prio": record.prio if record.prio else "",
                "value": record.value,
            })
        return render_to_string("dns/zone.txt", {
            "records": records,
            "TTL": domain.ttl if domain.ttl else 86400,
            "ns1": get_primary_ns_server().domain,
            "rname": domain.rname.replace("@", "."),
            "serial": domain.serial,
            "refresh": config.dns_refresh,
            "retry": config.dns_retry,
            "expire": config.dns_expire,
            "minimum": config.dns_minimum,
        })

    def gen_master_config(self):
        domains = []
        for domain in Domain.objects.all():
            domains.append(render_to_string("dns/master_config.txt", {
                "domain": domain.name,
                "slaves_ips": ";".join([x.ip for x in get_secondary_ns_servers()]),
            }))
        return "\n".join(domains)

    def gen_slave_config(self):
        domains = []
        for domain in Domain.objects.all():
            domains.append(render_to_string("dns/slave_config.txt", {
                "domain": domain.name,
                "msters_ips": get_primary_ns_server().ip,
            }))
        return "\n".join(domains)
