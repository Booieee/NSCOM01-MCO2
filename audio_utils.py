import wave
from pydub import AudioSegment
import pyaudio

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

def play_audio_stream(sample_rate=8000, channels=1, bit_depth=16):
    """
    Initializes an audio playback stream.

    Args:
        sample_rate (int): Sample rate of the audio (e.g., 8000 Hz).
        channels (int): Number of audio channels (e.g., 1 for mono).
        bit_depth (int): Bit depth of the audio (e.g., 16-bit).

    Returns:
        stream: An audio playback stream.
    """
    import pyaudio
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=pyaudio.paInt16 if bit_depth == 16 else pyaudio.paInt8,
        channels=channels,
        rate=sample_rate,
        output=True
    )
    return stream