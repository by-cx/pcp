import json
import logging
from subprocess import Popen, PIPE
import threading
from django.conf import settings
from wsgiadmin.apps.models import Log


class ScriptException(Exception): pass


class Script(object):
    def __init__(self, server):
        """
            Type:
                cmd: run given cmd          parms: cmd, stdin, user*, stdin*
                file: write new file        parms: path, content, owner*

            [
                {"type": "file", "path": "/tmp/test", "content": "testfile"},
                {"type": "cmd", "cmd": "/sbin/reboot". "owner": "cx:cx"},
            ]
        """
        self.requests = []
        self.reloads = {"apache": False, "nginx": False}
        self.restarts = {"apache": False, "nginx": False}
        self.log = []
        self.server = server

    def send(self, cmd, stdin=None):
        if settings.DEBUG:
            print "[cmd]: %s" % " ".join(["ssh", self.server]+cmd)
            logging.info("[cmd]: %s" % " ".join(["ssh", self.server]+cmd))
            if stdin:
                print "[stdin]: %s" % stdin
                logging.info("[stdin]: %s" % stdin)
        p = Popen(["ssh", self.server]+cmd, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        stdout, stderr = p.communicate(stdin)
        if not stderr:
            return json.loads(stdout)
        if settings.DEBUG:
            if stdout:
                print "[stdout]: %s" % stdout
                logging.info("[stdout]: %s" % stdout)
            if stderr:
                print "[stderr]: %s" % stderr
                logging.info("[stderr]: %s" % stderr)
            print "---"
        raise ScriptException("PCP runner script error: %s" % stderr)

    def commit(self):
        if self.restarts["nginx"]:
            self.add_cmd("/etc/init.d/nginx restart")
            self.reloads["nginx"] = False
            self.restarts["nginx"] = False
        elif self.reloads["nginx"]:
            self.add_cmd("/etc/init.d/nginx reload")
            self.reloads["nginx"] = False
        if self.restarts["apache"]:
            self.add_cmd("/etc/init.d/apache2 restart")
            self.reloads["apache"] = False
            self.restarts["apache"] = False
        elif self.reloads["apache"]:
            self.add_cmd("/etc/init.d/apache2 reload")
            self.reloads["apache"] = False

        t = threading.Thread(
            target=self.send,
            args=[["pcp_runner"], json.dumps(self.requests)]
        )
        t.setDaemon(True)
        t.start()
        return True #self.send(["pcp_runner"], json.dumps(self.requests))

    def print_requests(self):
        for request in self.requests:
            if request["type"] == "cmd":
                print "Run %s" % request["cmd"]
            elif request["type"] == "file":
                print "Write something into " % request["path"]

    def run(self, cmd):
        cmd = [{"type": "cmd", "cmd": cmd}]
        result = self.send(["pcp_runner"], json.dumps(cmd))
        print result
        if len(result) > 0:
            return result[0]

    def add_cmd(self, cmd, user="", stdin="", rm_stdin=False):
        self.requests.append({"type": "cmd", "cmd": cmd, "stdin": stdin, "user": user, "rm_stdin": rm_stdin})

    def add_file(self, path, content, owner=""):
        self.requests.append({"type": "file", "path": path, "content": content, "owner": owner},)

    def restart_apache(self):
        self.restarts["apache"] = True

    def restart_nginx(self):
        self.restarts["nginx"] = True

    def reload_apache(self):
        self.reloads["apache"] = True

    def reload_nginx(self):
        self.reloads["nginx"] = True