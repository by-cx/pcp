from wsgiadmin.core.backend_base import Script
from wsgiadmin.virt.models import VirtMachine
from wsgiadmin.virt.utils import VirtMachineConnection


class VirtMachineBackend(VirtMachine):

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(VirtMachineBackend, self).__init__(*args, **kwargs)
        self.connection = VirtMachineConnection.objects.get(id=self.id)
        self.script = Script(self.core_server)

    def gen_token_config(self, exclude=None):
        content = []
        for server in VirtMachineConnection.objects.filter(server=self.server):
            if exclude and server.id != exclude.id:
                content.append(("%s: 127.0.0.1:%d" % (server.token, server.vnc_port)))
        return content

    def install(self):
        self.gen_token_config()
        self.script.add_cmd("supervisorctl restart websockify")

    def uninstall(self):
        self.gen_token_config(self.id)
        self.script.add_cmd("supervisorctl restart websockify")