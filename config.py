'''
define constants for SIP and RTP settings
'''

SIP_PORT = 5060
RTP_PORT = 5004
RTP_VERSION = 2
PAYLOAD_TYPE = 0  # PCMU
SSRC = 12345 # Synchronization source identifier
LOCAL_IP = "127.0.0.1"
AUDIO_CODEC = "PCMU"  # G.711 codec
BUFFER_SIZE = 1024  # Buffer size for SIP