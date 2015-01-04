UDP Tunnel Proxy Server
=======================

## Prerequisite ## 
UDP proxy server requires python-pytun module to be installed on the
hosts

On Ubuntu 14.04 execute following 

	sudo apt-get upgrade
	sudo apt-get install python-pip
	sudo apt-get install python-dev
	sudo pip install python-pytun

## Description ## 

The UDP proxy Server provides a simple method to form a 
mesh between set of hosts using UDP tunnels and tun device. 
The UDP tunnel Proxy server consists of two files 

### 1. udpProxyServer.py ###

This is the main daemon. Download udpProxyServer.py file to 
all the hosts that should be meshed. The udpProxyServer.py
listens for data sent locally on the tunnel device and forwards 
it to remote server on UDP socket. Similarly it listens for 
packets received from remote host and forwards it to tunnel 
device. 

A point-to-point UDP tunnel is created for each remote peer

The proxy server binds to two ports 

	(a) control port: 
	The UDP proxy server listens for control messages on 
	this port. It allows dynamically peering to other hosts. 
	One can add or delete tunnels to hosts without shutting down 
	the proxy server

	(b) data port: 
	The data traffic from remote host is sent/received on data port. 


#### Example: ####
sudo python udpProxyServer.py [-dp \<dataPort\>] [-cp \<controlPort\>] &

#### Default: ####
Server uses following ports 

	data port: 5000
	control port: 5001 

### 2. udpProxyServerControl.py ###

This file provides control interface to the proxy server. 
User can download udpProxyServerControl.py on any one of the host or 
some other host that is be used for managing the mesh between the hosts. 

The UDP proxy server control allows user to add new tunnels 
to new host. User can also delete a tunnel to a host. 
Thus it provides capability to dynamically add or remove host 
from the mesh 

The udpProxyServer daemon expects following control message for adding 
or deleting a tunnel

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

### Example: ###

udpProxyServerControl.py 172.100.1.1 -o add -n udp0 -t 10.0.0.1 -r 172.100.1.2 -p 5001

Example Mesh between three hosts 

minion-1: 172.100.1.1   
minion-2: 172.100.1.2
minion-3: 172.100.2.3

#### [1]: Launch UDP Proxy Server Daemon on each host ####

sudo python udpProxyServer.py -dp 5000 -cp 5001 &

The daemon is now waiting for commands to add point-to-point 
tunnels to other hosts. The control messages are expected on udp port 5001 
while data packets are expected on port 5000. 

You can change the port numbers by changing the above cmdline params 

#### [2]: Create tunnel interfaces to each host peering with other hosts ####

###### Host 1: ######
Tunnel to Host 2:
udpProxyServerControl.py -s 172.100.1.1 -o add -n udp2 -t 10.0.1.1 -r 172.100.1.2 -p 5001

Tunnel to Host 3:
udpProxyServerControl.py -s 172.100.1.1 -o add -n udp3 -t 10.0.3.1 -r 172.100.1.2 -p 5001

###### Host 2: ######
Tunnel to Host 1:
udpProxyServerControl.py -s 172.100.1.2 -o add -n udp1 -t 10.0.1.2 -r 172.100.1.1 -p 5001

Tunnel to Host 3:
udpProxyServerControl.py -s 172.100.1.2 -o add -n udp3 -t 10.0.2.2 -r 172.100.1.3 -p 5001

###### Host 3: ######
Tunnel to Host 1:
udpProxyServerControl.py -s 172.100.1.3 -o add -n udp1 -t 10.0.3.2 -r 172.100.1.1 -p 5001

Tunnel to Host 2:
udpProxyServerControl.py -s 172.100.1.3 -o add -n udp3 -t 10.0.2.3 -r 172.100.1.2 -p 5001


Adding routes via tunnel interface

Host-1:
sudo route add -net 192.168.2.0 netmask 255.255.255.0 dev udp2
sudo route add -net 192.168.3.0 netmask 255.255.255.0 dev udp3

Host-2:
sudo route add -net 192.168.1.0 netmask 255.255.255.0 dev udp1
sudo route add -net 192.168.3.0 netmask 255.255.255.0 dev udp3

Host-3:
sudo route add -net 192.168.1.0 netmask 255.255.255.0 dev udp1
sudo route add -net 192.168.2.0 netmask 255.255.255.0 dev udp2




