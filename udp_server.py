

import socket
import random
import time

HOST = '127.0.0.1'
PORT = 12000   

def start_udp_server():
    """Start UDP ping server. Echoes packets back, simulates 30% loss."""
   
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((HOST, PORT))

    print("=" * 50)
    print(f"  UDP PING SERVER STARTED")
    print(f"  Listening on {HOST}:{PORT}")
    print(f"  Simulating 30% packet loss")
    print("=" * 50)

    while True:
        try:
            
            message, client_address = server_socket.recvfrom(1024)

            
            if random.random() < 0.3:
                print(f"[PACKET LOST] Dropped packet from {client_address}")
                continue  # Don't reply = simulate loss

           
            server_socket.sendto(message, client_address)
            print(f"[PING RECEIVED] from {client_address} → replied")

        except KeyboardInterrupt:
            print("\n[SERVER] Shutting down...")
            break

    server_socket.close()

if __name__ == "__main__":
    start_udp_server()
