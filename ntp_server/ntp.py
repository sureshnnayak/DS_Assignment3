import datetime
import time
class NTP:
    """Helper class defining constants."""

    _SYSTEM_EPOCH = datetime.date(*time.gmtime(0)[0:3])
    """system epoch"""
    _NTP_EPOCH = datetime.date(1900, 1, 1)
    """NTP epoch"""
    NTP_DELTA = (_SYSTEM_EPOCH - _NTP_EPOCH).days * 24 * 3600
    """delta between system and NTP time"""

    REF_ID_TABLE = {
        "GOES":  "Geostationary Orbit Environment Satellite",
        "GPS\0": "Global Position System",
        "GAL\0": "Galileo Positioning System",
        "PPS\0": "Generic pulse-per-second",
        "IRIG":  "Inter-Range Instrumentation Group",
        "WWVB":  "LF Radio WWVB Ft. Collins, CO 60 kHz",
        "DCF\0": "LF Radio DCF77 Mainflingen, DE 77.5 kHz",
        "HBG\0": "LF Radio HBG Prangins, HB 75 kHz",
        "MSF\0": "LF Radio MSF Anthorn, UK 60 kHz",
        "JJY\0": "LF Radio JJY Fukushima, JP 40 kHz, Saga, JP 60 kHz",
        "LORC":  "MF Radio LORAN C station, 100 kHz",
        "TDF\0": "MF Radio Allouis, FR 162 kHz",
        "CHU\0": "HF Radio CHU Ottawa, Ontario",
        "WWV\0": "HF Radio WWV Ft. Collins, CO",
        "WWVH":  "HF Radio WWVH Kauai, HI",
        "NIST":  "NIST telephone modem",
        "ACTS":  "NIST telephone modem",
        "USNO":  "USNO telephone modem",
        "PTB\0": "European telephone modem",
        "LOCL":  "uncalibrated local clock",
        "CESM":  "calibrated Cesium clock",
        "RBDM":  "calibrated Rubidium clock",
        "OMEG":  "OMEGA radionavigation system",
        "DCN\0": "DCN routing protocol",
        "TSP\0": "TSP time protocol",
        "DTS\0": "Digital Time Service",
        "ATOM":  "Atomic clock (calibrated)",
        "VLF\0": "VLF radio (OMEGA,, etc.)",
        "1PPS":  "External 1 PPS input",
        "FREE":  "(Internal clock)",
        "INIT":  "(Initialization)",
        "ROA\0": "Real Observatorio de la Armada",
        "\0\0\0\0":   "NULL",
    }
    """reference identifier table"""

    STRATUM_TABLE = {
        0: "unspecified or invalid",
        1: "primary reference (%s)",
    }
    """stratum table"""

    MODE_TABLE = {
        0: "reserved",
        1: "symmetric active",
        2: "symmetric passive",
        3: "client",
        4: "server",
        5: "broadcast",
        6: "reserved for NTP control messages",
        7: "reserved for private use",
    }
    """mode table"""

    LEAP_TABLE = {
        0: "no warning",
        1: "last minute of the day has 61 seconds",
        2: "last minute of the day has 59 seconds",
        3: "unknown (clock unsynchronized)",
    }
    """leap indicator table"""

    def system_to_ntp_time(self, timestamp):
        return timestamp + NTP.NTP_DELTA


    def _to_int(self, timestamp):
        return int(timestamp)


    def _to_frac(self, timestamp, n=32):
        return int(abs(timestamp - self._to_int(timestamp)) * 2 ** n)


    def _to_time(self, integ, frac, n=32):
        return integ + float(frac) / 2 ** n

    def ntp_to_system_time(timestamp):
        return timestamp - NTP.NTP_DELTA

    def system_to_ntp_time(timestamp):
        return timestamp + NTP.NTP_DELTA

    def leap_to_text(leap):
        if leap in NTP.LEAP_TABLE:
            return NTP.LEAP_TABLE[leap]
        else:
            raise NTPException("Invalid leap indicator.")

    def mode_to_text(mode):
        if mode in NTP.MODE_TABLE:
            return NTP.MODE_TABLE[mode]
        else:
            raise NTPException("Invalid mode.")

    def stratum_to_text(stratum):
        if stratum in NTP.STRATUM_TABLE:
            return NTP.STRATUM_TABLE[stratum] % stratum
        elif 1 < stratum < 16:
            return "secondary reference (%s)" % stratum
        elif stratum == 16:
            return "unsynchronized (%s)" % stratum
        else:
            raise NTPException("Invalid stratum or reserved.")

    def ref_id_to_text(ref_id, stratum=2):
        fields = (ref_id >> 24 & 0xff, ref_id >> 16 & 0xff,
                  ref_id >> 8 & 0xff, ref_id & 0xff)

        # return the result as a string or dot-formatted IP address
        if 0 <= stratum <= 1:
            text = "%c%c%c%c" % fields
            if text in NTP.REF_ID_TABLE:
                return NTP.REF_ID_TABLE[text]
            else:
                return "Unidentified reference source '%s'" % text
        elif 2 <= stratum < 255:
            return "%d.%d.%d.%d" % fields
        else:
            raise NTPException("Invalid stratum.")

class NTPException(Exception):
    pass
