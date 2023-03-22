#!/usr/bin/env python
from contextlib import closing
from socket import socket, AF_INET, SOCK_DGRAM
import struct
import datetime
import time

import matplotlib.pyplot as plt

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
        T1 =  float(str(client_origin_timestamp_secs) +"."+ str(client_origin_timestamp_secs))
        T2 = float(str(unpacked[8]) +"."+ str(unpacked[9]))
        T3 = float(str(unpacked[10]) +"."+ str(unpacked[11]))
        T4 = float(str(getTime()[0]) +"."+ str(getTime()[1]))
        return T1,T2,T3, T4

def NTP_burst(host,port):
    delta = []
    offset = []
    min_delay = float('inf')
    min_offset = float('inf')
    
    for i in range(8):
        if host==None:
            T1, T2, T3, T4 = get_ntp_time()
        else:
            T1, T2, T3, T4 = get_ntp_time(host,port)
        d = (T4-T1) - (T3-T2)
        delta.append(d)
        o = ((T2-T1) + (T3-T4))/2
        offset.append(o)
        if d < min_delay:
            min_delay = d
            min_offset = o
        # time.sleep(1)
    return min_delay, min_offset


if __name__ == "__main__":
    # host = "127.0.0.1"
    # port = 1234

    host = "pool.ntp.org"
    port = 123

    # host = "pool.ntp.org"
    # port = 123
    arr_delay = []
    arr_offset = []
    for i in range(15):
        print("Iteration: ", i)
        delay, offset =  NTP_burst(host,port)
        arr_delay.append(delay)
        arr_offset.append(offset)
        time.sleep(2)
    print("Delay: ", arr_delay)
    print("Offset: ", arr_offset)

    
    # read the data from the CSV file
    
    x = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
    plt.plot(x, arr_delay, label="Delay")
    plt.plot(x, arr_offset, label="Offset")
    plt.xlabel("Count")
    plt.ylabel("values: delay, offset")
    plt.savefig("local.png")
    plt.legend()

    # show the plot
    plt.show()

