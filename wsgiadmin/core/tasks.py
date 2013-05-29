from celery import task
from django.conf import settings
from paramiko import SSHClient, AutoAddPolicy


@task()
def commit_requests(requests, server, task_log=None):
    logger = commit_requests.get_logger()

    ssh = SSHClient()
    ssh.load_system_host_keys(settings.SSH_HOSTKEYS)
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    ssh.connect(server.domain, username="root", key_filename=settings.SSH_PRIVATEKEY)
    error = False
    msg = ""
    try:
        for req in requests:
            if req.get("type") == "cmd":
                req_user = req.get("user")
                if req_user == "root":
                    req_cmd = req.get("cmd")
                else:
                    req_cmd = "su %s -c '%s'" % (req_user, req.get("cmd"))
                req_stdin = req.get("stdin")
                logger.info("CMD: %s" % req_cmd)
                stdin, stdout, stderr = ssh.exec_command(req_cmd)
                if req_stdin:
                    stdin.write(req_stdin)
                    stdin.flush()
                stdin.channel.shutdown(1)
            elif req.get("type") == "file":
                req_path = req.get("path")
                req_cmd = "tee '%s'" % req_path
                req_stdin = req.get("stdin")
                req_owner = req.get("owner")
                logger.info("CMD: %s" % req_cmd)
                stdin, stdout, stderr = ssh.exec_command(req_cmd)
                if req_stdin:
                    stdin.write(req_stdin)
                    stdin.flush()
                stdin.channel.shutdown(1)
                if req_owner:
                    ssh.exec_command("chown %s:%s '%s'" % (req_owner, req_owner, req_path))
            if stdout.channel.recv_exit_status() != 0:
                error = True
    finally:
        ssh.close()

    if task_log:
        task_log.complete = True
        task_log.error = error
        task_log.backend_msg = msg
        task_log.save()

    return not error


"""
from paramiko import SSHClient, AutoAddPolicy
ssh = SSHClient()
ssh.set_missing_host_key_policy(AutoAddPolicy())
ssh.connect("localhost", username="root")
stdin, stdout, stderr = ssh.exec_command("tee /tmp/test.tee")
stdin.write("abcd")
stdin.flush()
stdin.channel.shutdown(1)
stdout.read()
stdin, stdout, stderr = ssh.exec_command("tee /tmp/test.tee")
stdin.write("efgh")
stdin.flush()
stdin.channel.shutdown(1)
stdout.read()
"""