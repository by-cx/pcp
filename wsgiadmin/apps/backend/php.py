import os
import re
from constance import config
from django.conf import settings
from wsgiadmin.apps.backend.main import AppBackend, AppException


class PHPApp(AppBackend):
    class Meta:
        proxy = True

    def install(self):
        super(PHPApp, self).install()
        parms = self.get_parmameters()
        self.script.add_cmd("mkdir -p %(home)s/fcgid" % parms, user=self.get_user())
        self.script.add_cmd("mkdir -p /var/www/%(user)s/" % parms)
        self.script.add_cmd("chown %(user)s:%(group)s /var/www/%(user)s/" % parms)

    def disable(self):
        super(PHPApp, self).disable()
        parms = self.get_parmameters()
        self.script.add_cmd("rm /etc/apache2/apps.d/%(user)s.conf" % parms)
        self.script.add_cmd("rm /etc/nginx/apps.d/%(user)s.conf" % parms)
        self.script.reload_apache()
        self.script.reload_nginx()

    def enable(self):
        super(PHPApp, self).enable()

    def uninstall(self):
        super(PHPApp, self).uninstall()
        parms = self.get_parmameters()
        self.script.add_cmd("rm /etc/apache2/apps.d/%(user)s.conf" % parms)
        self.script.add_cmd("rm /etc/nginx/apps.d/%(user)s.conf" % parms)
        self.script.add_cmd("rm /var/www/%(user)s/ -r" % parms)
        self.script.reload_apache()
        self.script.reload_nginx()

    def update(self):
        super(PHPApp, self).update()
        parms = self.get_parmameters()
        self.script.add_file("/etc/apache2/apps.d/%(user)s.conf" % parms, self.gen_apache_config())
        self.script.add_file("/etc/nginx/apps.d/%(user)s.conf" % parms, self.gen_nginx_config())
        self.script.add_file("/var/www/%(user)s/php-wrap" % parms, self.gen_php_wrap(), owner=self.get_user())
        self.script.add_file("/var/www/%(user)s/php.ini" % parms, self.gen_php_ini(), owner=self.get_user())
        self.script.add_cmd("chmod 555 /var/www/%(user)s/php-wrap" % parms)
        self.script.add_cmd("chown %(user)s:%(group)s /var/www/%(user)s/php-wrap" % parms)
        self.script.add_cmd("chmod 444 /var/www/%(user)s/php.ini" % parms)
        self.script.add_cmd("chown %(user)s:%(group)s /var/www/%(user)s/php.ini" % parms)
        self.script.reload_nginx()
        self.script.reload_apache()

    def gen_php_wrap(self):
        parms = self.get_parmameters()
        content = []
        content.append("#!/bin/sh")
        content.append("PHP_FCGI_CHILDREN=2")
        content.append("export PHP_FCGI_CHILDREN")
        content.append("PHP_FCGI_MAX_REQUESTS=400")
        content.append("export PHP_FCGI_MAX_REQUESTS")
        content.append("PHPRC=/var/www/%(user)s/php.ini" % parms)
        content.append("export PHPRC")
        content.append("exec /usr/bin/php-cgi\n")
        return "\n".join(content)

    def gen_php_ini(self):
        parms = self.get_parmameters()
        content = []
        content.append("%s" % self.script.run("cat %s" % settings.PHP_INI_PATH)["stdout"])
        content.append("error_log = %(home)s/logs/php.log" % parms)
        content.append("memory_limit = %s" % parms.get("memory_limit", "32M"))
        content.append("post_max_size = %s" % parms.get("post_max_size", "32M"))
        content.append("upload_max_filesize = %s" % parms.get("upload_max_filesize", "10"))
        content.append("max_file_uploads = %s" % parms.get("max_file_uploads", "10"))
        content.append("max_execution_time = %s" % parms.get("max_execution_time", "20"))
        content.append("allow_url_fopen = %s" % ("On" if parms.get("allow_url_fopen") else "Off"))
        content.append("display_errors = %s\n" % ("On" if parms.get("display_errors") else "Off"))
        return "\n".join(content)

    def gen_apache_config(self):
        parms = self.get_parmameters()
        content = []
        content.append("<VirtualHost %s>" % config.apache_url)
        content.append("\tSuexecUserGroup %(user)s %(group)s" % parms)
        content.append("\tServerName %(main_domain)s" % parms)
        if parms.get("misc_domains"):
            content.append("\tServerAlias %(misc_domains)s" % parms)
        content.append("\tDocumentRoot %(home)s/app/" % parms)
        content.append("\tCustomLog %(home)s/logs/access.log combined" % parms)
        content.append("\tErrorLog %(home)s/logs/error.log" % parms)
        content.append("\t<Directory %(home)s/app/>" % parms)
        content.append("\t\tOptions +ExecCGI %s" % "+Indexes" if parms.get("flag_index") else "")
        content.append("\t\tAllowOverride All")
        content.append("\t\tAddHandler fcgid-script .php")
        content.append("\t\tFCGIWrapper /var/www/%(user)s/php-wrap .php" % parms)
        content.append("\t\tOrder deny,allow")
        content.append("\t\tAllow from all")
        content.append("\t</Directory>")
        content.append("\tIPCCommTimeout 360")
        content.append("</VirtualHost>\n")
        return "\n".join(content)

    def gen_nginx_config(self):
        parms = self.get_parmameters()
        content = []
        content.append("server {")
        if self.core_server.os in ("archlinux", "gentoo", ):
            content.append("\tlisten       *:80;")
        else:
            content.append("\tlisten       [::]:80;")
        content.append("\tserver_name  %(domains)s;" % parms)
        content.append("\taccess_log %(home)s/logs/access.log;"% parms)
        content.append("\terror_log %(home)s/logs/error.log;"% parms)
        content.append("\tlocation / {")
        content.append("\t\tproxy_pass         http://%s/;" % config.apache_url)
        content.append("\t\tproxy_redirect     default;")
        content.append("\t\tproxy_set_header   X-Real-IP  $remote_addr;")
        content.append("\t\tproxy_set_header   Host       $host;")
        content.append("\t}")
        if parms.get("static_maps"):
            for location, directory in [(x.split()[0].strip(), x.split()[1].strip()) for x in parms.get("static_maps").split("\n") if len(x.split()) == 2]:
                if re.match("/[a-zA-Z0-9_\-\.]*/", location) and re.match("/[a-zA-Z0-9_\-\.]*/", directory):
                    content.append("\tlocation %s {" % location)
                    content.append("\t\talias %s;" % os.path.join(parms.get("home"), "app", directory[1:]))
                    content.append("\t}")
        content.append("}\n")
        return "\n".join(content)


class PHPFPMApp(AppBackend):
    class Meta:
        proxy = True

    def install(self):
        super(PHPFPMApp, self).install()
        parms = self.get_parmameters()
        self.script.add_cmd("mkdir -p %(home)s" % parms, user=self.get_user())

    def disable(self):
        super(PHPFPMApp, self).disable()
        parms = self.get_parmameters()
        self.script.add_cmd("rm /etc/apache2/apps.d/%(user)s.conf" % parms)
        self.script.add_cmd("rm /etc/nginx/apps.d/%(user)s.conf" % parms)
        self.script.add_cmd("rm /etc/php5/fpm/pool.d/%(user)s.conf" % parms)
        self.script.reload_apache()
        self.script.reload_nginx()
        self.disabled = True
        self.save()

    def enable(self):
        super(PHPFPMApp, self).enable()

    def uninstall(self):
        super(PHPFPMApp, self).uninstall()
        parms = self.get_parmameters()
        self.script.add_cmd("rm /etc/apache2/apps.d/%(user)s.conf" % parms)
        self.script.add_cmd("rm /etc/nginx/apps.d/%(user)s.conf" % parms)
        self.script.add_cmd("rm /etc/php5/fpm/pool.d/%(user)s.conf" % parms)
        self.script.reload_apache()
        self.script.reload_nginx()

    def update(self):
        super(PHPFPMApp, self).update()
        parms = self.get_parmameters()
        self.script.add_file("/etc/apache2/apps.d/%(user)s.conf" % parms, self.gen_apache_config())
        self.script.add_file("/etc/nginx/apps.d/%(user)s.conf" % parms, self.gen_nginx_config())
        # TODO: I think this will work just for debian
        self.script.add_file("/etc/php5/fpm/pool.d/%(user)s.conf" % parms, self.gen_fpm_config())
        self.script.reload_nginx()
        self.script.reload_apache()
        self.php_fpm_reload()

    def gen_fpm_config(self):
        parms = self.get_parmameters()
        content = []
        content.append("[%(user)s]" % parms)
        content.append("user = %(user)s" % parms)
        content.append("group = %(group)s" % parms)
        content.append("")
        content.append("listen = 127.0.0.1:%d" % (10000 + self.app.id))
        content.append("")
        content.append("pm = dynamic")
        content.append("pm.max_children = 5")
        content.append("pm.start_servers = 1")
        content.append("pm.min_spare_servers = 1")
        content.append("pm.max_spare_servers = 2")
        content.append("pm.max_requests = 500")
        content.append("")
        content.append("slowlog = %(home)s/logs/slow_scripts.log" % parms)
        content.append("request_slowlog_timeout = 10s")
        content.append("request_terminate_timeout = %s" % parms.get("max_execution_time", "20"))
        content.append("rlimit_files = 1024")
        content.append("chdir = %(home)s" % parms)
        content.append("")
        content.append("php_admin_value[sendmail_path] = /usr/sbin/sendmail -t -i -f %s(user)@localhost" % parms)
        content.append("php_admin_value[error_log] = %(home)s/logs/php.log" % parms)
        content.append("php_admin_value[max_execution_time] = %s" % parms.get("max_execution_time", "20"))
        content.append("php_admin_value[max_file_uploads] = %s" % parms.get("max_file_uploads", "10"))
        content.append("php_admin_value[upload_max_filesize] = %s" % parms.get("upload_max_filesize", "10"))
        content.append("php_admin_value[post_max_size] = %s" % parms.get("post_max_size", "32M"))
        content.append("php_admin_value[memory_limit] = %s" % parms.get("memory_limit", "32M"))
        content.append("php_admin_flag[allow_url_fopen] = %s" % ("On" if parms.get("allow_url_fopen") else "Off"))
        content.append("php_admin_flag[display_errors] = %s" % ("On" if parms.get("display_errors") else "Off"))
        return "\n".join(content)

    def gen_apache_config(self):
        parms = self.get_parmameters()
        content = []
        content.append("<VirtualHost %s>" % config.apache_url)
        content.append("\tSuexecUserGroup %(user)s %(group)s" % parms)
        content.append("\tServerName %(main_domain)s" % parms)
        if parms.get("misc_domains"):
            content.append("\tServerAlias %(misc_domains)s" % parms)
        content.append("\tDocumentRoot %(home)s/app/" % parms)
        content.append("\tCustomLog %(home)s/logs/access.log combined" % parms)
        content.append("\tErrorLog %(home)s/logs/error.log" % parms)
        content.append("\t<Directory %(home)s/app/>" % parms)
        if parms.get("flag_index"): content.append("\t\tOptions +Indexes")
        content.append("\t\tAllowOverride All")
        content.append("\t\tOrder deny,allow")
        content.append("\t\tAllow from all")
        content.append("\t</Directory>")
        content.append("\tProxyPassMatch ^/(.*\.php(/.*)?)$ fcgi://127.0.0.1:%d%s/$1" % (1000 + self.app.id))
        content.append("</VirtualHost>\n")
        return "\n".join(content)

    def gen_nginx_config(self):
        parms = self.get_parmameters()
        content = []
        content.append("server {")
        if self.core_server.os in ("archlinux", "gentoo", ):
            content.append("\tlisten       *:80;")
        else:
            content.append("\tlisten       [::]:80;")
        content.append("\tserver_name  %(domains)s;" % parms)
        content.append("\taccess_log %(home)s/logs/access.log;"% parms)
        content.append("\terror_log %(home)s/logs/error.log;"% parms)
        content.append("\tlocation / {")
        content.append("\t\tproxy_pass         http://%s/;" % config.apache_url)
        content.append("\t\tproxy_redirect     default;")
        content.append("\t\tproxy_set_header   X-Real-IP  $remote_addr;")
        content.append("\t\tproxy_set_header   Host       $host;")
        content.append("\t}")
        content.append("}\n")
        return "\n".join(content)

    def php_fpm_reload(self):
        if self.app.core_server.os in ("debian6", "debian7", ):
            self.script.add_cmd("/etc/init.d/php5-fpm reload")
        # TODO: support for Arch Linux
        else:
            raise AppException("Unknown server OS")
