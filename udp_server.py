"""
UDP Ping Server
Project: Computer Networks - Socket Programming
Course: 18B11CS311 - Computer Networks & IoT

THEORY (from Kurose & Forouzan):
- UDP = User Datagram Protocol (Transport Layer)
- CONNECTIONLESS: no handshake, no guarantee of delivery
- Small header (8 bytes vs TCP's 20 bytes)
- Used where speed > reliability (DNS, video streaming, gaming)
- This server simulates 30% packet loss (as taught in class)
- Demonstrates: UDP sockets, RTT measurement, packet loss
"""

import socket
import random
import time

HOST = '127.0.0.1'
PORT = 12000   # UDP server port (different from TCP server)

def start_udp_server():
    """Start UDP ping server. Echoes packets back, simulates 30% loss."""
    # AF_INET = IPv4, SOCK_DGRAM = UDP (no connection, no stream)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((HOST, PORT))

    print("=" * 50)
    print(f"  UDP PING SERVER STARTED")
    print(f"  Listening on {HOST}:{PORT}")
    print(f"  Simulating 30% packet loss")
    print("=" * 50)

    while True:
        try:
            # recvfrom returns data AND client address (UDP has no connection)
            message, client_address = server_socket.recvfrom(1024)

            # SIMULATE 30% PACKET LOSS (as taught in Kurose book)
            if random.random() < 0.3:
                print(f"[PACKET LOST] Dropped packet from {client_address}")
                continue  # Don't reply = simulate loss

            # Echo the message back
            server_socket.sendto(message, client_address)
            print(f"[PING RECEIVED] from {client_address} → replied")

        except KeyboardInterrupt:
            print("\n[SERVER] Shutting down...")
            break

    server_socket.close()

if __name__ == "__main__":
    start_udp_server()
