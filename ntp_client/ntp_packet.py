import json
import struct
from ntp import NTP, NTPException
import datetime

class NTPPacket(object):
    _PACKET_FORMAT = "!B B B b 11I"
    """packet format to pack/unpack"""

    def __init__(self, version=2, mode=3, tx_timestamp=0):
        """Constructor.

        Parameters:
        version      -- NTP version
        mode         -- packet mode (client, server)
        tx_timestamp -- packet transmit timestamp
        """
        self.leap = 0
        self.version = version
        self.mode = mode
        self.stratum = 0
        self.poll = 0
        self.precision = 0
        self.root_delay = 0
        self.root_dispersion = 0
        self.ref_id = 0
        self.ref_timestamp = 0
        self.orig_timestamp = 0
        self.orig_timestamp_high = 0
        self.orig_timestamp_low = 0
        self.recv_timestamp = 0
        self.tx_timestamp = tx_timestamp
        self.tx_timestamp_high = 0
        self.tx_timestamp_low = 0
        self.ntp = NTP()

    def to_data(self):
        """Convert this NTPPacket to a buffer that can be sent over a socket.

        Returns:
        buffer representing this packet

        Raises:
        NTPException -- in case of invalid field
        """
        try:
            packed = struct.pack(
                NTPPacket._PACKET_FORMAT,
                (self.leap << 6 | self.version << 3 | self.mode),
                self.stratum,
                self.poll,
                self.precision,
                self.ntp._to_int(self.root_delay) << 16 | self.ntp._to_frac(self.root_delay, 16),
                self.ntp._to_int(self.root_dispersion) << 16 |
                self.ntp._to_frac(self.root_dispersion, 16),
                self.ref_id,
                self.ntp._to_int(self.ref_timestamp),
                self.ntp._to_frac(self.ref_timestamp),
                self.orig_timestamp_high,
                self.orig_timestamp_low,
                self.ntp._to_int(self.recv_timestamp),
                self.ntp._to_frac(self.recv_timestamp),
                self.ntp._to_int(self.tx_timestamp),
                self.ntp._to_frac(self.tx_timestamp))
        except struct.error:
            raise NTPException("Invalid NTP packet fields.")
        return packed

    def from_data(self, data):
        """Populate this instance from a NTP packet payload received from
        the network.

        Parameters:
        data -- buffer payload

        Raises:
        NTPException -- in case of invalid packet format
        """
        try:
            unpacked = struct.unpack(
                NTPPacket._PACKET_FORMAT,
                data[0:struct.calcsize(NTPPacket._PACKET_FORMAT)]
            )
        except struct.error:
            raise NTPException("Invalid NTP packet.")

        self.leap = unpacked[0] >> 6 & 0x3
        self.version = unpacked[0] >> 3 & 0x7
        self.mode = unpacked[0] & 0x7
        self.stratum = unpacked[1]
        self.poll = unpacked[2]
        self.precision = unpacked[3]
        self.root_delay = float(unpacked[4])/2**16
        self.root_dispersion = float(unpacked[5])/2**16
        self.ref_id = unpacked[6]
        self.ref_timestamp = self.ntp._to_time(unpacked[7], unpacked[8])
        self.orig_timestamp = self.ntp._to_time(unpacked[9], unpacked[10])
        self.orig_timestamp_high = unpacked[9]
        self.orig_timestamp_low = unpacked[10]
        self.recv_timestamp = self.ntp._to_time(unpacked[11], unpacked[12])
        self.tx_timestamp = self.ntp._to_time(unpacked[13], unpacked[14])
        self.tx_timestamp_high = unpacked[13]
        self.tx_timestamp_low = unpacked[14]

    def GetTxTimeStamp(self):
        return (self.tx_timestamp_high,self.tx_timestamp_low)

    def SetOriginTimeStamp(self,high,low):
        self.orig_timestamp_high = high
        self.orig_timestamp_low = low

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
            'ref_timestamp': datetime.datetime.fromtimestamp( NTP.ntp_to_system_time(self.ref_timestamp)).strftime("%m/%d/%Y, %H:%M:%S.%f"),
            'orig_timestamp': datetime.datetime.fromtimestamp(NTP.ntp_to_system_time(self.orig_timestamp)).strftime("%m/%d/%Y, %H:%M:%S.%f"),
            'recv_timestamp': datetime.datetime.fromtimestamp(NTP.ntp_to_system_time(self.recv_timestamp)).strftime("%m/%d/%Y, %H:%M:%S.%f"),
            'tx_timestamp': datetime.datetime.fromtimestamp(NTP.ntp_to_system_time(self.tx_timestamp)).strftime("%m/%d/%Y, %H:%M:%S.%f")
        })