import socket
import select
import re
from sip import *
from rtp import parse_rtp_packet
from audio_utils import play_audio_stream
from config import *

# Validate the audio format of the RTP payload
EXPECTED_SAMPLE_RATE = 8000  # 8 kHz
EXPECTED_CHANNELS = 1        # Mono
EXPECTED_BIT_DEPTH = 16      # 16-bit PCM

def validate_audio_format(sample_rate, channels, bit_depth):
    if sample_rate != EXPECTED_SAMPLE_RATE:
        raise ValueError(f"Unsupported sample rate: {sample_rate} Hz. Expected: {EXPECTED_SAMPLE_RATE} Hz.")
    if channels != EXPECTED_CHANNELS:
        raise ValueError(f"Unsupported number of channels: {channels}. Expected: {EXPECTED_CHANNELS}.")
    if bit_depth != EXPECTED_BIT_DEPTH:
        raise ValueError(f"Unsupported bit depth: {bit_depth}-bit. Expected: {EXPECTED_BIT_DEPTH}-bit.")

# SIP and RTP setup
sip_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sip_sock.bind((LOCAL_IP, SIP_PORT))

rtp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rtp_sock.bind((LOCAL_IP, RTP_PORT))

try:
    # sip_sock.settimeout(5)  # uncomment after testing
    # Handle SIP INVITE
    try:
        data, addr = sip_sock.recvfrom(1024)
        print("Received SIP message:", data.decode())
    except socket.timeout:
        print("Timeout waiting for SIP message.")
        sip_sock.close()
        rtp_sock.close()
        exit(1)
    
    # Decode the SIP message
    decoded_data = data.decode(errors="ignore")

    # Extract Call-ID using regex
    call_id_match = re.search(r"Call-ID:\s*(\S+)", decoded_data)
    if call_id_match:
        call_id = call_id_match.group(1)
        print("Extracted Call-ID:", call_id)
    else:
        print("Call-ID not found")

    if b"INVITE" in data:
        sip_sock.sendto(build_ok(call_id, "caller", "callee").encode(), addr) # id, to, from_
        print("Sent 200 OK")

        # Wait for ACK
        data, _ = sip_sock.recvfrom(1024)
        if b"ACK" in data:
            print("Received ACK, starting RTP session")

            print(data.decode(errors="ignore")) # delete after testing

            # Validate audio format (adjust these values based on your RTP payload format)
            try:
                validate_audio_format(sample_rate=8000, channels=1, bit_depth=16)
            except ValueError as e:
                print(f"Audio format mismatch: {e}")
                sip_sock.close()
                rtp_sock.close()
                exit(1)

            # Start RTP session with validated audio format
            stream = play_audio_stream(sample_rate=8000, channels=1, bit_depth=16)
            frame_count = 0
            sockets = [rtp_sock, sip_sock]

            while True:
                readable, _, _ = select.select(sockets, [], [])

                for sock in readable:
                    data, addr = sock.recvfrom(2048)

                    if sock == sip_sock:
                        if b"BYE" in data:
                            # from ack to ok
                            print("Received BYE, ending call")
                            sip_sock.sendto(build_ok(call_id, "caller", "callee").encode(), addr) # send okay instead of ack
                            print("Sent 200 OK")
                            # sip_sock.sendto(build_ack(call_id, "caller", "callee").encode(), addr) # call_id, to, from_
                            raise SystemExit
                        else:
                            print("Received SIP message:", data.decode(errors="ignore"))

                    elif sock == rtp_sock:
                        try:
                            header, payload = parse_rtp_packet(data)
                            stream.write(payload)
                            print(f"Received frame #{frame_count}, "
                                  f"Sequence: {header['sequence_number']}, "
                                  f"Timestamp: {header['timestamp']}, "
                                  f"Size: {len(payload)} bytes")
                            frame_count += 1
                        except Exception as e:
                            print(f"Error parsing RTP packet: {e}")
except Exception as e:
    print("Error:", e)
finally:
    sip_sock.close()
    rtp_sock.close()
    if 'stream' in locals():
        stream.close()  # Ensure the audio stream is closed
    print("Sockets and audio stream closed.")