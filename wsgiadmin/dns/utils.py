from constance import config
from wsgiadmin.dns.models import Record

def set_domain_default_state(domain):
    for record in domain.record_set.all():
        record.delete()

    record = Record()
    record.name = "@"
    record.record_type = "A"
    record.value = config.dns_default_a
    record.ttl = config.dns_default_record_ttl
    record.domain = domain
    record.save()

    record = Record()
    record.name = "@"
    record.record_type = "AAAA"
    record.value = config.dns_default_aaaa
    record.ttl = config.dns_default_record_ttl
    record.domain = domain
    record.save()

    record = Record()
    record.name = "@"
    record.record_type = "MX"
    record.value = config.dns_default_mx if config.dns_default_mx[-1] == "." else "%s." % config.dns_default_mx
    record.ttl = config.dns_default_record_ttl
    record.domain = domain
    record.prio = 10
    record.save()

    record = Record()
    record.name = "www"
    record.record_type = "CNAME"
    record.value = "@"
    record.ttl = config.dns_default_record_ttl
    record.domain = domain
    record.save()

