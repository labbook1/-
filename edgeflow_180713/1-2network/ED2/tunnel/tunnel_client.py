#!/usr/bin/env python
## need update
import os, sys
import hashlib
import getopt
import fcntl
import icmp
import time
import struct
import socket, select
import random
import time

import ofdm.TDMATunnel

SHARED_PASSWORD = hashlib.md5("xiaoxia").digest()
TUNSETIFF = 0x400454ca
IFF_TUN   = 0x0001

MODE = 0
DEBUG = 0
PORT = 0
IP="192.168.10.4"
IFACE_IP = "10.0.0.1"
MTU = 1500
CODE = 86
TIMEOUT = 60*10 # seconds

class Tunnel():
    def create(self):
        self.tfd = os.open("/dev/net/tun", os.O_RDWR)
        ifs = fcntl.ioctl(self.tfd, TUNSETIFF, struct.pack("16sH", "t%d", IFF_TUN))
        self.tname = ifs[:16].strip("\x00")
        self.clients = []
        self.usrpFlag = True
        self.percentage = 0.5
        self.time1 = 0
        self.flag = 1
        self.TrueFlag = 1
        self.mac = 0
        self.packet = 0
        print(self.clients)

    def close(self):
        os.close(self.tfd)

    def config(self, ip):
        os.system("ip link set %s up" % (self.tname))
        os.system("ip link set %s mtu 1400" % (self.tname))
        os.system("ip addr add %s dev %s" % (ip, self.tname))


    def run(self):

        self.icmpfd = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
        self.packet = icmp.ICMPPacket()
        self.client_seqno = 1

        dataFlag = False
        datatemp = 0
        buf = 0
        time2 = time.time()
        while True:
            rset = select.select([self.icmpfd, self.tfd], [], [])[0]
            for r in rset:
                if r == self.tfd:
                    #print("tun")
                    if DEBUG: o.write(1, ">")
                    if self.usrpFlag == True:
                        datatemp = os.read(self.tfd, MTU)
                        buf = self.packet.create(8, 86, 8000, 1, datatemp)
                        dataFlag = True
                        if len(datatemp) > 500:
                            time.sleep(0.002)
                            self.icmpfd.sendto(buf, (IP, 22))
                        else:
                            self.icmpfd.sendto(buf, (IP, 22))
                        dataFlag = False
                elif r == self.icmpfd:
                    if DEBUG: os.write(1, "<")
                    buf = self.icmpfd.recv(icmp.BUFFER_SIZE)
                    data = self.packet.parse(buf, DEBUG)
                    ip = socket.inet_ntoa(self.packet.src)
                    #print("WWWWWWWWWWWWWWWWWWWW")
                    if self.packet.code in (CODE, CODE+1):
                         # Simply write the packet to local or forward them to other clients ???
                         os.write(self.tfd, data)
                    if self.packet.code in (90,91):
                          print("AAAA"+str(self.packet.code))
                          print(time.time() - time2)
                          time2 = time.time()
                          if self.packet.code == 90:
                              self.usrpFlag = True
                          else:
                              self.usrpFlag = False
                         #self.clients[key]["aliveTime"] = time.time()

def usage(status = 0):
    print "Usage: icmptun [-s code|-c serverip,code,id] [-hd] [-l localip]"
    sys.exit(status)

if __name__=="__main__":
    MODE=2
    CODE=87
    IP="192.168.5.9"
    PORT=22
    IFACE_IP = "192.168.2.2/24"

    tun = Tunnel()
    tun.create()
    print "Allocated interface %s" % (tun.tname)
    tun.config(IFACE_IP)
    try:
        tun.run()
    except KeyboardInterrupt:
        tun.close()
        sys.exit(0)

