"""
Simple HTTP Web Server (Socket-based)
Project: Computer Networks - Socket Programming
Course: 18B11CS311 - Computer Networks & IoT

THEORY (from Kurose Ch. 2 - Application Layer):
- HTTP = HyperText Transfer Protocol (Application Layer)
- HTTP runs over TCP (port 80 by default, here port 8080)
- Client sends HTTP GET request, server responds with HTTP response
- Demonstrates: HTTP request/response, status codes (200 OK, 404 Not Found)
- This is exactly what the lab manual's "Socket Programming Web Server: TCP" asks for!
"""

import socket
import os

HOST = '127.0.0.1'
PORT = 8080       # HTTP usually port 80, using 8080 to avoid root permissions

def create_sample_html():
    """Create a sample HTML file for the server to serve."""
    html = """<!DOCTYPE html>
<html>
<head><title>CN Project - HTTP Server</title></head>
<body>
  <h1>Computer Networks Project</h1>
  <h2>Socket-Based HTTP Web Server</h2>
  <p>This page is served by our custom Python HTTP server built using sockets.</p>
  <p><strong>Course:</strong> 18B11CS311 - Computer Networks & IoT</p>
  <ul>
    <li>Protocol: HTTP/1.0 over TCP</li>
    <li>Port: 8080</li>
    <li>Status: 200 OK</li>
  </ul>
</body>
</html>"""
    with open("index.html", "w") as f:
        f.write(html)
    print("[SERVER] Created index.html")

def handle_http_request(client_socket):
    """Parse HTTP GET request and send appropriate HTTP response."""
    try:
        request = client_socket.recv(4096).decode('utf-8')
        if not request:
            return

        # Parse the first line: e.g., "GET /index.html HTTP/1.1"
        first_line = request.split('\n')[0]
        parts = first_line.split()

        if len(parts) < 2:
            return

        method = parts[0]    # GET, POST, etc.
        path = parts[1]      # /index.html

        # Default to index.html
        if path == '/':
            path = '/index.html'

        filename = path.lstrip('/')

        print(f"[REQUEST] {method} {path}")

        # Try to open the requested file
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                content = f.read()

            # HTTP 200 OK Response
            response = (
                "HTTP/1.0 200 OK\r\n"
                "Content-Type: text/html\r\n"
                f"Content-Length: {len(content)}\r\n"
                "Connection: close\r\n"
                "\r\n"
            ).encode('utf-8') + content

            print(f"[RESPONSE] 200 OK → {filename}")

        else:
            # HTTP 404 Not Found Response
            body = b"<html><body><h1>404 Not Found</h1><p>The requested file does not exist.</p></body></html>"
            response = (
                "HTTP/1.0 404 Not Found\r\n"
                "Content-Type: text/html\r\n"
                f"Content-Length: {len(body)}\r\n"
                "Connection: close\r\n"
                "\r\n"
            ).encode('utf-8') + body

            print(f"[RESPONSE] 404 Not Found → {filename}")

        client_socket.send(response)

    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        client_socket.close()


def start_http_server():
    """Start the HTTP server."""
    create_sample_html()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    print("=" * 55)
    print(f"  HTTP WEB SERVER STARTED")
    print(f"  Open browser: http://{HOST}:{PORT}/index.html")
    print(f"  Or test 404:  http://{HOST}:{PORT}/missing.html")
    print("=" * 55)

    try:
        while True:
            client_socket, address = server_socket.accept()
            print(f"[CONNECTION] Browser connected from {address}")
            handle_http_request(client_socket)
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down...")
    finally:
        server_socket.close()


if __name__ == "__main__":
    start_http_server()
