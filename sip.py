# import socket
# import uuid
# import threading
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

def build_ok(call_id, to_user, from_user):
    return (
        "SIP/2.0 200 OK\r\n"
        f"Via: SIP/2.0/UDP 127.0.0.1:5060\r\n"
        f"From: <sip:{from_user}@127.0.0.1>\r\n"
        f"To: <sip:{to_user}@127.0.0.1>\r\n"
        f"Call-ID: {call_id}\r\n"
        "CSeq: 1 BYE\r\n"
        "Content-Length: 0\r\n"
        "\r\n"
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