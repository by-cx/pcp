from django.conf import settings
from wsgiadmin.apps.backend import AppBackend


class NodeApp(AppBackend):

    class Meta:
        proxy = True

    def get_port(self):
        return settings.GUNICORN_PROXY_PORT + self.id

    def get_parmameters(self):
        parms = super(NodeApp, self).get_parmameters()
        parms["port"] = self.get_port()
        return parms

    def install(self):
        super(NodeApp, self).install()
        parms = self.get_parmameters()
        self.script.add_cmd("tee -a %(home)s/.bashrc" % parms, user=self.get_user(), stdin="\n\nexport PATH=$PATH:~/node_bin/bin/\n")
        self.script.add_cmd("cp -a /opt/node-%(version)s %(home)s/node_bin" % parms, user=self.get_user())

    def update(self):
        super(NodeApp, self).update()
        parms = self.get_parmameters()
        self.script.add_file("/etc/supervisor/apps.d/%(user)s.conf" % parms, self.gen_supervisor_config())
        self.script.add_file("/etc/nginx/apps.d/%(user)s.conf" % parms, self.gen_nginx_config())
        self.script.reload_nginx()

    def disable(self):
        super(NodeApp, self).disable()
        parms = self.get_parmameters()
        self.stop()
        self.script.add_cmd("rm /etc/nginx/apps.d/%(user)s.conf" % parms)
        self.script.reload_nginx()

    def enable(self):
        self.update()
        super(NodeApp, self).enable()

    def uninstall(self):
        super(NodeApp, self).uninstall()
        parms = self.get_parmameters()
        self.stop()
        self.script.add_cmd("rm /etc/supervisor/apps.d/%(user)s.conf" % parms)
        self.script.add_cmd("rm /etc/nginx/apps.d/%(user)s.conf" % parms)
        self.script.add_cmd("supervisorctl reread")
        self.script.add_cmd("supervisorctl update")

    def gen_supervisor_config(self):
        parms = self.get_parmameters()
        content = []
        content.append("[program:%(user)s]" % parms)
        content.append("command=/home/apps/%(user)s/node_bin/bin/npm start" % parms)
        content.append("directory=%(home)s/app" % parms)
        content.append("process_name=%(user)s" % parms)
        content.append("user=%(user)s" % parms)
        content.append("group=%(group)s" % parms)
        content.append("stdout_logfile=%(home)s/logs/stdout.log" % parms)
        content.append("stdout_logfile_maxbytes=2MB")
        content.append("stdout_logfile_backups=5")
        content.append("stdout_capture_maxbytes=2MB")
        content.append("stdout_events_enabled=false")
        content.append("stderr_logfile=%(home)s/logs/stderr.log" % parms)
        content.append("stderr_logfile_maxbytes=2MB")
        content.append("stderr_logfile_backups=5")
        content.append("stderr_capture_maxbytes=2MB")
        content.append("stderr_events_enabled=false\n")
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
        content.append("\t\tproxy_pass         http://127.0.0.1:%d/;" % self.get_port())
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

    def start(self):
        parms = self.get_parmameters()
        self.script.add_cmd("supervisorctl reread")
        self.script.add_cmd("supervisorctl update")
        # should be needed, but for sure in some cases
        self.script.add_cmd("supervisorctl start %(user)s" % parms)

    def restart(self):
        parms = self.get_parmameters()
        self.script.add_cmd("supervisorctl reread")
        self.script.add_cmd("supervisorctl update")
        self.script.add_cmd("supervisorctl restart %(user)s" % parms)

    def stop(self):
        parms = self.get_parmameters()
        self.script.add_cmd("supervisorctl stop %(user)s" % parms)
