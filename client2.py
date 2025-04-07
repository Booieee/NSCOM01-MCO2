import socket
from sip import build_ok, build_ack
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
    sip_sock.settimeout(5)  # Set a 5-second timeout for SIP responses
    # Handle SIP INVITE
    try:
        data, addr = sip_sock.recvfrom(1024)
        print("Received SIP message:", data.decode())
    except socket.timeout:
        print("Timeout waiting for SIP message.")
        sip_sock.close()
        rtp_sock.close()
        exit(1)

    if b"INVITE" in data:
        sip_sock.sendto(build_ok().encode(), addr)
        print("Sent 200 OK")

        # Wait for ACK
        data, _ = sip_sock.recvfrom(1024)
        if b"ACK" in data:
            print("Received ACK, starting RTP session")

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

            while True:
                try:
                    data, _ = rtp_sock.recvfrom(2048)
                    if not data:
                        break

                    # Check for BYE message during RTP session
                    if b"BYE" in data:
                        print("Received BYE, ending call")
                        sip_sock.sendto(build_ack().encode(), addr)
                        break

                    try:
                        # Use the improved parse_rtp_packet function
                        header, payload = parse_rtp_packet(data)
                        stream.write(payload)  # Write raw PCM data to the audio stream
                        print(f"Received frame #{frame_count}, "
                            f"Sequence: {header['sequence_number']}, "
                            f"Timestamp: {header['timestamp']}, "
                            f"Size: {len(payload)} bytes")
                        frame_count += 1
                    except Exception as e:
                        print(f"Error parsing RTP packet: {e}")

                except KeyboardInterrupt:
                    print("RTP session interrupted")
                    break
except Exception as e:
    print("Error:", e)
finally:
    sip_sock.close()
    rtp_sock.close()
    if 'stream' in locals():
        stream.close()  # Ensure the audio stream is closed
    print("Sockets and audio stream closed.")