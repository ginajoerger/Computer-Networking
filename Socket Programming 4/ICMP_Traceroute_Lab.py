#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 17:26:15 2019

@author: ginajoerger
"""
from socket import *
import socket
import os
import sys
import struct
import time
import select
import binascii

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 2

def checksum(str):
    csum = 0
    countTo = (len(str) // 2) * 2
    count = 0
    
    while count < countTo:
        thisVal = str[count + 1] * 256 + str[count]
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2
        
    if countTo < len(str):
        csum = csum + str[len(str) - 1].decode()
        csum = csum & 0xffffffff
        
    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def build_packet():
    myChecksum = 0
    ID = os.getpid() & 0xFFFF
    
    header = struct.pack("!bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("!d", time.time())
    
    myChecksum = checksum(header + data)
    
    header = struct.pack("!bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data
    
    return packet
    
def get_route(hostname):
    timeLeft = TIMEOUT
    for ttl in range(1, MAX_HOPS):
        for tries in range(TRIES):
            destAddr = socket.gethostbyname(hostname)

            icmp = socket.getprotobyname("icmp")
            mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
            
            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
            mySocket.settimeout(TIMEOUT)
            try:
                d = build_packet()
                mySocket.sendto(d, (hostname, 0))
                t = time.time()
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], timeLeft)
                howLongInSelect = (time.time() - startedSelect)
                if whatReady[0] == []: # Timeout
                    print(" * * * Request timed out.")
                recvPacket, addr = mySocket.recvfrom(1024)
                timeReceived = time.time()
                timeLeft = timeLeft - howLongInSelect
                if timeLeft <= 0:
                    print(" * * * Request timed out.")
            except socket.timeout:
                continue
            else:
                hr = recvPacket[20:28]
                types, code, checksum, packetID, sequence = struct.unpack("!bbHHh", hr)
                
                if types == 11:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    print(" %d rtt=%.0f ms %s" %(ttl,(timeReceived -t)*1000, addr[0]))
                elif types == 3:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    print(" %d rtt=%.0f ms %s" %(ttl,(timeReceived-t)*1000, addr[0]))
                elif types == 0:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    print(" %d rtt=%.0f ms %s" %(ttl,(timeReceived - timeSent)*1000, addr[0]))
                    return
                else:
                    print("error")
                break
            finally:
                mySocket.close()
                
get_route("www.australia.gov.au")