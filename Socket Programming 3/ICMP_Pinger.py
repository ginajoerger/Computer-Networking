import socket
import os
import sys
import struct
import time
import select
import binascii

ICMP_ECHO_REQUEST = 8

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


def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout

    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []:  # Timeout
            return "Request timed out."

        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

        # Fill in start
        hr = recPacket[20:28]
        types, code, checksum, packetID, sequence = struct.unpack("!bbHHh", hr)
        if packetID == ID and types == 0:
            TTL = ord(struct.unpack("!c", recPacket[8:9])[0].decode())
            theByteSize = struct.calcsize("!d")
            timeSent = struct.unpack("!d", recPacket[28:28 + theByteSize])[0]
            delayTime = timeReceived - timeSent
            return (delayTime, TTL, theByteSize)
        # Fill in end

        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return "Request timed out."


def sendOnePing(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)

    myChecksum = 0
    # Make a dummy header with a 0 checksum.
    # struct -- Interpret strings as packed binary data
    header = struct.pack("!bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("!d", time.time())
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)
    
    #if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network byte order
        #myChecksum = htons(myChecksum) & 0xffff 
    #else:
        #myChecksum = htons(myChecksum)

    header = struct.pack("!bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data

    mySocket.sendto(packet, (destAddr, 1))  # AF_INET address must be tuple, not str
    # Both LISTS and TUPLES consist of a number of objects
    # which can be referenced by their position number within the object


def doOnePing(destAddr, timeout):
    icmp = socket.getprotobyname("icmp")

    # SOCK_RAW is a powerful socket type. For more details see: http://sock-raw.org/papers/sock_raw

    mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)

    myID = os.getpid() & 0xFFFF  # Return the current process i
    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)

    mySocket.close()
    return delay


def ping(host, timeout=1):
    # timeout=1 means: If one second goes by without a reply from the server,
    # the client assumes that either the client’s ping or the server’s pong is lost
    dest = socket.gethostbyname(host)
    print("Pinging " + dest + " using Python:")
    print("")
    # Send ping requests to a server separated by approximately one second

    counter = 0
    for i in range(5):
        x = doOnePing(dest, timeout)
        if not x:
            print("Request timed out.")
            counter += 1
        else:
            delay = int(x[0]*100000)
            neededTime = x[1]
            num = x[2]
            print("Received from: " + dest)
            print("    Byte(s) = " + str(num))
            print("    Delay = " + str(delay))
            print("    TTL = " + str(neededTime))
        time.sleep(1)  # one second
    print("")
    print("Packets Sent = " + str(5) + ", Packets Received = " + str(5-counter) + ", Packets Lost = " + str(counter))
    print("")
    
    return


ping("127.0.0.1")