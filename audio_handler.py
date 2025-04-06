'''
Implementation of Audio Handling

Task To Do:
1. Client 1: Read and encode .wav (or G.711) audio files for RTP transmission.
2. Client 2: Receive RTP packets and decode them to play audio in real-time.
3. Ensure proper buffering and latency management.
'''
import socket
import pyaudio
import wave
import queue
import threading
import numpy as np

def read_and_encode_audio(audio_file, frame_duration=20):
    """
    Read and encode .wav audio files for RTP transmission using G.711.

    Args:
        audio_file (str): Path to the .wav file.
        frame_duration (int): Duration of each audio frame in milliseconds.

    Yields:
        bytes: Encoded audio frames.
    """
    with wave.open(audio_file, 'rb') as wf:
        # Get audio properties
        sample_rate = wf.getframerate()
        channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        frame_size = int(sample_rate * frame_duration / 1000) * channels * sample_width

        while True:
            # Read a frame of audio data
            audio_data = wf.readframes(frame_size)
            if not audio_data:
                break

            # Convert raw PCM data to numpy array
            pcm_samples = np.frombuffer(audio_data, dtype=np.int16)

            # Encode audio data using G.711 μ-law
            encoded_audio = linear_to_ulaw(pcm_samples)

            yield encoded_audio.tobytes()

# Constants for μ-law
MU = 255

def linear_to_ulaw(sample):
    """
    Convert a linear PCM sample to μ-law.
    """
    sign = np.sign(sample)
    magnitude = np.log1p(MU * np.abs(sample) / 32768.0) / np.log1p(MU)
    ulaw_sample = ((1 + MU) * magnitude).astype(np.int16) - 128
    return (sign * ulaw_sample).astype(np.uint8)

def ulaw_to_linear(ulaw_sample):
    """
    Convert a μ-law sample to linear PCM.
    """
    ulaw_sample = ulaw_sample.astype(np.int16) + 128
    magnitude = (np.expm1(ulaw_sample / (1 + MU)) * 32768.0).astype(np.int16)
    return magnitude

def receive_and_play_audio(port, buffer_size=2048):
    """
    Receive RTP packets and decode them to play audio in real-time using G.711.

    Args:
        port (int): Port to listen for RTP packets.
        buffer_size (int): Size of the buffer for receiving packets.
    """
    # Set up UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', port))

    # Set up PyAudio for playback
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16,  # 16-bit audio
                        channels=1,             # Mono
                        rate=8000,              # 8 kHz sample rate
                        output=True)

    print(f"Listening for RTP packets on port {port}...")

    while True:
        data, addr = sock.recvfrom(buffer_size)
        if data:
            # Extract RTP payload (audio data)
            payload = data[12:]  # RTP header is 12 bytes

            # Decode audio data using G.711 μ-law
            decoded_audio = ulaw_to_linear(np.frombuffer(payload, dtype=np.uint8))

            # Play the decoded audio
            stream.write(decoded_audio.tobytes())

    # Cleanup
    stream.stop_stream()
    stream.close()
    audio.terminate()

class JitterBuffer:
    def __init__(self, max_size=50):
        self.buffer = queue.Queue(maxsize=max_size)

    def add_packet(self, packet):
        """
        Add a packet to the jitter buffer.
        """
        if not self.buffer.full():
            self.buffer.put(packet)

    def get_packet(self):
        """
        Retrieve a packet from the jitter buffer.
        """
        if not self.buffer.empty():
            return self.buffer.get()
        return None

def receive_with_jitter_buffer(port, buffer_size=2048):
    """
    Receive RTP packets with jitter buffering and play audio in real-time using G.711.

    Args:
        port (int): Port to listen for RTP packets.
        buffer_size (int): Size of the buffer for receiving packets.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', port))

    jitter_buffer = JitterBuffer()

    def receive_packets():
        while True:
            data, addr = sock.recvfrom(buffer_size)
            if data:
                jitter_buffer.add_packet(data)

    # Start a thread to receive packets
    threading.Thread(target=receive_packets, daemon=True).start()

    # Set up PyAudio for playback
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16,  # 16-bit audio
                        channels=1,             # Mono
                        rate=8000,              # 8 kHz sample rate
                        output=True)

    while True:
        packet = jitter_buffer.get_packet()
        if packet:
            payload = packet[12:]  # RTP header is 12 bytes

            # Decode audio data using G.711 μ-law
            decoded_audio = ulaw_to_linear(np.frombuffer(payload, dtype=np.uint8))

            # Play the decoded audio
            stream.write(decoded_audio.tobytes())

    # Cleanup
    stream.stop_stream()
    stream.close()
    audio.terminate()