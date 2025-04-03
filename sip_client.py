'''
Implementation of a SIP client in Python.

Task to do:
1. Set up SIP communication over UDP.
2. Implement SIP messages like INVITE, 200 OK, ACK, and BYE.
3. Include an SDP body in the INVITE(contains codec, IP address, port).
4. Handle SIP responses (log errors for 4xx and 5xx responses).
'''
import socket
import uuid
from network_util import send_udp_packet, receive_udp_packet, create_udp_socket
from config import *

def generate_sip_invite(to, from_, call_id, sdp):
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

def generate_sdp_body():
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



def generate_sip_response(status_code, call_id, to, from_):
    """
    Generate a SIP response message.
    """
    return f"SIP/2.0 {status_code} {get_status_message(status_code)}\r\n" \
           f"Via: SIP/2.0/UDP {LOCAL_IP}:{SIP_PORT};branch=z9hG4bK{call_id}\r\n" \
           f"From: <sip:{from_}@{LOCAL_IP}>;tag={call_id}\r\n" \
           f"To: <sip:{to}@{LOCAL_IP}>;tag={call_id}\r\n" \
           f"Call-ID: {call_id}\r\n" \
           f"CSeq: 1 INVITE\r\n" \
           f"Content-Length: 0\r\n\r\n"

def get_status_message(status_code):
    """
    Get the status message for a given SIP status code.
    """
    status_messages = {
        200: "OK",
        404: "Not Found",
        486: "Busy Here",
        500: "Server Internal Error",
        # Add more status codes as needed
    }
    return status_messages.get(status_code, "Unknown Status")

def generate_sip_ack(call_id, to, from_):
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

def generate_sip_bye(call_id, to, from_):
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

def log_sip_message(message):
    """
    Save all SIP messages for debugging purposes.
    """
    with open("sip_log.txt", "a") as log_file:
        log_file.write(message + "\n")
    print(f"Logged SIP message: {message}")

def create_call_id():
    """
    Generate a unique Call-ID for the SIP session.
    """
    return str(uuid.uuid4())

def sip_client(to, from_, call_id):
    """
    Main function to run the SIP client.
    """

    # Create a unique Call-ID for the session
    call_id = create_call_id()
    print(f"Generated Call-ID: {call_id}")

    # Create a UDP socket
    sock = create_udp_socket()

    # Generate SDP body
    sdp = generate_sdp_body()

    # Generate SIP INVITE message
    sip_invite = generate_sip_invite(to, from_, call_id, sdp)
    send_udp_packet(to, SIP_PORT, sip_invite)

    # Wait for SIP response
    addr, response = receive_udp_packet(sock, BUFFER_SIZE)
    print(f"Received response: {response}")

    # Check for SIP response status
    if "200 OK" in response:
        print("Call established successfully.")
        ack_message = generate_sip_ack(call_id, to, from_)
        send_udp_packet(sock, ack_message, (to, SIP_PORT))
    elif response.split()[1].startswith(('4', '5')):
        print(f"Error: {response}")
        log_sip_message(response)

    # Close the socket
    sock.close()
