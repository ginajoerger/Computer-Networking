#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 23:51:00 2019

@author: ginajoerger
"""
import random
from socket import *

def main():
    host = 'localhost'
    port = 12000
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    print('Server: Socket Created')

    serverSocket.bind((host, port))
    print('Server: Socket connected to ' + host)

    while True:
        rand = random.randint(0, 10)
        message, address = serverSocket.recvfrom(1024)
        if rand < 4:
            continue

        serverSocket.sendto(message, address)
        
if __name__ == '__main__':
    main()