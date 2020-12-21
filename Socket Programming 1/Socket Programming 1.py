#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 27 18:50:04 2019

@author: ginajoerger
"""

#import socket module
from socket import *
import sys #In order to terminate the program

#Prepare a server socket
serverPort = 8070 #declared server port
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort)) #binds port to address
serverSocket.listen(1) #listen to one connection at a time
    
while True:
    #Establish the connection
    print('Ready to serve...')
    connectionSocket, addr = serverSocket.accept() #accept and establish new connection
    try:
        message = connectionSocket.recv(1024)
        filename = message.split()[1]
        f = open(filename[1:])
        outputdata = f.read()

        connectionSocket.send(b'HTTP/1.1 200 OK\r\n\r\n') #Send one HTTP header line into socket

        #Send the content of the requested file to the client
        for i in range(0, len(outputdata)):
            connectionSocket.send(outputdata[i].encode('utf-8'))
        connectionSocket.send(b"\r\n")
        connectionSocket.close()
    except IOError:
        #Send response message for file not found
        connectionSocket.send(b'HTTP/1.1 404 Not Found\r\n\r\n')
        connectionSocket.send(b"<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n")
        #Close client socket
        connectionSocket.close()

serverSocket.close()
sys.exit() #Terminate the program after sending the corresponding data