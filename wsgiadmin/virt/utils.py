import uuid
from constance import config
from django.template.loader import render_to_string
import libvirt
import random
from wsgiadmin.virt.models import VirtMachine
import xml.etree.ElementTree as ET


class VirtException(Exception): pass


class VirtMachineConnection(VirtMachine):
    #http://www.ibm.com/developerworks/library/os-python-kvm-scripting1/index.html

    class Meta:
        proxy = True

    def create_domain(self, memory, cpus, size):
        """
            memory - memory in MiB
            cpus - number of CPUs
            size - size of disk in GB
        """

        domain_xml = render_to_string("virt/domain.xml", {
            "name": self.ident,
            "memory": memory,
            "cpus": cpus,
            "uuid": uuid.uuid4(),
            "disk_file": config.virt_disk_pathfile % self.ident,
            "mac": mac_generator(),
        })
        self.create_storage(size)
        conn = libvirt.open(self.server.libvirt_url)
        conn.virDomainDefineXML(domain_xml)

    def create_storage(self, size):
        """
            size - size in GB
        """
        storage_xml = render_to_string("virt/storage-vol.xml", {
            "name": self.ident,
            "disk_file": config.virt_disk_pathfile % self.ident,
            "size": size,
        })
        conn = libvirt.open(self.server.libvirt_url)
        pool = conn.virStoragePoolLookupByName(config.virt_pool)
        pool.virStorageVolCreateXMLFrom(storage_xml)

    def _get_libvirt_connection(self):
        conn = libvirt.open(self.server.libvirt_url)
        if conn == None:
            raise VirtException("Can't connect to server")
        return conn

    def domain(self):
        conn = self._get_libvirt_connection()
        #print "Conn"
        #print conn.domainXMLToNative("hypervisor", "messenger", 0)
        #for parm in dir(conn):
        #    print parm
        return conn.lookupByName(self.ident)

    def memory(self):
        domain = self.domain()
        info = domain.info()
        return info[1] / float(1024)

    def cpus(self):
        domain = self.domain()
        #print "Domain"
        #for parm in dir(domain):
        #    print parm
        info = domain.info()
        return info[3]

    def state(self):
        domain = self.domain()
        info = domain.info()
        return info[0]

    def start(self):
        "Resume stopped VM"
        domain = self.domain()
        domain.create()

    def reset(self):
        "Force reset VM"
        domain = self.domain()
        domain.reset(0)

    def reboot(self):
        "Kindly reboot VM"
        domain = self.domain()
        domain.reboot(1)

    def shutdown(self):
        "Kindly shutdown VM"
        domain = self.domain()
        domain.shutdown(1)

    def force_shutdown(self):
        "Brutaly shutdown VM"
        domain = self.domain()
        domain.destroy(0)

    def dump(self):
        "Returns XML of domain"
        domain = self.domain()
        return ET.fromstring(domain.XMLDesc(0))

    def storage_list(self):
        dump = self.dump()
        conn = self._get_libvirt_connection()
        disks = []
        for subtree in dump.findall("./devices/disk"):
            if subtree.attrib["device"] == "disk":
                disk = {"name": "", "size": {"capacity": 0, "alloc": 0}, "source": ""}
                for parm in subtree:
                    if parm.tag == "source":
                        disk["source"] = parm.attrib["dev"] if "dev" in parm.attrib else parm.attrib["file"]
                    if parm.tag == "target":
                        disk["name"] = parm.attrib["dev"]
                disks.append(disk)
        for disk in disks:
            vol = conn.storageVolLookupByPath(disk["source"])
            if vol:
                info = vol.info()
                print info
                disk["size"] = {"capacity": info[1] / float(1024**3), "alloc": info[2] / float(1024**3)}
            else:
                disk["size"] = {"capacity": -1, "alloc": -1}
        return disks

    def vnc_port(self):
        dump = self.dump()
        for subtree in dump.findall("./devices/graphics"):
            return subtree.attrib.get("port", 0)


def mac_generator():
    return ':'.join(map(lambda x: "%02x" % x, [ 0x52, 0x54, 0x00, random.randint(0x00, 0x7F), random.randint(0x00, 0xFF), random.randint(0x00, 0xFF) ]))