#import socket
from socket import socket, AF_INET, SOCK_DGRAM
from contextlib import closing
import datetime
import struct


NTP_PACKET_FORMAT = "!12I"

"""
In the context of Network Time Protocol (NTP), NTP_DELTA refers to the difference between the Unix 
epoch time (January 1, 1970) and the NTP epoch time (January 1, 1900). This value is subtracted 
from the NTP timestamp to convert it into Unix epoch time.
"""
NTP_DELTA = 2208988800  # 1970-01-01 00:00:00
NTP_QUERY = b'\x1b' + 47 * b'\0' 

# Here we define the UDP IP address as well as the port number that we have 
# already defined in the client python script.
UDP_IP_ADDRESS = "127.0.0.1"
UDP_PORT_NO = 1234

serverSock = socket(AF_INET, SOCK_DGRAM)
serverSock.bind((UDP_IP_ADDRESS, UDP_PORT_NO))



def getTime():
    t = datetime.datetime.now().timestamp() + NTP_DELTA
    arr = str(t).split('.')
    return (int(arr[0]), int(arr[1]))
    

while True:
    data, addr = serverSock.recvfrom(1024)
    server_receipt_timestamp_secs, server_receipt_timestamp_ms = getTime()
    print("system time :", getTime())
    server_send_timestamp_secs, server_send_timestamp_ms = getTime()
    severresponse = struct.pack("!12I", 0, 0, 0, 0, 0, 0, 0, 0, server_receipt_timestamp_secs, server_receipt_timestamp_ms, server_send_timestamp_secs, server_send_timestamp_ms)
    serverSock.sendto(severresponse, addr)
