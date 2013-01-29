#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subprocess import Popen, PIPE
import json
import shlex
import sys

def log(msg):
    with open("/var/log/pcp_runner.log", "a") as f:
        f.write("%s\n" % msg)

def run(cmd, stdin=None):
    log("[cmd]: %s" % cmd)
    splited_cmd = shlex.split(str(cmd))
    p = Popen(splited_cmd, stdout=PIPE, stderr=PIPE, stdin=PIPE)
    stdout, stderr = p.communicate(stdin)
    if stdout:
        log("[stdout]: %s" % stdout)
    if stderr:
        log("[stderr]: %s" % stderr)
    ret_code = p.wait()
    log("[ret_code]: %d" % ret_code)
    log("---")
    return ret_code, stdout, stderr


def main():
    requests = json.loads(sys.stdin.read().strip())
    for request in requests:
        log(request)
        if request["type"] == "cmd":
            cmd = request["cmd"]
            if request.get("user"):
                cmd = "su %s -c '%s'" % (request.get("user"), cmd)
                ret_code, stdout, stderr = run(cmd, request.get("stdin") if request.get("stdin") else None)
                request["status"] = "ok"
                request["stdout"] = stdout
                request["stderr"] = stderr
                request["ret_code"] = ret_code
            if request.get("rm_stdin"):
                request["stdin"] = ""
            #if ret_code != 0:
            #    break
        elif request["type"] == "file":
            with open(request["path"], "w") as f:
                f.write(request["content"])
                request["status"] = "ok"
            if request.get("owner"):
                run("chown %s %s" % (request.get("owner"), request.get("path")))
        else:
            request["status"] = "unknown type"
    sys.stdout.write(json.dumps(requests))


if __name__ == "__main__":
    try:
        main()
    except OSError as e:
        print "OSError (%s)" % e