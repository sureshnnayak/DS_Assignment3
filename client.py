#!/usr/bin/env python
from contextlib import closing
from socket import socket, AF_INET, SOCK_DGRAM
import struct
import datetime
import time

NTP_PACKET_FORMAT = "!12I"
NTP_DELTA = 2208988800  # 1970-01-01 00:00:00
NTP_QUERY = b'\x1b' + 47 * b'\0'  


def getTime():
    t = datetime.datetime.now().timestamp() + NTP_DELTA
    arr = str(t).split('.')
    return (int(arr[0]), int(arr[1]))



"""
T1  is  Origin  Timestamp field  of  the  response  message;
T2  is  the  Receive Timestamp field  of  the response message;  
T3  is  the  Transmit Timestamp field  of  the  response  message;  and  
T4  is  the  time  this response  message arrived
"""

def get_ntp_time(host="pool.ntp.org", port=123):
    client = socket(AF_INET, SOCK_DGRAM)
    client_origin_timestamp_secs, client_origin_timestamp_ms = getTime()
    client_msg = b'\x1b' + 47 * b'\0'  # NTP request packet
    client.sendto(client_msg, (host, port))
  
    data, address = client.recvfrom(1024)
    if data:
        unpacked = struct.unpack(NTP_PACKET_FORMAT,data)
        T1 =  str(client_origin_timestamp_secs) +"."+ str(client_origin_timestamp_secs)
        T2 = str(unpacked[8]) +"."+ str(unpacked[9])
        T3 = str(unpacked[10]) +"."+ str(unpacked[11])
        return T1,T2,T3


if __name__ == "__main__":
    #print (time.ctime(ntp_time()))
    print(get_ntp_time("127.0.0.1", 1234))
    print("\nTime from NTP Server")
    print(get_ntp_time())