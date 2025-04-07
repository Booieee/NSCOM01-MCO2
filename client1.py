import os
import socket
import time
import uuid
from sip import build_invite, build_ack, build_ack_bye, generate_sdp_body
from rtp import *  # Assuming you have this
from config import * #specify rtp port in config.py

# check current directory for debugging
print("Current directory: ", os.getcwd()) # remove after testing
file_name = "audio.mp3" # default file name for testing
while True:
    file_name = input("Enter the audio file name (e.g. audio.mp3): ")
    try:
        # Check if the audio file exists
        with open(file_name, 'rb') as f:
            print(f"File '{file_name}' found.")
            break
    except FileNotFoundError:
        print(f"File '{file_name}' not found in the current directory: {os.getcwd()}. Please try again.")

receiver_ip = '127.0.0.1'
receiver_sip_port = SIP_PORT
receiver_rtp_port = RTP_PORT

# SIP Setup
call_id = str(uuid.uuid4())  # Unique call identifier
sdp = generate_sdp_body()

sip_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

invite_msg = build_invite("callee", "caller", call_id, sdp)
sip_sock.sendto(invite_msg.encode(), (receiver_ip, receiver_sip_port))
print("Sent INVITE")

sip_sock.settimeout(5)  # Set a 5-second timeout for SIP responses

try:
    data, _ = sip_sock.recvfrom(1024)
    if b"200 OK" in data:
        print("Received 200 OK")
        ack_msg = build_ack(call_id, "callee", "caller")
        sip_sock.sendto(ack_msg.encode(), (receiver_ip, receiver_sip_port))
        print("Sent ACK")

        # Start RTP streaming
        rtp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        seq = 0
        timestamp = 0

        for frame in read_audio_frames(file_name):  # Supports MP3, WAV, etc.
            pkt = build_rtp_packet(frame, sequence_number=seq, timestamp=timestamp)
            rtp_sock.sendto(pkt, (receiver_ip, receiver_rtp_port))

            print(f"Sent frame #{seq}, Timestamp: {timestamp}, Size: {len(frame)} bytes")
            time.sleep(0.02)  # Simulate real-time
            seq += 1
            timestamp += 160

        # Send BYE after streaming
        bye_msg = build_ack_bye(call_id, "callee", "caller") # call_id, to, from_ 
        sip_sock.sendto(bye_msg.encode(), (receiver_ip, receiver_sip_port))
        print("Sent BYE")
        try:
            data, _ = sip_sock.recvfrom(1024)
            if b"200 OK" in data:
                print("Received 200 OK, call terminated.")
        except socket.timeout:
            print("No ACK for BYE, terminating anyway.")
    else:
        print("Did not receive 200 OK, call failed.")
except socket.timeout:
    print("Timeout waiting for 200 OK, call failed.")
    sip_sock.close()
    exit(1)
finally:
    sip_sock.close()
    rtp_sock.close()
    print("Sockets closed.")

