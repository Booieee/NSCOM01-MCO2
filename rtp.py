import struct
import wave
from pydub import AudioSegment
import pyaudio 

def build_rtp_packet(payload, sequence_number=0, timestamp=0, ssrc=1234):
    header = struct.pack("!BBHII", 0x80, 0x00, sequence_number, timestamp, ssrc)
    return header + payload

# delete if the new parser works
def parse_rtp_packet_before(packet):
    header = packet[:12]
    payload = packet[12:]
    return payload

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

def read_audio_frames_before(file_path, frame_size=320):
    """
    Reads audio frames from a WAV file.

    Args:
        file_path (str): Path to the audio file.
        frame_size (int): Number of bytes per frame (default is 320 for 20ms at 8kHz).

    Yields:
        bytes: A single audio frame.
    """
    with wave.open(file_path, 'rb') as wav_file:
        # Ensure the WAV file is in the correct format
        if wav_file.getnchannels() != 1:
            raise ValueError("Only mono audio is supported.")
        if wav_file.getsampwidth() != 2:
            raise ValueError("Only 16-bit audio is supported.")
        if wav_file.getframerate() != 8000:
            raise ValueError("Only 8kHz audio is supported.")

        while True:
            frame = wav_file.readframes(frame_size // 2)  # Divide by 2 because 16-bit audio = 2 bytes per sample
            if not frame:
                break
            yield frame

def read_audio_frames(file_path, frame_size=320):
    """
    Reads audio frames from a file (supports WAV and other formats).

    Args:
        file_path (str): Path to the audio file.
        frame_size (int): Number of bytes per frame (default is 320 for 20ms at 8kHz).

    Yields:
        bytes: A single audio frame.
    """
    if file_path.endswith('.wav'):
        # Handle WAV files
        with wave.open(file_path, 'rb') as wav_file:
            if wav_file.getnchannels() != 1 or wav_file.getsampwidth() != 2 or wav_file.getframerate() != 8000:
                raise ValueError("Unsupported WAV format. Expected 8 kHz, mono, 16-bit PCM.")
            while True:
                frame = wav_file.readframes(frame_size // 2)  # Divide by 2 because 16-bit audio = 2 bytes per sample
                if not frame:
                    break
                yield frame
    else:
        # Handle other formats (e.g., MP3, AAC)
        audio = AudioSegment.from_file(file_path)
        audio = audio.set_frame_rate(8000).set_channels(1).set_sample_width(2)  # Convert to 8kHz, mono, 16-bit PCM
        raw_data = audio.raw_data
        for i in range(0, len(raw_data), frame_size):
            yield raw_data[i:i + frame_size]