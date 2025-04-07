LOCAL_IP = "127.0.0.1"  # or your LAN IP
SIP_PORT = 5060         # default or any valid SIP ports
RTP_PORT = 5004        # default or any valid RTP ports // ANY EVEN NUMBER PORTS
RTP_VERSION = 2
PAYLOAD_TYPE = 0  # PCMU
SSRC = 12345 # Synchronization source identifier
AUDIO_CODEC = "PCMU"  # G.711 codec
BUFFER_SIZE = 1024  # Buffer size for SIP