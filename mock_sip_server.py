import socket
from config import *
import traceback

def start_mock_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((LOCAL_IP, SIP_PORT))
    print(f"[Server] Listening on {LOCAL_IP}:{SIP_PORT}")

    while True:
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            message = data.decode()
            print(f"\n[Server] Received from {addr}:\n{message}")

            if message.startswith("INVITE"):
                call_id = extract_call_id(message)
                to = extract_field(message, "To")
                from_ = extract_field(message, "From")

                response = f"SIP/2.0 200 OK\r\n" \
                           f"Via: SIP/2.0/UDP {LOCAL_IP}:{SIP_PORT};branch=z9hG4bK{call_id}\r\n" \
                           f"From: {from_};tag={call_id}\r\n" \
                           f"To: {to};tag={call_id}\r\n" \
                           f"Call-ID: {call_id}\r\n" \
                           f"CSeq: 1 INVITE\r\n" \
                           f"Content-Length: 0\r\n\r\n"

                sock.sendto(response.encode(), addr)
                print("[Server] Sent 200 OK")

            elif message.startswith("ACK"):
                print("[Server] Received ACK. Call established.")

            elif message.startswith("BYE"):
                print("[Server] Received BYE. Call ended.")
                goodbye = f"SIP/2.0 200 OK\r\nCall-ID: {extract_call_id(message)}\r\nContent-Length: 0\r\n\r\n"
                sock.sendto(goodbye.encode(), addr)

        except ConnectionResetError:
            print("[Server] Connection reset by client. Waiting for next message...")
        except Exception as e:
            print(f"[Server] Unexpected error: {e}")

def extract_call_id(msg):
    for line in msg.splitlines():
        if line.startswith("Call-ID"):
            return line.split(" ")[1].strip()
    return "test123"

def extract_field(msg, field_name):
    for line in msg.splitlines():
        if line.startswith(field_name):
            return line.split(":", 1)[1].strip()
    return ""

if __name__ == "__main__":
    start_mock_server()