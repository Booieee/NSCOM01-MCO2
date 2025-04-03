'''
Implementation of Audio Handling

Task To Do:
1. Client 1: Read and encode .wav (or G.711) audio files for RTP transmission.
2. Client 2: Receive RTP packets and decode them to play audio in real-time.
3. Ensure proper buffering and latency management.
'''

import pyaudio
import wave