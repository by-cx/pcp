# -*- coding: utf-8 -*-
from django.core.cache import cache

from os.path import join

from wsgiadmin.settings import *
from wsgiadmin.apacheconf.models import *
from wsgiadmin.requests.request import SSHHandler

from django.conf import settings

uwsgi = False

def user_directories(user, use_cache=False):

    dirs = []
    if use_cache:
        dirs = cache.get('user_directories_%s' % user.pk)

    if not dirs:
        sh = SSHHandler(user, user.parms.web_machine)
        dirs = sh.instant_run("/usr/bin/find %s -maxdepth 2 -type d" % user.parms.home)[0].split("\n")

        if dirs:
            cache.set('user_directories_%s' % user.pk, dirs, timeout=3600*24*7)

    return [d.strip() for d in dirs if d.strip() and not "/." in d]


def get_user_wsgis(user, use_cache=True):

    wsgis = []
    if use_cache:
        wsgis = cache.get('user_wsgis_%s' % user.pk)

    if not wsgis:
        sh = SSHHandler(user, user.parms.web_machine)
        wsgis = sh.instant_run("/usr/bin/find %s -maxdepth 5 -type f -name '*.wsgi'" % user.parms.home)[0]
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
        root_len = len(venv_location)
        output = sh.instant_run("/usr/bin/find %s -maxdepth 1 -type d" % venv_location)[0].split("\n")
        venvs = [one[root_len:] for one in output if one[root_len:]]

        if venvs:
            cache.set("user_venvs_%s" % user.pk, venvs, timeout=3600*24*7)

    return venvs


def gen_vhosts():
    first = []
    last = []

    content = ""

    for s in site.objects.filter(removed=False):
        if "*." in s.serverName or "*." in s.serverAlias:
            last.append(s)
        else:
            first.append(s)

    for s in first + last:
        if not s.owner.parms.enable: continue

        conf = []
        wsgi = True
        #wsgi,php,static

        try:
            s.wsgi
        except:
            wsgi = False

        if wsgi:
            configtype = "wsgi"
        elif s.php:
            configtype = "php"
        elif not s.php and s.documentRoot:
            configtype = "static"
        else:
            print "%s nevytvořeno" % s.serverName
            break

        if configtype == "php": conf.append("SuexecUserGroup %s %s" % (s.owner.username, s.owner.username))

        conf.append("ServerName " + s.serverName)
        if s.serverAlias: conf.append("ServerAlias " + s.serverAlias)
        if configtype in ["php", "static"]: conf.append("DocumentRoot " + s.documentRoot)

        conf.append("CustomLog /var/log/webs/access_%s.log combined" % s.serverName)
        conf.append("ErrorLog /var/log/webs/error_%s.log" % s.serverName)

        if wsgi and s.wsgi.allow_ips:
            ips = [x.strip() for x in s.wsgi.allow_ips.split("\n") if x]
            conf.append("<DirectoryMatch \".*\">")
            conf.append("Order Deny,Allow")

            for ip in ips:
                conf.append("Allow from %s" % ip)

            conf.append("Deny from all")
            conf.append("</DirectoryMatch>")

        if configtype == "wsgi" and s.wsgi.uwsgi:
            conf.append("<Location />")
            conf.append("\tSetHandler uwsgi-handler")
            conf.append("\tuWSGISocket %s" % s.wsgi.socket())
            conf.append("</Location>")

        else:
            if configtype == "wsgi": conf.append("WSGIDaemonProcess %s user=%s group=%s processes=%d threads=%d" % (
            s.serverName.replace(".", "_"), s.owner.username, s.owner.username, s.wsgi.processes, s.wsgi.threads))
            if configtype == "wsgi": conf.append("WSGIProcessGroup " + s.serverName.replace(".", "_"))
            if configtype == "wsgi": conf.append("WSGIScriptAlias / " + s.wsgi.script)

        for alias in s.alias_set.all():
            conf.append("Alias \"%s\" \"%s\"" % (alias.name, alias.directory))

        if configtype == "wsgi" and s.wsgi.append == "Django":
            conf.append("Alias \"/media/\"     \"/usr/lib/pymodules/python2.6/django/contrib/admin/media/\"")
            conf.append("<Directory /usr/lib/pymodules/python2.6/django/contrib/admin/media/>")
            conf.append("\tOrder deny,allow")
            conf.append("\tAllow from all")
            conf.append("</Directory>")
            conf.append("<Location /media/>")
            conf.append("\tSetHandler None")
            conf.append("</Location>")
        if configtype == "wsgi" and s.wsgi.static:
            for static in [x.strip().split(" ") for x in s.wsgi.static.split("\n") if not "#" in x]:
                print static
                if len(static) == 2 and len(static[0]) > 1 and static[0][0] == "/" and static[0][-1] == "/" and len(
                    static[1]) > 1 and static[1][0] == "/" and static[1][-1] == "/":
                    print "2", static
                    conf.append("Alias \"%s\"     \"%s\"" % (static[0], s.owner.parms.home + static[1]))
                    conf.append("<Directory \"%s\">" % (s.owner.parms.home + static[1]))
                    conf.append("\tOrder deny,allow")
                    conf.append("\tAllow from all")
                    conf.append("</Directory>")
                    conf.append("<Location \"%s\">" % (static[0]))
                    conf.append("\tSetHandler None")
                    conf.append("</Location>")

        for custom in [str(c.conf).split("\n") for c in s.custom_set.all()]:
            for customline in custom:
                conf.append(customline.strip())

        #if s.php: conf.append("PHP_Fix_Pathinfo_Enable 1")
        if s.documentRoot: conf.append("<Directory %s>" % s.documentRoot)
        options = ""
        if s.php: options += " +ExecCGI"
        if s.indexes: options += " +Indexes"
        if s.documentRoot: conf.append("\tOptions" + options)
        if s.documentRoot: conf.append("\tAllowOverride All")
        if s.documentRoot and configtype in ["php"]: conf.append("\tAddHandler fcgid-script .php")
        if s.documentRoot and configtype in ["php"]: conf.append(
            "\tFCGIWrapper /var/www/%s/php5-wrap .php" % s.owner.username)
        #if s.documentRoot and configtype in ["php"]: conf.append("\tAcceptPathInfo On")
        if s.documentRoot: conf.append("\tOrder deny,allow")
        if s.documentRoot: conf.append("\tAllow from all")
        if s.documentRoot: conf.append("</Directory>")

        for alias in s.alias_set.all():
            conf.append("<Directory %s>" % alias.directory)
            if alias.indexes: conf.append("\tOptions +Indexes")
            conf.append("\tOrder deny,allow")
            conf.append("\tAllow from all")
            conf.append("</Directory>")

        if configtype == "php": conf.append("IPCCommTimeout 360")

        content += "<VirtualHost *:80>\n"
        content += "\t" + "\n\t".join(conf)
        content += "\n</VirtualHost>\n\n"

        #Awstats
        awstats = ""
        awstats += "Include \"/etc/awstats.conf\"\n"
        awstats += "SiteDomain=\"%s\"\n" % s.serverName
        awstats += "LogFile=\"/var/log/webs/access_%s.log\"\n" % s.serverName

        f = open(ROOT + "awstats/awstats.%s.conf" % s.serverName, "w")
        f.write(awstats)
        f.close()

    return content


def gen_uwsgi_xml():
    uwsgi = []
    uwsgi.append("<rosti>")

    for w in wsgi.objects.filter(uwsgi=True):
        uwsgi.append("<uwsgi id=\"%d\">" % w.id)
        pp = w.site.owner.parms.home
        for pp in [w.site.owner.parms.home + x.strip() for x in w.python_path.split("\n") if x.strip()]:
            uwsgi.append("\t<pythonpath>%s</pythonpath>" % pp)
        uwsgi.append("\t<master/>")
        uwsgi.append("\t<no-orphans/>")
        uwsgi.append("\t<processes>%s</processes>" % w.processes)
        uwsgi.append("\t<optimize>0</optimize>")
        uwsgi.append("\t<home>%s</home>" % w.virtualenv_path())
        uwsgi.append("\t<limit-as>128</limit-as>")
        uwsgi.append("\t<chmod-socket>660</chmod-socket>")
        uwsgi.append("\t<uid>%s</uid>" % w.site.owner.username)
        uwsgi.append("\t<gid>%s</gid>" % w.site.owner.username)
        uwsgi.append("\t<pidfile>%s</pidfile>" % w.pidfile())
        uwsgi.append("\t<socket>%s</socket>" % w.socket())
        uwsgi.append("\t<wsgi-file>%s</wsgi-file>" % w.script)
        uwsgi.append("\t<daemonize>%s</daemonize>" % w.logfile())
        uwsgi.append("\t<chdir>%s</chdir>" % pp)

        uwsgi.append("</uwsgi>")

    uwsgi.append("</rosti>")

    return "\n".join(uwsgi)


def gen_nginx_conf():
    pass
