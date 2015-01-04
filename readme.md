The UDP proxy Server provides a simple mesh between set of hosts 
using UDP tunnels and tun device. The UDP tunnel Proxy solution 
consists of two files 

1. udpProxyServer.py 

Copy this file to all the hosts you wish to mesh. This is the proxy daemon 
that copies packets to/from tun device to udp socket and vice versa. 

The proxy server binds to two ports 

(a) control port: 
The UDP proxy server listens for control messages on this port. It allows dynamically peering to other hosts. One can add or delete tunnels to hosts without shutting down the proxy server

(b) data port: 
The data traffic from remote host is sent/received on data port. 


Example:
sudo python udpProxyServer.py [-dp \<dataPort\>] [-cp \<controlPort\>] &

Default: 

data port: 5000
control port: 5001 

2. udpProxyServerControl.py 

This file provides control interface to the proxy server. You can install this on any one host or some remote server that will be used for controlling the mesh between the hosts. 

The UDP proxy server control allows you to add new tunnels to newly added host. You can also delete a tunnel to a host. Thus dynamically addint/deleting host to/from mesh 

The udpProxyServer expects control message in following format: 

{ 
  'op': 'add',
  'tunnel' : [
      {
        'name' : 'TunnelName',
        'tunnelIP': 'TunnelLocalIP',
        'netmask': 'TunnelNetMask',
        'mtu': 'TunnelMTU',
        'remoteServer': 'Remte Server IP for this tunnel'
      }
   ]
}

Example: 

udpProxyServerControl.py 172.100.1.1 -o add -n udp0 -t 10.0.0.1 -r 172.100.1.2 -p 5001

Example Mesh between three hosts 

minion-1: 172.100.1.1   
minion-2: 172.100.1.2
minion-3: 172.100.2.3

[1]: Launch UDP Proxy Server Daemon on each host

sudo python udpProxyServer.py -dp 5000 -cp 5001 &

The daemon is now waiting for commands to add point-to-point 
tunnels to other hosts. The control messages are expected on udp port 5001 
while data packets are expected on port 5000. 

You can change the port numbers by changing the above cmdline params 

[2]: Create tunnel interfaces to each host peering with other hosts

Host 1: 
  Tunnel to Host 2:
      udpProxyServerControl.py -s 172.100.1.1 -o add -n udp2 -t 10.0.0.2 -r 172.100.1.2 -p 5001

  Tunnel to Host 3:
      udpProxyServerControl.py -s 172.100.1.1 -o add -n udp3 -t 10.0.0.2 -r 172.100.1.2 -p 5001

Host 2: 
  Tunnel to Host 1:
      udpProxyServerControl.py -s 172.100.1.2 -o add -n udp1 -t 10.0.1.1 -r 172.100.1.1 -p 5001

  Tunnel to Host 3:
      udpProxyServerControl.py -s 172.100.1.2 -o add -n udp3 -t 10.0.1.3 -r 172.100.1.3 -p 5001

Host 3: 
  Tunnel to Host 1:
      udpProxyServerControl.py -s 172.100.1.3 -o add -n udp1 -t 10.0.2.1 -r 172.100.1.1 -p 5001

  Tunnel to Host 2:
      udpProxyServerControl.py -s 172.100.1.3 -o add -n udp3 -t 10.0.2.2 -r 172.100.1.2 -p 5001


Example of adding routes via tunnel 

Host-1:
sudo route add -net 192.168.2.0 netmask 255.255.255.0 dev udp2
sudo route add -net 192.168.3.0 netmask 255.255.255.0 dev udp3

Host-2:
sudo route add -net 192.168.1.0 netmask 255.255.255.0 dev udp1
sudo route add -net 192.168.3.0 netmask 255.255.255.0 dev udp3

Host-3:
sudo route add -net 192.168.1.0 netmask 255.255.255.0 dev udp1
sudo route add -net 192.168.2.0 netmask 255.255.255.0 dev udp2


With above example host can route 192.168.x.y network via udp tunnel 


