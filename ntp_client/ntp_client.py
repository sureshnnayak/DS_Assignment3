import json
import socket
import time
from ntp_packet import NTPPacket
from ntp import NTP
import datetime
import os
import logging
import json
import pathlib

class NTPStats(NTPPacket):
    """NTP statistics.

    Wrapper for NTPPacket, offering additional statistics like offset and
    delay, and timestamps converted to system time.
    """

    def __init__(self):
        """Constructor."""
        super(NTPStats, self).__init__()
        self.dest_timestamp = 0
        """destination timestamp"""
        self.ntp = NTP()

    @property
    def offset(self):
        """offset"""
        return ((self.recv_timestamp - self.orig_timestamp) +
                (self.tx_timestamp - self.dest_timestamp)) / 2

    @property
    def delay(self):
        """round-trip delay"""
        return ((self.dest_timestamp - self.orig_timestamp) -
                (self.tx_timestamp - self.recv_timestamp))

    @property
    def tx_time(self):
        """Transmit timestamp in system time."""
        return NTP.ntp_to_system_time(self.tx_timestamp)

    @property
    def recv_time(self):
        """Receive timestamp in system time."""
        return NTP.ntp_to_system_time(self.recv_timestamp)

    @property
    def orig_time(self):
        """Originate timestamp in system time."""
        return NTP.ntp_to_system_time(self.orig_timestamp)

    @property
    def ref_time(self):
        """Reference timestamp in system time."""
        return NTP.ntp_to_system_time(self.ref_timestamp)

    @property
    def dest_time(self):
        """Destination timestamp in system time."""
        return NTP.ntp_to_system_time(self.dest_timestamp)

    @property
    def to_json(self):
        return json.dumps({
            'leap': self.leap,
            'version': self.version,
            'mode': self.mode,
            'stratum': self.stratum,
            'poll': self.poll,
            'precision': self.precision,
            'root_delay': self.root_delay,
            'root_dispersion': self.root_dispersion,
            'ref_id': self.ref_id,
            'ref_timestamp': datetime.datetime.fromtimestamp(NTP.ntp_to_system_time(self.ref_timestamp)).strftime("%m/%d/%Y, %H:%M:%S.%f"),
            'orig_timestamp': datetime.datetime.fromtimestamp(NTP.ntp_to_system_time(self.orig_timestamp)).strftime("%m/%d/%Y, %H:%M:%S.%f"),
            'recv_timestamp': datetime.datetime.fromtimestamp(NTP.ntp_to_system_time(self.recv_timestamp)).strftime("%m/%d/%Y, %H:%M:%S.%f"),
            'tx_timestamp': datetime.datetime.fromtimestamp(NTP.ntp_to_system_time(self.tx_timestamp)).strftime("%m/%d/%Y, %H:%M:%S.%f")
        })


class NTPClient(object):
    """NTP client session."""

    def __init__(self):
        """Constructor."""
        pass

    def request(self, host, version=2, port="ntp", timeout=5):
        """Query a NTP server.

        Returns:
        NTPStats object
        """
        # lookup server address
        if host == 'localhost' or '127.0.0.1':
            addrinfo = socket.getaddrinfo(host, port)[0]
            family, sockaddr = addrinfo[0], addrinfo[4]
        else:
            family, sockaddr = socket.AF_INET, ('localhost', 123)

        # create the socket
        s = socket.socket(family, socket.SOCK_DGRAM)

        try:
            s.settimeout(timeout)

            # create the request packet - mode 3 is client
            query_packet = NTPPacket(
                mode=3,
                version=version,
                tx_timestamp=NTP.system_to_ntp_time(time.time())
            )

            # send the request
            s.sendto(query_packet.to_data(), sockaddr)

            # wait for the response - check the source address
            src_addr = None,
            while src_addr[0] != sockaddr[0]:
                response_packet, src_addr = s.recvfrom(256)
            # build the destination timestamp
            dest_timestamp = NTP.system_to_ntp_time(time.time())
        except socket.timeout:
            print("No response received from %s." % host)
            return None, None
        finally:
            s.close()

        # construct corresponding statistics
        stats = NTPStats()
        stats.from_data(response_packet)
        stats.dest_timestamp = dest_timestamp

        return query_packet, stats


if __name__ == '__main__':

    # path to src directory
    # if env not provided uses remote ntp server
    host = os.getenv("NTP_SERVER","pool.ntp.org")
    port = int(os.getenv("NTP_PORT","123"))
    src_dir = pathlib.Path(__file__).parent.resolve()
    logging.basicConfig(filename=f"{src_dir}/logs/client_{host}.log",
                    format='%(message)s',
                    )
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    c = NTPClient()

    input, output = [], []
    total_delay, total_offset = [], []
    delay_o, offset_o = [],[]
    burst_counter, time_counter, retransmit_counter = 0, 0, 0

    try:
        while (True):
            while (True):
                #host = 'localhost'
                #port = 1234

                query_packet, response = c.request(host=host, port=port, version=3)
                if not response:
                    print("packet retransmitting..")
                    retransmit_counter += 1
                    if retransmit_counter == 10:
                        break
                    continue
                input.append(query_packet.to_json())
                output.append(response.to_json)

                total_delay.append(response.delay)
                total_offset.append(response.offset)

                print("Burst packet - transmit")
                burst_counter += 1
                if burst_counter == 8:
                    burst_counter = 0
                    break
            if len(output) == 0:
                print("The server is out of service. all the message retransmitted failed. ")
                break
            logger.info(input)
            logger.info(output)

            offset_o.append(min(total_offset[::-1][0:4]))
            delay_o.append(min(total_delay[::-1][0:4]))
            print("Sleeping for 4 mins....")
            
            if time_counter >= 15:
                break
            time.sleep(4 * 60)
            time_counter += 1
            input, output = [],[]
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        data =  {
                    "total_delay" : total_delay, 
                    "total_offset" : total_offset, 
                    "delay0" : delay_o, 
                    "offset0" : offset_o
                }

        with open(f"{src_dir}/logs/plotting_data_{host}.json", 'a') as f:
            json.dump(data, f)