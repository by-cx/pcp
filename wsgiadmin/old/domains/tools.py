def domains_list(user, used=[]):
    domains = user.domain_set.filter(parent=None).order_by("name")
    list_of_domains = []

    for domain in domains:
        list_of_domains.append(domain)
        list_of_domains += list(domain.subdomains.order_by("name"))

    if used:
        new_list = []
        for domain in list_of_domains:
            if domain not in used:
                new_list.append(domain)
        list_of_domains = new_list

    return list_of_domains

def used_domains(user, ignore=None):
    used = []
    for site in user.usersite_set.all():
        if ignore and site == ignore: continue
        used += [site.main_domain] + list(site.misc_domains.all())
    return used
