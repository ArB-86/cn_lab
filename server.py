"""
TCP Multi-Client Chat Server
Project: Computer Networks - Socket Programming
Course: 18B11CS311 - Computer Networks & IoT

THEORY (from Kurose & Forouzan):
- Uses TCP (Transport Layer) for reliable, connection-oriented communication
- TCP 3-Way Handshake: SYN → SYN-ACK → ACK establishes each client connection
- Port 12345 is the well-known port where server listens
- Each client gets its own thread (concurrent connections)
- Demonstrates: Client-Server model, Sockets, TCP, Multiplexing
"""

import socket
import threading

# ─────────────────────────────────────────────
#  SERVER CONFIGURATION
# ─────────────────────────────────────────────
HOST = '127.0.0.1'   # localhost (loopback IP)
PORT = 12345         # server listens on this port

# Store all connected clients: { socket: username }
clients = {}
lock = threading.Lock()  # thread-safe access to clients dict


def broadcast(message, sender_socket=None):
    """Send a message to ALL connected clients except the sender."""
    with lock:
        for client_socket in list(clients.keys()):
            if client_socket != sender_socket:
                try:
                    client_socket.send(message.encode('utf-8'))
                except Exception:
                    client_socket.close()
                    del clients[client_socket]


def handle_client(client_socket, address):
    """
    Handle communication with a single connected client.
    Each client runs in its own thread.
    """
    print(f"[NEW CONNECTION] {address} connected.")

    # Ask client for their username
    client_socket.send("Enter your username: ".encode('utf-8'))
    username = client_socket.recv(1024).decode('utf-8').strip()

    with lock:
        clients[client_socket] = username

    join_msg = f"[SERVER] {username} has joined the chat!"
    print(join_msg)
    broadcast(join_msg, sender_socket=client_socket)
    client_socket.send(f"[SERVER] Welcome {username}! You are connected.\n".encode('utf-8'))

    # Main loop: receive and broadcast messages
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            if message.lower() == '/quit':
                break
            full_msg = f"[{username}]: {message}"
            print(full_msg)
            broadcast(full_msg, sender_socket=client_socket)
        except Exception as e:
            print(f"[ERROR] {e}")
            break

    # Client disconnected
    with lock:
        if client_socket in clients:
            del clients[client_socket]
    client_socket.close()
    leave_msg = f"[SERVER] {username} has left the chat."
    print(leave_msg)
    broadcast(leave_msg)


def start_server():
    """Start the TCP server and listen for incoming connections."""
    # AF_INET = IPv4, SOCK_STREAM = TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # SO_REUSEADDR allows reuse of port immediately after restart
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((HOST, PORT))   # Bind to IP and port
    server_socket.listen(5)            # Queue up to 5 pending connections

    print("=" * 50)
    print(f"  TCP CHAT SERVER STARTED")
    print(f"  Listening on {HOST}:{PORT}")
    print(f"  Waiting for clients to connect...")
    print("=" * 50)

    try:
        while True:
            # TCP 3-Way Handshake happens here (accept() completes it)
            client_socket, address = server_socket.accept()

            # Spawn a new thread for each client
            thread = threading.Thread(target=handle_client, args=(client_socket, address))
            thread.daemon = True
            thread.start()

            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down...")
    finally:
        server_socket.close()


if __name__ == "__main__":
    start_server()
