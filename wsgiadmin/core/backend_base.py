import json
import logging
from multiprocessing import Process
from subprocess import Popen, PIPE
import sys
from threading import Thread
import time
from paramiko import SSHClient, AutoAddPolicy
from wsgiadmin.core.exceptions import ScriptException, PCPException
from django.conf import settings
from wsgiadmin.core.models import CommandLog
from django.db import connection
from wsgiadmin.core.tasks import commit_requests


class BaseScript(object):
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
        self.server_object = server
        self.server = server.ssh_cmd.split(" ")

    def commit(self, no_thread=False):
        if self.restarts["nginx"]:
            if self.server_object.os in ("debian6", "debian7", ):
                self.add_cmd("/etc/init.d/nginx restart")
            elif self.server_object.os == "archlinux":
                self.add_cmd("systemctl restart nginx")
            self.reloads["nginx"] = False
            self.restarts["nginx"] = False
        elif self.reloads["nginx"]:
            if self.server_object.os in ("debian6", "debian7", ):
                self.add_cmd("/etc/init.d/nginx reload")
            elif self.server_object.os == "archlinux":
                self.add_cmd("systemctl reload nginx")
            self.reloads["nginx"] = False
        if self.restarts["apache"]:
            if self.server_object.os in ("debian6", "debian7", ):
                self.add_cmd("/etc/init.d/apache2 restart")
            elif self.server_object.os == "archlinux":
                self.add_cmd("systemctl restart apache")
            self.reloads["apache"] = False
            self.restarts["apache"] = False
        elif self.reloads["apache"]:
            if self.server_object.os in ("debian6", "debian7", ):
                self.add_cmd("/etc/init.d/apache2 reload")
            elif self.server_object.os == "archlinux":
                self.add_cmd("systemctl reload apache")
            self.reloads["apache"] = False

    def print_requests(self):
        for request in self.requests:
            if request["type"] == "cmd":
                sys.stdout.write("Run %s\n" % request["cmd"])
            elif request["type"] == "file":
                sys.stdout.write("Write something into \n" % request["path"])

    def run(self, cmd):
        #dummy method, define new one
        pass

    def add_cmd(self, cmd, user="", stdin="", rm_stdin=False):
        self.requests.append({"type": "cmd", "cmd": cmd, "stdin": stdin, "user": user, "rm_stdin": rm_stdin})

    def add_file(self, path, content, owner=""):
        self.requests.append({"type": "file", "path": path, "content": content, "owner": owner}, )

    def restart_apache(self):
        self.restarts["apache"] = True

    def restart_nginx(self):
        self.restarts["nginx"] = True

    def reload_apache(self):
        self.reloads["apache"] = True

    def reload_nginx(self):
        self.reloads["nginx"] = True

    def add_command(self, cmd, stdin=None, rm_stdin=False, user="root"):
        command = CommandLog()
        command.server = self.server_object
        command.command = cmd
        command.execute_user = user
        command.stdin = stdin
        command.rm_stdin = rm_stdin
        command.save()
        return command

    def set_result(self, command, stdout, stderr, status_code):
        command.result_stdout = stdout
        command.result_stderr = stderr
        command.status_code = status_code
        if command.rm_stdin:
            command.stdin = ""
        command.save()


class QueueScript(BaseScript):

    def commit(self, no_thread=False, tasklog=None):
        super(QueueScript, self).commit(no_thread)

        for request in self.requests:
            #{"type": "cmd", "cmd": cmd, "stdin": stdin, "user": user, "rm_stdin": rm_stdin}
            if request["type"] == "cmd":
                args = {
                    "cmd": request.get("cmd"),
                    "stdin": request.get("stdin") if request.get("stdin") else None,
                    "user": request.get("user") if request.get("user") else "root",
                    "rm_stdin": request.get("rm_stdin"),
                }
                self.add_command(**args)
            #{"type": "file", "path": path, "content": content, "owner": owner},
            elif request["type"] == "file":
                args = {
                    "cmd": "tee '%s'" % request.get("path"),
                    "stdin": request.get("content"),
                    "user": "root",
                    "rm_stdin": True,
                }
                self.add_command(**args)
                if request.get("owner"):
                    args = {
                        "cmd": "chown %s:%s '%s'" % (request.get("owner"), request.get("owner"), request.get("path")),
                        "stdin": None,
                        "user": "root",
                        "rm_stdin": False,
                    }
                    self.add_command(**args)

    def run(self, cmd):
        command = self.add_command(cmd)
        cur = connection.cursor()
        counter = 0
        while counter < 100:
            if command.processed:
                return command.result_stdout
            counter += 1
            time.sleep(0.1)
        raise PCPException("Error: waiting for response too long")


class DirectSSHScript(BaseScript):
    def commit(self, no_thread=False, tasklog=None):
        super(DirectSSHScript, self).commit(no_thread)

        if no_thread:
            self.send(["pcp_runner"], json.dumps(self.requests))
        else:
            p = Thread(
                target=self.send,
                args=[["pcp_runner"], json.dumps(self.requests)]
            )
            p.start()
        return True #self.send(["pcp_runner"], json.dumps(self.requests))

    def send(self, cmd, stdin=None):
        if settings.DEBUG:
            sys.stdout.write("[cmd]: %s\n" % " ".join(["ssh"] + self.server + cmd))
            logging.info("[cmd]: %s" % " ".join(["ssh"] + self.server + cmd))
            if stdin:
                sys.stdout.write("[stdin]: %s\n" % stdin)
                logging.info("[stdin]: %s" % stdin)

        p = Popen(["ssh"] + self.server + cmd, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        stdout, stderr = p.communicate(stdin)
        if settings.DEBUG:
            if stdout:
                sys.stdout.write("[stdout]: %s\n" % stdout)
                logging.info("[stdout]: %s" % stdout)
            if stderr:
                sys.stdout.write("[stderr]: %s\n" % stderr)
                logging.info("[stderr]: %s" % stderr)
            sys.stdout.write("---\n")
        if not stderr:
            return json.loads(stdout)
        raise ScriptException("PCP runner script error: %s" % stderr)

    def run(self, cmd):
        cmd = [{"type": "cmd", "cmd": cmd}]
        result = self.send(["pcp_runner"], json.dumps(cmd))
        if len(result) > 0:
            return result[0]


class ParamikoScript(BaseScript):
    """ Backend based on Paramiko """

    def commit(self, no_thread=False, tasklog=None):
        super(ParamikoScript, self).commit(no_thread)
        commit_requests.delay(self.requests, self.server_object, tasklog)

    def run(self, cmd):
        ssh = SSHClient()
        ssh.load_system_host_keys(settings.SSH_HOSTKEYS)
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(self.server_object.domain, username="root", key_filename=settings.SSH_PRIVATEKEY)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        ssh.close()
        return {"stdout": stdout.read(), "stderr": stderr.read()}



Script = ParamikoScript
