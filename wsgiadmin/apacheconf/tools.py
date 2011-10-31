from os.path import join

from wsgiadmin.requests.request import SSHHandler, NginxRequest, ApacheRequest

from django.conf import settings
from django.core.cache import cache

def user_directories(user, use_cache=False):

    dirs = []
    if use_cache:
        dirs = cache.get('user_directories_%s' % user.pk)

    if not dirs:
        sh = SSHHandler(user, user.parms.web_machine)
        dirs = sh.run("/usr/bin/find %s -maxdepth 2 -type d" % user.parms.home, instant=True)[0].split("\n")

        if dirs:
            cache.set('user_directories_%s' % user.pk, dirs, timeout=3600*24*7)

    return [d.strip() for d in dirs if d.strip() and not "/." in d]


def get_user_wsgis(user, use_cache=True):

    wsgis = []
    if use_cache:
        wsgis = cache.get('user_wsgis_%s' % user.pk)

    if not wsgis:
        sh = SSHHandler(user, user.parms.web_machine)
        wsgis = sh.run("/usr/bin/find %s -maxdepth 5 -type f -name '*.wsgi'" % user.parms.home, instant=True)[0]
        wsgis = [one.strip() for one in wsgis.split("\n") if one]

        if wsgis:
            cache.set('user_wsgis_%s' % user.pk, wsgis, timeout=3600*24*7)

    return wsgis


def get_user_venvs(user, use_cache=True):

    venvs = []
    if use_cache:
        venvs = cache.get('user_venvs_%s' % user.pk)

    if not venvs:
        sh = SSHHandler(user, user.parms.web_machine)
        venv_location = join(user.parms.home, settings.VIRTUALENVS_DIR)
        root_len = len(venv_location) + 1
        output = sh.run("/usr/bin/find %s -maxdepth 1 -type d" % venv_location, instant=True)[0].split("\n")
        venvs = [one[root_len:] for one in output if one[root_len:]]

        if venvs:
            cache.set("user_venvs_%s" % user.pk, venvs, timeout=3600*24*7)

    return venvs

def restart_master(config_mode, user):
    if 'nginx' in config_mode:
        nr = NginxRequest(user, user.parms.web_machine)
        nr.mod_vhosts()
        nr.reload()
    else:
        ar = ApacheRequest(user, user.parms.web_machine)
        ar.mod_vhosts()
        ar.reload()
