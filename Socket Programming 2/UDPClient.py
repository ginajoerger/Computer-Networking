#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 23:56:40 2019

@author: ginajoerger
"""
from socket import *
from time import time, ctime
import sys

def main():
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    print('Client: Socket Created')
    serverHost = 'localhost'
    serverPort = 12000
    clientSocket.settimeout(1)

    for i in range(10):
        startTime = time()
        message = "PING " + str(i+1) + " " + ctime(startTime)[11:19]

        try:
            clientSocket.sendto(message.encode(),(serverHost, int(serverPort)))
            encoded, serverAddress = clientSocket.recvfrom(1024)

            endTime = time()
            modified = encoded.decode()
            print(modified)
            print("RTT: %.3f ms\n" % ((endTime - startTime)*1000))
        except:
            print("PING %i Request timed out\n" % (i+1))

    clientSocket.close()

if __name__ == '__main__':
    main()
    
    