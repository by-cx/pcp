import json
from subprocess import Popen, PIPE


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
        self.request = []
        self.log = []
        self.server = server

    def send(self, cmd, stdin=None):
        p = Popen(["ssh", self.server]+cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate(stdin)
        if not stderr:
            return json.loads(stdout)
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