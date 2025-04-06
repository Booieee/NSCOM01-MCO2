'''
Implementaion of RTP and RTCP Streaming

Task to do:
1. Implement RTP packetization (read audio file and send frames).
2. Send Audio via UDP to the other client.
3. Receive RTP packets and reconstruct audio stream.
4. Implement RTCP for minimal statistics (packet loss, jitter).
'''

import socket
import wave
import struct
import time
from config import *
from audio_handler import read_and_encode_audio, receive_with_jitter_buffer

def create_rtp_header(sequence_number, timestamp):
    """
    Create an RTP header.
    """
    rtp_header = 0
    rtp_header |= (RTP_VERSION << 30)  # Version (2 bits)
    rtp_header |= (0 << 29)           # Padding (1 bit)
    rtp_header |= (0 << 28)           # Extension (1 bit)
    rtp_header |= (0 << 27)           # CSRC count (4 bits)
    rtp_header |= (PAYLOAD_TYPE << 16)  # Payload type (7 bits)
    rtp_header |= sequence_number     # Sequence number (16 bits)

    # Pack the header into bytes
    header_bytes = struct.pack('!BBHII', (rtp_header >> 24) & 0xFF, (rtp_header >> 16) & 0xFF,
                               sequence_number, timestamp, SSRC)
    return header_bytes

def send_rtp_stream(audio_file, ip, port, frame_duration=20):
    """
    Read audio frames from a file and send them as RTP packets.
    
    Args:
        audio_file (str): Path to the audio file (.wav).
        ip (str): Destination IP address.
        port (int): Destination port.
        frame_duration (int): Duration of each audio frame in milliseconds.
    """
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sequence_number = 0
    timestamp = 0

    print(f"Streaming audio to {ip}:{port}...")
    for encoded_audio in read_and_encode_audio(audio_file, frame_duration):
        # Create RTP header
        rtp_header = create_rtp_header(sequence_number, timestamp)

        # Combine header and payload
        rtp_packet = rtp_header + encoded_audio

        # Send RTP packet
        sock.sendto(rtp_packet, (ip, port))

        # Update sequence number and timestamp
        sequence_number += 1
        timestamp += frame_duration * 8  # Assuming 8 kHz sample rate

        # Simulate real-time streaming
        time.sleep(frame_duration / 1000)

    print("Streaming complete.")
    sock.close()

def receive_rtp_stream(port, rtcp_port, output_file="audio.wav"):
    """
    Receive RTP packets, reconstruct the audio stream, and send RTCP reports.
    
    Args:
        port (int): Port to listen for RTP packets.
        rtcp_port (int): Port to send RTCP reports.
        output_file (str): Path to save the reconstructed audio stream.
    """
    print(f"Listening for RTP packets on port {port}...")

    # Use the jitter buffer for smoother playback
    receive_with_jitter_buffer(port)

def create_rtcp_report(ssrc, fraction_lost, cumulative_lost, highest_seq, jitter):
    """
    Create an RTCP Receiver Report (RR).
    
    Args:
        ssrc (int): SSRC of the RTP stream.
        fraction_lost (float): Fraction of packets lost.
        cumulative_lost (int): Total number of packets lost.
        highest_seq (int): Highest sequence number received.
        jitter (int): Estimated jitter.
    
    Returns:
        bytes: RTCP Receiver Report packet.
    """
    rtcp_header = struct.pack('!BBH', 0x80, 201, 7)  # Version 2, RR, length
    ssrc_bytes = struct.pack('!I', ssrc)
    report_block = struct.pack('!IBBHII', ssrc, int(fraction_lost * 256), cumulative_lost,
                               highest_seq, jitter, 0)
    return rtcp_header + ssrc_bytes + report_block

