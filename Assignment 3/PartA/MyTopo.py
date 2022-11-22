from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import os


class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    # pylint: disable=arguments-differ
    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()


class NetworkTopo( Topo ):
    "A LinuxRouter connecting three IP subnets"

    # pylint: disable=arguments-differ
    def build( self, **_opts ):

        defaultIP = '192.168.1.1/24'  # IP address for r0-eth1
        router1 = self.addHost( 'r1', cls=LinuxRouter, ip=None, intfName1 = "r1-eth0", intfName2 = "r1-eth1", intfName3 = "r1-eth2" )
        router2 = self.addHost( 'r2', cls=LinuxRouter, ip=None, intfName1 = "r2-eth0", intfName2 = "r2-eth1")
        router3 = self.addHost( 'r3', cls=LinuxRouter, ip=None, intfName1 = "r3-eth0", intfName2 = "r3-eth1" )
        router4 = self.addHost( 'r4', cls=LinuxRouter, ip=None, intfName1 = "r4-eth0", intfName2 = "r4-eth1", intfName3 = "r4-eth2"  )
        

        
        self.addLink(router1, router2, intfName1 = "r1-eth1",intfName2='r2-eth0',
                      params1 = {"ip":"121.0.0.2/16"}, params2={ 'ip' : '121.0.0.1/16' } )
        self.addLink(router2, router4, intfName1="r2-eth1", intfName2='r4-eth0',
                      params1 = {"ip":"123.0.0.1/16"},params2 = {"ip":"123.0.0.2/16"})
        self.addLink(router4, router3, intfName1 = "r4-eth1", intfName2='r3-eth0',
                      params1 = {"ip":"124.0.0.2/16"},params2={ 'ip' : '124.0.0.1/16' } )
        self.addLink(router3, router1, intfName1 = "r3-eth1", intfName2='r1-eth2',
                      params1 = {"ip":"122.0.0.1/16"},params2={ 'ip' : '122.0.0.2/16' } )
        

        h1 = self.addHost( 'h1', ip='120.0.0.1/16', intfName1 = "h1-eth0")
        h2 = self.addHost( 'h2', ip='125.0.0.1/16', intfName1 = "h2-eth0")

        self.addLink(h1, router1, intfName = 'h1-eth0', intfName2='r1-eth0',params1={"ip":"120.0.0.1/16"},
                      params2={ "ip" : "120.0.0.2/16" })
        self.addLink(router4, h2, intfName1 = "r4-eth2", intfName2 = "h2-eth0", 
                      params1 = {"ip":"125.0.0.2/16"}, params2 = {"ip":"125.0.0.1/16"})
        # for h, s in [ (h1, router1), (h2, router3)]:
        #     self.addLink( h, s )


def run():

    topo = NetworkTopo()
    net = Mininet( topo=topo,waitConnected=True)
    info(net["r1"].cmd('ip route add 124.0.0.0/16 via 122.0.0.1 dev r1-eth2'))
    info(net["r1"].cmd('ip route add default via 121.0.0.1 dev r1-eth1'))
    info(net["r2"].cmd('ip route add 120.0.0.0/16 via 121.0.0.2 dev r2-eth0'))
    info(net["r2"].cmd('ip route add 122.0.0.0/16 via 121.0.0.2 dev r2-eth0'))
    info(net["r2"].cmd('ip route add default via 123.0.0.2 dev r2-eth1'))
    info(net["r3"].cmd('ip route add 120.0.0.0/16 via 122.0.0.2 dev r3-eth1'))
    info(net["r3"].cmd('ip route add 121.0.0.0/16 via 122.0.0.2 dev r3-eth1'))
    info(net["r3"].cmd('ip route add default via 124.0.0.2 dev r3-eth0'))
    info(net["r4"].cmd('ip route add 122.0.0.0/16 via 124.0.0.1 dev r4-eth1'))
    info(net["r4"].cmd('ip route add default via 123.0.0.1 dev r4-eth0'))
    info(net["h1"].cmd("ip route add default via 120.0.0.2 dev h1-eth0"))
    info(net["h2"].cmd("ip route add default via 125.0.0.2 dev h2-eth0"))
    net.start()
    info( '*** Routing Table on Router:\n' )
    CLI( net )
    net.stop()


if __name__ == '__main__':
    setLogLevel( 'info' )
    run()


    # r1 ip route add 123.0.0.0/16 via 121.0.0.1 dev r1-eth1
    # r1 ip route add default via 122.0.0.1 dev r1-eth2
    # r2 ip route add 120.0.0.0/16 via 121.0.0.2 dev r2-eth0
    # r2 ip route add 122.0.0.0/16 via 121.0.0.2 dev r2-eth0
    # r2 ip route add default via 123.0.0.2 dev r2-eth1
    # r3 ip route add 120.0.0.0/16 via 122.0.0.2 dev r3-eth1
    # r3 ip route add 121.0.0.0/16 via 122.0.0.2 dev r3-eth1
    # r3 ip route add default via 124.0.0.2 dev r3-eth0
    # r4 ip route add 122.0.0.0/16 via 124.0.0.1 dev r4-eth1
    # r4 ip route add default via 123.0.0.1 dev r4-eth0

