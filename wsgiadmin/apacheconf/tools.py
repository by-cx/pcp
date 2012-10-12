from os.path import join

from wsgiadmin.requests.request import SSHHandler, NginxRequest, ApacheRequest, UWSGIRequest
from constance import config

from django.conf import settings
from django.core.cache import cache
from wsgiadmin.stats.tools import pay

def user_directories(user, use_cache=False):

    dirs = None
    if use_cache:
        dirs = cache.get('user_directories_%s' % user.pk)

    if dirs is None:
        sh = SSHHandler(user, user.parms.web_machine)
        dirs = sh.run("/usr/bin/find -L %s -maxdepth %d -type d" % (user.parms.home, config.find_directory_deep), instant=True)[0].split("\n")

        cache.set('user_directories_%s' % user.pk, dirs, timeout=3600*24*7)

    return [d.strip() for d in dirs if d.strip() and not "/." in d]


def get_user_wsgis(user, use_cache=True):

    wsgis = None
    if use_cache:
        wsgis = cache.get('user_wsgis_%s' % user.pk)

    if wsgis is None:
        sh = SSHHandler(user, user.parms.web_machine)
        wsgis = sh.run("/usr/bin/find %s -maxdepth 5 -type f -iname '*.wsgi'" % user.parms.home, instant=True)[0]
        wsgis = [one.strip() for one in wsgis.split("\n") if one]
        cache.set('user_wsgis_%s' % user.pk, wsgis, timeout=3600*24*7)

    return wsgis


def get_user_venvs(user, use_cache=True):

    venvs = None
    if use_cache:
        venvs = cache.get('user_venvs_%s' % user.pk)

    if venvs is None:
        sh = SSHHandler(user, user.parms.web_machine)
        venv_location = join(user.parms.home, settings.VIRTUALENVS_DIR)
        root_len = len(venv_location) + 1
        output = sh.run("/usr/bin/find %s -maxdepth 1 -type d" % venv_location, instant=True)[0].split("\n")
        venvs = [one[root_len:] for one in output if one[root_len:]]

        cache.set("user_venvs_%s" % user.pk, venvs, timeout=3600*24*7)

    return venvs

def restart_master(config_mode, user):
    if 'nginx' in config_mode:
        nr = NginxRequest(user, user.parms.web_machine)
        nr.mod_vhosts()
        nr.reload()
    if 'apache' in config_mode:
        ar = ApacheRequest(user, user.parms.web_machine)
        ar.mod_vhosts()
        ar.reload()

def remove_app_preparation(app, remove_domains=True):
    if app.pay:
        pay(app.owner, app.type, "Last payment for this site - %s" % app.main_domain.domain_name, app.pay)

    #Signal
    restart_master(config.mode, app.owner)

    if app.type == "uwsgi":
        ur = UWSGIRequest(app.owner,  app.owner.parms.web_machine)
        ur.stop(app, instant=True)
        ur.mod_config()

    if remove_domains:
        for sitedomain in app.sitedomain_set.all():
            sitedomain.delete()