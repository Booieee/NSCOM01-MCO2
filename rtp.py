import struct
import wave
from pydub import AudioSegment
import pyaudio 

def build_rtp_packet(payload, sequence_number=0, timestamp=0, ssrc=1234):
    header = struct.pack("!BBHII", 0x80, 0x00, sequence_number, timestamp, ssrc)
    return header + payload

def parse_rtp_packet(packet):
    """
    Parses an RTP packet and extracts the header fields and payload.

    Args:
        packet (bytes): The RTP packet.

    Returns:
        dict: A dictionary containing the RTP header fields.
        bytes: The payload of the RTP packet.
    """
    if len(packet) < 12:
        raise ValueError("Invalid RTP packet: too short to contain a valid header.")

    # Unpack the RTP header (12 bytes)
    header = struct.unpack("!BBHII", packet[:12])
    version = (header[0] >> 6) & 0x03  # First 2 bits
    padding = (header[0] >> 5) & 0x01  # Next 1 bit
    extension = (header[0] >> 4) & 0x01  # Next 1 bit
    csrc_count = header[0] & 0x0F  # Last 4 bits
    marker = (header[1] >> 7) & 0x01  # First bit of second byte
    payload_type = header[1] & 0x7F  # Last 7 bits of second byte
    sequence_number = header[2]
    timestamp = header[3]
    ssrc = header[4]

    # Extract the payload
    payload = packet[12:]

    # Return the parsed header fields and payload
    return {
        "version": version,
        "padding": padding,
        "extension": extension,
        "csrc_count": csrc_count,
        "marker": marker,
        "payload_type": payload_type,
        "sequence_number": sequence_number,
        "timestamp": timestamp,
        "ssrc": ssrc,
    }, payload

def read_audio_frames(file_path, frame_size=520):
    """
    Reads audio frames from a file (supports WAV and other formats).

    Args:
        file_path (str): Path to the audio file.
        frame_size (int): Number of bytes per frame (default is 320 for 20ms at 8kHz).

    Yields:
        bytes: A single audio frame.
    """
    try:
        print(f"Converting '{file_path}' to 8kHz mono 16-bit PCM using pydub...")
        audio = AudioSegment.from_file(file_path)
        audio = audio.set_frame_rate(8000).set_channels(1).set_sample_width(2)
        raw_data = audio.raw_data

        for i in range(0, len(raw_data), frame_size):
            yield raw_data[i:i + frame_size]

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        raise