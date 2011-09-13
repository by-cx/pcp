# -*- coding: utf-8 -*-

import time, logging, urllib, json
from django.conf import settings

info = logging.info

class request_raw(object):
    server = ""

    def __init__(self, server):
        self.server = server

    def read_file(self, filename):
        params = urllib.urlencode({
            "key": settings.NODE_KEY,
            "action": "read_file",
            "filename": filename,
            })

        f = urllib.urlopen("http://%s:8999/" % self.server, params)
        ret = json.loads(f.read())
        f.close()

        info("Read file %s | Status: %s" % (filename, ret["status"]))

        return ret

    def remove_file(self, filename):
        params = urllib.urlencode({
            "key": settings.NODE_KEY,
            "action": "remove_file",
            "filename": filename,
            })

        f = urllib.urlopen("http://%s:8999/" % self.server, params)
        ret = json.loads(f.read())
        f.close()

        info("Remove file %s | Status: %s" % (filename, ret["status"]))

        return ret

    def save_file(self, filename, content):
        params = urllib.urlencode({
            "key": settings.NODE_KEY,
            "action": "save_file",
            "filename": filename,
            "content": content
        })

        f = urllib.urlopen("http://%s:8999/" % self.server, params)
        ret = json.loads(f.read())
        f.close()

        info("Save file %s | Status: %s" % (filename, ret["status"]))

        return ret

    def run(self, cmd, stdin=None):
        params = {
            "key": settings.NODE_KEY,
            "action": "cmd",
            "cmd": cmd
        }
        if stdin: params.update({"stdin": stdin})
        params = urllib.urlencode(params)

        f = urllib.urlopen("http://%s:8999/" % self.server, params)
        ret = json.loads(f.read())
        f.close()

        info("%s | Status: %s | stdout: %s | stderr: %s" % (cmd, ret["status"], ret["stdout"], ret["stderr"]))

        return ret


class request(request_raw):
    id = None
    datetime_insert = time.time()
    datetime_processed = 0
    status = "initiate"
    action = ""
    server = ""
    data = {}

    def __init__(self, action="", server="", data={}):
        self.action = action
        self.server = server
        self.data = data

    def done(self):
        self.status = "done"
        self.datetime_processed = time.time()

    def save(self):
        logging.info("Request %s" % self.action)

        if self.action == "uwsgi_config":
            filename = settings.UWSGI_CONF
            content = self.data["config"]
            self.save_file(filename, content)
        elif self.action == "uwsgi_start":
            self.run("/usr/bin/uwsgi-manager.py -s %s" % str(self.data["web_id"]))
        elif self.action == "uwsgi_restart":
            self.run("/usr/bin/uwsgi-manager.py -R %s" % str(self.data["web_id"]))
        elif self.action == "uwsgi_stop":
            self.run("/usr/bin/uwsgi-manager.py -S %s" % str(self.data["web_id"]))
        elif self.action == "uwsgi_reload":
            self.run("/usr/bin/uwsgi-manager.py -r %s" % str(self.data["web_id"]))
        #self.run("/usr/bin/uwsgi-manager.py -R %s" % str(self.data["web_id"]))

        elif self.action == "nginx_reload":
            content = self.data["vhosts"]
            self.save_file(settings.NGINX_CONF, content)
            self.run("touch /tmp/nginx_reload")
        elif self.action == "nginx_restart":
            content = self.data["vhosts"]
            self.save_file(settings.NGINX_CONF, content)
            self.run("touch /tmp/nginx_restart")
        elif self.action == "apache_reload":
            content = self.data["vhosts"]
            self.save_file(settings.APACHE_CONF, content)
            #self.run("chown www-data:www-data /etc/apache2/sites-enabled/99_auto.conf")
            #self.run("/etc/init.d/apache2 reload")
            self.run("touch /tmp/apache_reload")

        elif self.action == "apache_restart":
            content = self.data["vhosts"]
            self.save_file(settings.APACHE_CONF, content)
            #self.run("/etc/init.d/apache2 restart")
            self.run("touch /tmp/apache_restart")

        elif self.action == "bind_add_zone":
            info("Saving zone for %s" % self.data["domain"])
            filename = "/etc/bind/pri_auto/%s.zone" % self.data["domain"]
            content = self.data["zone"]
            self.save_file(filename, content)
            self.run("chown root:bind /etc/bind/pri_auto/%s.zone" % self.data["domain"])
            self.run("chmod 644 /etc/bind/pri_auto/%s.zone" % self.data["domain"])

        elif self.action == "bind_rm_zone":
            self.run("rm /etc/bind/pri_auto/%s.zone" % self.data["domain"])

        elif self.action == "bind_mod_config":
            info("Generating config")
            filename = "/etc/bind/named.local.auto"
            content = self.data["config"]
            self.save_file(filename, content)
            self.run("/etc/init.d/bind9 reload")

        elif self.action == "create_mailbox":
            info("Creating mailbox %s" % self.data["maildir"])
            self.run("/bin/mkdir -p %s" % self.data["homedir"])
            self.run("/bin/chown email:email %s -R" % self.data["homedir"])
            self.run("/usr/bin/maildirmake %s" % self.data["maildir"])
            self.run("/bin/chown email:email %s -R" % self.data["maildir"])
            self.run("/usr/bin/maildirmake %s" % self.data["maildir"] + "/.Spam")
            self.run("/bin/chown email:email %s -R" % self.data["maildir"] + "/.Spam")

        elif self.action == "pg_add_db":
            self.run("createuser -D -R -S %s" % self.data["dbname"])
            self.run("createdb -O %s %s" % (self.data["dbname"], self.data["dbname"]))
            sql = "ALTER USER %s WITH PASSWORD '%s';" % (self.data["dbname"], self.data["dbpass"])
            self.run("psql template1", stdin=sql)
            self.data["dbpass"] = "******"

        elif self.action == "pg_rm_db":
            self.run("dropdb %s" % self.data["dbname"])
            self.run("dropuser %s" % self.data["dbname"])

        elif self.action == "pg_passwd_db":
            sql = "ALTER USER %s WITH PASSWORD '%s';" % (self.data["dbname"], self.data["dbpass"])
            self.run("psql template1", stdin=sql)
            self.data["dbpass"] = "******"

        if self.action == "my_add_db":
            db = self.data["dbname"]
            passwd = self.data["dbpass"]
            sql = []

            sql.append("CREATE DATABASE %s;" % db)
            sql.append("CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';" % (db, passwd))
            sql.append("GRANT ALL PRIVILEGES ON %s.* TO '%s'@'localhost' WITH GRANT OPTION;" % (db, db))

            for x in sql:
                self.run("mysql -u root", stdin=x)

            self.data["dbpass"] = "******"

        elif self.action == "my_rm_db":
            db = self.data["dbname"]
            sql = []

            sql.append("DROP DATABASE %s;" % db)
            sql.append("DROP USER '%s'@'localhost';" % db)

            for x in sql:
                self.run("mysql -u root", stdin=x)

        elif self.action == "my_passwd_db":
            db = self.data["dbname"]
            passwd = self.data["dbpass"]
            sql = []

            sql.append("DROP USER '%s'@'localhost';" % db)
            sql.append("CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';" % (db, passwd))
            sql.append("GRANT ALL PRIVILEGES ON %s.* TO '%s'@'localhost' WITH GRANT OPTION;" % (db, db))

            for x in sql:
                self.run("mysql -u root", stdin=x)

            self.data["dbpass"] = "******"

        elif self.action == "ssh_passwd":
            username = self.data["username"]
            password = self.data["password"]

            self.run("/usr/sbin/chpasswd", stdin="%s:%s" % (username, password))

        self.done()

#if __name__ == "__main__":
#	r = request()
#	r.datetime_insert = time.time()
#	r.datetime_processed = 0
#	r.status = "initiate"
#	r.action = "test"
#	r.server = "89.111.104.66"
#	r.data = {"tid":1}
#	r.save()
