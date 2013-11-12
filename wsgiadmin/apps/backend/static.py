from wsgiadmin.apps.backend.main import AppBackend


class StaticApp(AppBackend):

    class Meta:
        proxy = True

    def disable(self):
        super(StaticApp, self).disable()
        parms = self.get_parmameters()
        self.script.add_cmd("rm /etc/nginx/apps.d/%(user)s.conf" % parms)
        self.script.reload_nginx()
        self.disabled = True
        self.save()

    def enable(self):
        super(StaticApp, self).enable()

    def uninstall(self):
        super(StaticApp, self).uninstall()
        parms = self.get_parmameters()
        self.script.add_cmd("rm /etc/nginx/apps.d/%(user)s.conf" % parms)
        self.script.reload_nginx()

    def update(self):
        super(StaticApp, self).update()
        parms = self.get_parmameters()
        self.script.add_file("/etc/nginx/apps.d/%(user)s.conf" % parms, self.gen_nginx_config())
        self.script.reload_nginx()

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
        content.append("\troot %(home)s/app;"% parms)
        if parms.get("flag_index"):
            content.append("\tautoindex on;")
        else:
            content.append("\tautoindex off;")
        content.append("\tindex index.html index.htm default.html default.htm;")
        content.append("}\n")
        return "\n".join(content)