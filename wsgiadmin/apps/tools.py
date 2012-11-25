import json
from subprocess import Popen, PIPE
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
        self.log = []
        self.server = server

    def send(self, cmd, stdin=None):
        if settings.DEBUG:
            print "[cmd]: %s" % " ".join(["ssh", self.server]+cmd)
            if stdin:
                print "[stdin]: %s" % stdin
        p = Popen(["ssh", self.server]+cmd, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        stdout, stderr = p.communicate(stdin)
        if not stderr:
            return json.loads(stdout)
        if settings.DEBUG:
            if stdout:
                print "[stdout]: %s" % stdout
            if stderr:
                print "[stderr]: %s" % stderr
            print "---"
        raise ScriptException("PCP runner script error: %s" % stderr)

    def commit(self):
        return self.send(["pcp_runner"], json.dumps(self.requests))

    def print_requests(self, server):
        for request in self.requests:
            if request["type"] == "cmd":
                print "Run %s" % request["cmd"]
            elif request["type"] == "file":
                print "Write something into " % request["path"]

    def run(self, cmd):
        cmd = [{"type": "cmd", "cmd": cmd}]
        result = self.send(["pcp_runner"], json.dumps(cmd))
        if len(result) > 0:
            return result[0]

    def add_cmd(self, cmd, user="", stdin=""):
        self.requests.append({"type": "cmd", "cmd": cmd, "stdin": stdin, "user": user})

    def add_file(self, path, content, owner=""):
        self.requests.append({"type": "file", "path": path, "content": content, "owner": owner},)