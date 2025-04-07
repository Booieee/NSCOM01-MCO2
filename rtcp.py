import struct
import time

def build_rtcp_sender_report(ssrc, rtp_timestamp, packet_count, octet_count):
    """
    Builds an RTCP Sender Report packet.
    :param ssrc: Synchronization source identifier (integer).
    :param rtp_timestamp: RTP timestamp of the last sent packet.
    :param packet_count: Total number of RTP packets sent.
    :param octet_count: Total number of bytes sent in RTP payloads.
    :return: RTCP Sender Report packet as bytes.
    """
    ntp_timestamp = int(time.time()) + 2208988800  # Convert UNIX time to NTP time
    ntp_frac = int((time.time() % 1) * (2**32))  # Fractional part of NTP timestamp

    # RTCP Sender Report Header (8 bytes)
    rtcp_header = struct.pack('!BBH', 0x80, 200, 6)  # Version 2, SR type (200), length 6 words

    # Sender Report Body
    sender_info = struct.pack('!IIIIII', ssrc, ntp_timestamp, ntp_frac, rtp_timestamp, packet_count, octet_count)

    return rtcp_header + sender_info
