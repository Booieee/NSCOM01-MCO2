'''
A helper functions for networking

Task to do: DONE
1. Implement helper functions:
    - send_udp_packet(ip, port, data): Sends data over UDP to the specified IP and port.
    - receive_udp_packet(socket, buffer_size): Receives data from a UDP socket with the specified buffer size.
    - create_udp_socket(port): Creates a UDP socket bound to the specified port.
'''

import socket
from config import *

def send_udp_packet(ip, port, data):
    """
    Sends data over UDP to the specified IP and port.
    
    Args:
        ip (str): The destination IP address.
        port (int): The destination port number.
        data (bytes): The data to be sent.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            if isinstance(data, str):
                data = data.encode('utf-8')
            sock.sendto(data, (ip, port))
            print(f"Sent {len(data)} bytes to {ip}:{port}")
    except Exception as e:
        print(f"Error sending UDP packet: {e}")

def receive_udp_packet(sock, buffer_size = BUFFER_SIZE, timeout = None):
    """
    Receives data from a UDP socket with the specified buffer size. 
    Ensure it can handle multiple incoming messages correctly.

    Args:
        sock (socket.socket): The UDP socket to receive data from.
        buffer_size (int): The size of the buffer for receiving data.
        timeout (float): The timeout for the socket in seconds. If None, no timeout is set.
    
    Returns:
        tuple: The address of the sender and the received data.
    """
    try:
        if timeout:
            sock.settimeout(timeout)
        data, addr = sock.recvfrom(buffer_size)
        print(f"Received {len(data)} bytes from {addr}")
        return addr, data
    except socket.timeout:
        print("Socket timed out waiting for data")
        return None
    except Exception as e:
        print(f"Error receiving UDP packet: {e}")
        return None

def create_udp_socket(port):
    """
    Creates a UDP socket bound to the specified port.
    
    Args:
        port (int): The port number to bind the socket to.
    
    Returns:
        socket.socket: The created UDP socket.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', port))
        print(f"Socket created and bound to port {port}")
        return sock
    except Exception as e:
        print(f"Error creating UDP socket: {e}")
        return None