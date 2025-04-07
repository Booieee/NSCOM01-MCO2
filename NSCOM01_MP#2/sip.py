import socket
import uuid
import threading
from network_util import send_udp_packet, receive_udp_packet, create_udp_socket
from config import *

def build_invite(to, from_, call_id, sdp):
    """
    Generate a SIP INVITE message.
    """
    return f"INVITE sip:{to}@{LOCAL_IP}:{SIP_PORT} SIP/2.0\r\n" \
           f"Via: SIP/2.0/UDP {LOCAL_IP}:{SIP_PORT};branch=z9hG4bK{call_id}\r\n" \
           f"From: <sip:{from_}@{LOCAL_IP}>;tag={call_id}\r\n" \
           f"To: <sip:{to}@{LOCAL_IP}>\r\n" \
           f"Call-ID: {call_id}\r\n" \
           f"CSeq: 1 INVITE\r\n" \
           f"Contact: <sip:{from_}@{LOCAL_IP}:{SIP_PORT}>\r\n" \
           f"Content-Type: application/sdp\r\n" \
           f"Content-Length: {len(sdp)}\r\n\r\n" \
           f"{sdp}"

def build_ok():
    return "SIP/2.0 200 OK\r\n\r\n"

# delete if the new generator works
def generate_sdp_body_before():
    """
    Generate an SDP body for the INVITE message.
    """
    return f"v=0\r\n" \
           f"o=- 0 0 IN IP4 {LOCAL_IP}\r\n" \
           f"s=Session\r\n" \
           f"c=IN IP4 {LOCAL_IP}\r\n" \
           f"t=0 0\r\n" \
           f"a=tool:libavformat 58.29.100\r\n" \
           f"a=recvonly\r\n" \
           f"m=audio {RTP_PORT} RTP/AVP {AUDIO_CODEC}\r\n" \
           f"a=rtpmap:{AUDIO_CODEC} PCMU/8000\r\n"

# remove after testing main generator
def generate_sdp_body_2():
    return (
        "v=0\r\n"
        "o=- 0 0 IN IP4 127.0.0.1\r\n"
        "s=Audio Session\r\n"
        "c=IN IP4 127.0.0.1\r\n"
        "t=0 0\r\n"
        "m=audio 8000 RTP/AVP 0\r\n"
        "a=rtpmap:0 PCMU/8000/1\r\n"  # PCMU codec, 8kHz, mono
    )

def generate_sdp_body():
    """
    Generate an SDP body for the INVITE message.
    """
    return (
        "v=0\r\n"
        "o=- 0 0 IN IP4 127.0.0.1\r\n"
        "s=Audio Session\r\n"
        "c=IN IP4 127.0.0.1\r\n"
        "t=0 0\r\n"
        "m=audio 8000 RTP/AVP 0 96\r\n"  # PCMU (0) and dynamic payload type (96)
        "a=rtpmap:0 PCMU/8000/1\r\n"
        "a=rtpmap:96 L16/8000/1\r\n"  # Linear PCM (16-bit)
    )

def build_ack(call_id, to, from_):
    """
    Generate a SIP ACK message.
    """
    return f"ACK sip:{to}@{LOCAL_IP}:{SIP_PORT} SIP/2.0\r\n" \
           f"Via: SIP/2.0/UDP {LOCAL_IP}:{SIP_PORT};branch=z9hG4bK{call_id}\r\n" \
           f"From: <sip:{from_}@{LOCAL_IP}>;tag={call_id}\r\n" \
           f"To: <sip:{to}@{LOCAL_IP}>;tag={call_id}\r\n" \
           f"Call-ID: {call_id}\r\n" \
           f"CSeq: 2 ACK\r\n" \
           f"Content-Length: 0\r\n\r\n"

def build_ack_bye(call_id, to, from_):
    """
    Generate a SIP BYE message.
    """
    return f"BYE sip:{to}@{LOCAL_IP}:{SIP_PORT} SIP/2.0\r\n" \
           f"Via: SIP/2.0/UDP {LOCAL_IP}:{SIP_PORT};branch=z9hG4bK{call_id}\r\n" \
           f"From: <sip:{from_}@{LOCAL_IP}>;tag={call_id}\r\n" \
           f"To: <sip:{to}@{LOCAL_IP}>;tag={call_id}\r\n" \
           f"Call-ID: {call_id}\r\n" \
           f"CSeq: 3 BYE\r\n" \
           f"Content-Length: 0\r\n\r\n"