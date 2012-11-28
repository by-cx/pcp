import json
import logging
from multiprocessing import Process
from subprocess import Popen, PIPE
import sys
from django.conf import settings


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
            sys.stdout.write("[cmd]: %s\n" % " ".join(["ssh", self.server]+cmd))
            logging.info("[cmd]: %s" % " ".join(["ssh", self.server]+cmd))
            if stdin:
                sys.stdout.write("[stdin]: %s\n" % stdin)
                logging.info("[stdin]: %s" % stdin)
        p = Popen(["ssh", self.server]+cmd, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        stdout, stderr = p.communicate(stdin)
        if not stderr:
            return json.loads(stdout)
        if settings.DEBUG:
            if stdout:
                sys.stdout.write("[stdout]: %s\n" % stdout)
                logging.info("[stdout]: %s" % stdout)
            if stderr:
                sys.stdout.write("[stderr]: %s\n" % stderr)
                logging.info("[stderr]: %s" % stderr)
            sys.stdout.write("---\n")
        raise ScriptException("PCP runner script error: %s" % stderr)

    def commit(self, no_thread=False):
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

        if no_thread:
            self.send(["pcp_runner"], json.dumps(self.requests))
        else:
            p = Process(
                target=self.send,
                args=[["pcp_runner"], json.dumps(self.requests)]
            )
            p.start()
        return True #self.send(["pcp_runner"], json.dumps(self.requests))

    def print_requests(self):
        for request in self.requests:
            if request["type"] == "cmd":
                sys.stdout.write("Run %s\n" % request["cmd"])
            elif request["type"] == "file":
                sys.stdout.write("Write something into \n" % request["path"])

    def run(self, cmd):
        cmd = [{"type": "cmd", "cmd": cmd}]
        result = self.send(["pcp_runner"], json.dumps(cmd))
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