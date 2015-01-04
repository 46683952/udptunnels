#! /usr/bin/env python

#                                                                         
# udpProxyServer.py 
#  
# Decription: A simple Proxy Server tunneling over UDP with tun device 
#
# Copyright (C) 2015  Sameer Merchant <smerchan@yahoo.com>
#                                                                         
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the 
# Free Software Foundation; either version 2, or (at your option) any  
# later version.                                                      
#                                                                      
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of         
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU 
# General Public License for more details.                         
#
import sys
import socket
import select
import errno
import pytun
import argparse 
import json

class UDPServer(object):

   def __init__(self, dport, cport):

      self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      self.sock.bind(('0.0.0.0', dport))
      self.dport = dport

      self.control = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      self.control.bind(('0.0.0.0', cport))
      self.cport = cport

      print "Listening for control event on UDP Port %d, data on port %d" % (
            cport, dport)

      self.tunnels = {}
      self.remoteServer = {}

      self.to_tun = {}
      self.to_sock = {}
   
      self.rlist = [ self.sock, self.control ]  
      self.wlist = [ ]
      self.xlist = [ ]

   def addTunnel(self, t):

       localAddr =  t.get('tunnelIP', None)
       tunnelname = t.get('name', None)
       netmask = t.get('netmask', None)
       remoteServerIP = t.get('remoteServer', None)
       mtu = t.get('mtu', 1500)

       if ((localAddr is None) or 
           (tunnelname is None) or 
           (netmask is None) or 
           (remoteServerIP is None)): 
          print "Invalid param addr:%s, name:%s, mask:%s remoteServer:%s" % (
                 localAddr, tunnelname, netmask, remoteServerIP)
          return 

       print "Adding tunnel %s" % str(t)
 
       tun = pytun.TunTapDevice(name=tunnelname)
       tun.addr = localAddr
       tun.netmask = netmask
       tun.mtu = mtu
       tun.up()
 
       self.tunnels[remoteServerIP] = tun
       self.remoteServer[tun.name] = remoteServerIP
       self.rlist.append(tun)

   def getTunnel(self, remoteServerIP):
       return self.tunnels.get(remoteServerIP, None)
      
   def getRemoteServer(self, tunnelName):
       return self.remoteServer.get(tunnelName, None)

   def delTun(self, t):
       name = t.get('name', None)
       remoteServerIP = self.getRemoteServer(name)
       tunnel = self.getTunnel(remoteServerIP)
   
       if remoteServerIP == None: 
          #print "Remote server Not Found for tunnel %s" % name
          return 

       if tunnel == None: 
          #print "Tunnel %s not found" % name
          return 

       print "deleting tunnel %s" % str(t)
       del self.tunnels[remoteServerIP]
       del self.remoteServerIP[name]

       self.rlist.remove(tunnel)
       tunnel.close()

   def updateServer(self, msg):
       m = json.loads(msg)
       op = m.get('op', None)

       tunnels = m.get('tunnel', [])

       for tunnel in tunnels: 
           if op == 'add': 
              self.addTunnel(tunnel)
           elif op == 'del': 
              self.delTunnel(tunnel)
           else: 
              print "Invalid operation: %s" % op
       
   def run(self):

       self.to_sock = {}
       self.to_tun = {} 

       while True: 
          try: 
             r, w, z = select.select(self.rlist, self.wlist, self.xlist)

             #print "Received an event: \n" 
             #print r

             #
             # Check if any data was received from any Tunnel interface 
             #
             for rs, tun in self.tunnels.iteritems():
                 if tun in r:
                    # 
                    # Add the packet to be sent to remote server 
                    # as a tuple 
                    #  (remoteServerAddr, data) 
                    #
                    self.to_sock[rs] = tun.read(tun.mtu)
                    #pkt = ' 0x'.join(hex(ord(x))[2:] for x in to_sock)
                    #print pkt 
 
             #
             # Check if data was received from socket interface 
             #
             if self.sock in r:
                 to_tun, addr = self.sock.recvfrom(65535)
                 #
                 # Lookup tunnel interface based on 
                 # sender IP address 
                 #
                 tun = self.getTunnel(addr[0])

                 if tun:
                    #
                    # Add packets to be sent to the Tunnel
                    # Cache it as a tuple
                    #   (tunnel, data) 
                    #
                    self.to_tun[tun.name] = (tun, to_tun)
                 ''' 
                 else: 
                    print "No tunnel found for server IP %s" % str(addr[0])
                 '''

             if self.control in r: 
                controlMessage, caddr = self.control.recvfrom(65535)
                #print "Received Control Message %s" % str(controlMessage)
                self.updateServer(controlMessage)
                  
             #
             # Write data to tunnel
             #
             for name, (tun, data) in self.to_tun.iteritems():
                  tun.write(data)

             self.to_tun = {}

             #
             # Write data to socket 
             #
             for (raddr, to_sock) in self.to_sock.iteritems():
                 self.sock.sendto(to_sock, (raddr, self.dport))

             self.to_sock = {}

          except (select.error, socket.error, pytun.Error), e:
                if e[0] == errno.EINTR:
                    continue
                print >> sys.stderr, str(e)
                break

def getOptions():
    tunnelIP = ''
    remoteServerIP = ''
    dp = None
    cp = None
    mtu = None
    name = None

    parser = argparse.ArgumentParser(description='UDP proxy Server ')
    parser.add_argument('-dp','--dataPort', 
                        help='UDP Proxy Server data port', 
                        type=int, default=5000)
    parser.add_argument('-cp','--controlPort', 
                        help='UDP Proxy Server control port', 
                        type=int, default=5001)
    args = vars(parser.parse_args())
 
    dp = args.get('dataPort', None)
    cp = args.get('controlPort', None)

    return (dp, cp)

def main():
   (dp, cp) = getOptions()
   if (dp is None) or (cp is None): 
       print "Invalid Ports - data port: %d, control port %d" % (dp, cp)

   server = UDPServer(dp, cp)
   server.run()
    
if __name__ == '__main__':
   main()
