import logging, urllib, json
from django.conf import settings

info = logging.info

class RawRequest(object):
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
