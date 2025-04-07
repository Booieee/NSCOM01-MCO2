import socket
from sip import build_ok, build_ack
from rtp import parse_rtp_packet
from audio_utils import play_audio_stream

from sip import build_ok, build_ack_bye, generate_sdp_body

sip_port = 5060
rtp_port = 4000

# SIP receive
sip_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sip_sock.bind(('', sip_port))

data, addr = sip_sock.recvfrom(1024)
print("Received:", data.decode())
sip_sock.sendto(build_ok().encode(), addr)

data, _ = sip_sock.recvfrom(1024)
print("ACK:", data.decode())

# RTP receive
rtp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
rtp_sock.bind(('', rtp_port))

stream = play_audio_stream()

frame_count = 0
while True:
    try:
        data, _ = rtp_sock.recvfrom(2048)
        frame = parse_rtp_packet(data)
        stream.write(frame)

        print(f"Received frame #{frame_count}, Size: {len(frame)} bytes")
        frame_count += 1

    except KeyboardInterrupt:
        break

