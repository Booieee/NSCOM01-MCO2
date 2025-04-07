import wave
import pyaudio

def read_audio_frames(filename):
    wf = wave.open(filename, 'rb')
    while True:
        data = wf.readframes(160)  # 20ms at 8kHz mono 16-bit
        if not data:
            break
        yield data
    wf.close()

# delete after testing
def play_audio_stream_before():
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16, channels=1, rate=8000, output=True)
    return stream

def play_audio_stream_2(sample_rate=8000, channels=1, bit_depth=16):
    import pyaudio
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=pyaudio.paInt16 if bit_depth == 16 else pyaudio.paInt8,
        channels=channels,
        rate=sample_rate,
        output=True
    )
    return stream

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