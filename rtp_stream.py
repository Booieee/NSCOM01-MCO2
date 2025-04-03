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