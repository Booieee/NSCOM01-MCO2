import threading
from sip_client import sip_client
from rtp_stream import receive_rtp_stream
import logging

logging.basicConfig(level=logging.DEBUG)

def client_1():
    logging.debug("Client 1: Initiating call...")
    sip_client(to="127.0.0.1", from_="client1", call_id=None)

def client_2():
    logging.debug("Client 2: Listening for incoming calls...")
    receive_rtp_stream(port=5010, rtcp_port=5011)

if __name__ == "__main__":
    # Start Client 2 in a separate thread to listen for incoming calls
    threading.Thread(target=client_2, daemon=True).start()

    # Start Client 1 to initiate the call
    client_1()