

import socket
import threading


HOST = '127.0.0.1'  
PORT = 12345         


clients = {}
lock = threading.Lock()  


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

    
    client_socket.send("Enter your username: ".encode('utf-8'))
    username = client_socket.recv(1024).decode('utf-8').strip()

    with lock:
        clients[client_socket] = username

    join_msg = f"[SERVER] {username} has joined the chat!"
    print(join_msg)
    broadcast(join_msg, sender_socket=client_socket)
    client_socket.send(f"[SERVER] Welcome {username}! You are connected.\n".encode('utf-8'))

    
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

    
    with lock:
        if client_socket in clients:
            del clients[client_socket]
    client_socket.close()
    leave_msg = f"[SERVER] {username} has left the chat."
    print(leave_msg)
    broadcast(leave_msg)


def start_server():
    """Start the TCP server and listen for incoming connections."""
   
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    
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
            
            client_socket, address = server_socket.accept()

           
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
