import os
from contextlib import contextmanager

from mininet.cli import CLI
from mininet.log import info, setLogLevel
from mininet.net import Mininet
from mininet.node import Node
from mininet.topo import Topo


class Router(Node):
    @contextmanager
    def in_router_dir(self):
        working_dir = os.getcwd()
        self.cmd('cd %s' % self.name)
        self.cmd('mkdir test')
        yield
        self.cmd('cd %s' % working_dir)

    def config(self, **params):
        super(Router, self).config(**params)


        self.cmd('sysctl net.ipv4.ip_forward=1')


        with self.in_router_dir():
            self.cmd('bird -l')


    def terminate(self):

        self.cmd('sysctl net.ipv4.ip_forward=0')


        with self.in_router_dir():
            self.cmd('birdc -l down')

        super(Router, self).terminate()


class DisabledRouter(Node):


    @contextmanager
    def in_router_dir(self):
        working_dir = os.getcwd()
        self.cmd('cd %s' % self.name)

        yield
        self.cmd('cd %s' % working_dir)

    def config(self, **params):
        super(DisabledRouter, self).config(**params)

        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')

        super(DisabledRouter, self).terminate()


def prefix(address, length):
    return "%s/%s" % (address, str(length))


class Topology(Topo):
    def build(self, *args, **params):

        router1 = self.addHost( 'r1', cls=Router, ip=None, intfName1 = "r1-eth0", intfName2 = "r1-eth1", intfName3 = "r1-eth2" )
        router2 = self.addHost( 'r2', cls=Router, ip=None, intfName1 = "r2-eth0", intfName2 = "r2-eth1")
        router3 = self.addHost( 'r3', cls=Router, ip=None, intfName1 = "r3-eth0", intfName2 = "r3-eth1" )
        router4 = self.addHost( 'r4', cls=Router, ip=None, intfName1 = "r4-eth0", intfName2 = "r4-eth1", intfName3 = "r4-eth2"  )
        h1 = self.addHost( 'h1', ip='120.0.0.1/16',cls=Router, intfName1 = "h1-eth0")
        h2 = self.addHost( 'h2', ip='125.0.0.1/16',cls=Router, intfName1 = "h2-eth0")

        self.addLink(h1, router1, intfName = 'h1-eth0', intfName2='r1-eth0',params1={"ip":"120.0.0.1/16"},
                      params2={ "ip" : "120.0.0.2/16" })
        self.addLink(router4, h2, intfName1 = "r4-eth2", intfName2 = "h2-eth0", 
                      params1 = {"ip":"125.0.0.2/16"}, params2 = {"ip":"125.0.0.1/16"})
        self.addLink(router1, router2, intfName1 = "r1-eth1",intfName2='r2-eth0',
                      params1 = {"ip":"121.0.0.2/16"}, params2={ 'ip' : '121.0.0.1/16' })
        self.addLink(router2, router4, intfName1="r2-eth1", intfName2='r4-eth0',
                      params1 = {"ip":"123.0.0.1/16"},params2 = {"ip":"123.0.0.2/16"})
        self.addLink(router4, router3, intfName1 = "r4-eth1", intfName2='r3-eth0',
                      params1 = {"ip":"124.0.0.2/16"},params2={ 'ip' : '124.0.0.1/16' })
        self.addLink(router3, router1, intfName1 = "r3-eth1", intfName2='r1-eth2',
                      params1 = {"ip":"122.0.0.1/16"},params2={ 'ip' : '122.0.0.2/16' })
        

def run():

    topology = Topology()
    net = Mininet(topo=topology)

    # Setting the parameters as instructed

    info(net["r1"].cmd("tc qdisc add dev r1-eth0 root handle 1: tbf rate 100mbit buffer 26214400  limit 26214400 "))
    info(net["r1"].cmd("tc qdisc add dev r1-eth1 root handle 1: tbf rate 100mbit buffer 26214400  limit 26214400 "))
    info(net["r1"].cmd("tc qdisc add dev r1-eth2 root handle 1: tbf rate 100mbit buffer 26214400  limit 26214400 "))
    info(net["r2"].cmd("tc qdisc add dev r2-eth0 root handle 1: tbf rate 100mbit buffer 26214400  limit 26214400 "))
    info(net["r2"].cmd("tc qdisc add dev r2-eth1 root handle 1: tbf rate 100mbit buffer 26214400  limit 26214400 "))
    info(net["r3"].cmd("tc qdisc add dev r3-eth0 root handle 1: tbf rate 100mbit buffer 26214400  limit 26214400 "))
    info(net["r3"].cmd("tc qdisc add dev r3-eth1 root handle 1: tbf rate 100mbit buffer 26214400  limit 26214400 "))
    info(net["r4"].cmd("tc qdisc add dev r4-eth0 root handle 1: tbf rate 100mbit buffer 26214400  limit 26214400 "))
    info(net["r4"].cmd("tc qdisc add dev r4-eth1 root handle 1: tbf rate 100mbit buffer 26214400  limit 26214400 "))
    info(net["r4"].cmd("tc qdisc add dev r4-eth2 root handle 1: tbf rate 100mbit buffer 26214400  limit 26214400 "))
    
    info(net["r1"].cmd("tc qdisc add dev r1-eth0 parent 1:1 handle 10: netem dealy 30ms"))
    info(net["r1"].cmd("tc qdisc add dev r1-eth1 parent 1:1 handle 10: netem dealy 30ms"))
    info(net["r1"].cmd("tc qdisc add dev r1-eth2 parent 1:1 handle 10: netem dealy 30ms"))
    info(net["r2"].cmd("tc qdisc add dev r2-eth0 parent 1:1 handle 10: netem dealy 30ms"))
    info(net["r2"].cmd("tc qdisc add dev r2-eth1 parent 1:1 handle 10: netem dealy 30ms"))
    info(net["r3"].cmd("tc qdisc add dev r3-eth0 parent 1:1 handle 10: netem dealy 30ms"))
    info(net["r3"].cmd("tc qdisc add dev r3-eth1 parent 1:1 handle 10: netem dealy 30ms"))
    info(net["r4"].cmd("tc qdisc add dev r4-eth0 parent 1:1 handle 10: netem dealy 30ms"))
    info(net["r4"].cmd("tc qdisc add dev r4-eth1 parent 1:1 handle 10: netem dealy 30ms"))
    info(net["r4"].cmd("tc qdisc add dev r4-eth2 parent 1:1 handle 10: netem dealy 30ms"))

    net.start()

    CLI(net)

    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()