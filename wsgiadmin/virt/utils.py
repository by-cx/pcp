import libvirt
from wsgiadmin.virt.models import VirtMachine
import xml.etree.ElementTree as ET


class VirtException(Exception): pass


class VirtMachineConnection(VirtMachine):
    #http://www.ibm.com/developerworks/library/os-python-kvm-scripting1/index.html

    class Meta:
        proxy = True

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
        return conn.lookupByName(self.name)

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

    def dump(self):
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
