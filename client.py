

import socket
import threading
import sys


HOST = '127.0.0.1'
PORT = 12345


def receive_messages(client_socket):

    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                print("\n[DISCONNECTED] Server closed the connection.")
                break
            print(f"\r{message}\n> ", end='', flush=True)
        except Exception:
            print("\n[ERROR] Lost connection to server.")
            break


def start_client():
    """Connect to the TCP server and start chatting."""
   
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
       
        client_socket.connect((HOST, PORT))
        print("=" * 50)
        print(f"  CONNECTED TO CHAT SERVER at {HOST}:{PORT}")
        print(f"  Type your message and press Enter to send")
        print(f"  Type '/quit' to exit")
        print("=" * 50)

        
        recv_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        recv_thread.daemon = True
        recv_thread.start()

      
        while True:
            try:
                message = input("> ")
                if not message.strip():
                    continue
                client_socket.send(message.encode('utf-8'))
                if message.lower() == '/quit':
                    print("[CLIENT] Disconnecting...")
                    break
            except (KeyboardInterrupt, EOFError):
                break

    except ConnectionRefusedError:
        print(f"[ERROR] Could not connect to {HOST}:{PORT}")
        print("[ERROR] Make sure server.py is running first!")
        sys.exit(1)
    finally:
        client_socket.close()


if __name__ == "__main__":
    start_client()
