#! /usr/bin/env python

#                                                                         
# udpProxyServerControl.py 
#  
# Decription: Util to control simple Proxy Server 
#             tunneling over UDP with tun device 
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

import argparse
import socket
import json 


def getParams():
    parser = argparse.ArgumentParser(
                        description='UDP proxy Server control util')
    parser.add_argument('-s','--server',
                        help='UDP proxy Server Name',
                        type=str, required=True)
    parser.add_argument('-p','--port',
                        help='UDP proxy Server control port',
                        type=int, default=5001)
    parser.add_argument('-o','--operation',
                        help='operation: add or del',
                        type=str, default="add")
    parser.add_argument('-n','--name',
                        help='tunnel name',
                        type=str, required=True)
    parser.add_argument('-t','--tunnel',
                        help='tunnel interface IP address',
                        type=str, required=True)
    parser.add_argument('-tm','--mask',
                        help='tunnel interface Netmask',
                        type=str, default="255.255.255.252")
    parser.add_argument('-m','--mtu',
                        help='tunnel interface mtu',
                        type=int, default=1500)
    parser.add_argument('-r','--remote',
                        help='remote server IP',
                        type=str, required=True)
    args = vars(parser.parse_args())


    s = args.get('server', None)
    p = args.get('port', None)
    o = args.get('operation', None)
    
    if (o != "add") and (o != "del"):
       print "Valid operations: 'add' or 'del'"
       return None

    n = args.get('name', None)
    t = args.get('tunnel', None)
    tm = args.get('mask', None)
    m = args.get('mtu', None)
    r = args.get('remote', None)
    
    return (s, p,  o, n, t, tm, m, r)

def test(data): 
    m = json.loads(data)
    print "Json Message: \n" 
    print m

def main():
    arg = getParams()
    if arg is None:
       return

    (s, p, o, n, t, tm, m, r) = arg

    msg = { 
       'op': o,
       'tunnel' : [ 
           { 
              'name' : n,
              'tunnelIP': t,
              'netmask': tm,
              'mtu': m,
              'remoteServer': r
           }
        ]
    }

    data = json.dumps(msg) 

    print "sending data %s to server: %s, port: %s" % (data, s, p)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sent = sock.sendto(data, (s, p))
    print sent 
    test(data)

if __name__ == '__main__':
   main()
