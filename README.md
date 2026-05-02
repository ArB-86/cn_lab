# Computer Networks Socket Programming Project

This repository contains several Python socket programming examples for a Computer Networks course (18B11CS311 - Computer Networks & IoT). The project demonstrates key networking concepts using TCP and UDP sockets, including a multi-client chat server, an HTTP web server, and a UDP ping client/server pair.

## Repository Contents

- `server.py` - TCP multi-client chat server
- `client.py` - TCP chat client for connecting to `server.py`
- `http_server.py` - Simple HTTP server that serves `index.html`
- `index.html` - Sample HTML page served by `http_server.py`
- `udp_server.py` - UDP ping server with simulated packet loss
- `udp_client.py` - UDP ping client that measures RTT and packet loss

## Requirements

- Python 3.x
- No external libraries required; uses only Python standard library modules (`socket`, `threading`, `os`, `time`, `random`, `sys`)

## Usage

### TCP Chat Server

1. Start the server:
   ```bash
   python server.py
   ```
2. Start one or more clients in separate terminals:
   ```bash
   python client.py
   ```
3. Enter a username when prompted and chat with connected clients.
4. Type `/quit` to disconnect a client.

### HTTP Server

1. Start the HTTP server:
   ```bash
   python http_server.py
   ```
2. Open a browser and navigate to:
   ```text
   http://127.0.0.1:8080/index.html
   ```
3. The server will serve `index.html` and return a 404 page for missing files.

### UDP Ping Client / Server

1. Start the UDP server:
   ```bash
   python udp_server.py
   ```
2. In a separate terminal, run the UDP client:
   ```bash
   python udp_client.py
   ```
3. The client sends 10 UDP ping messages and prints RTT statistics.

## Notes

- The TCP chat example uses `127.0.0.1:12345` by default.
- The HTTP server uses `127.0.0.1:8080` and creates `index.html` if it is missing.
- The UDP ping server listens on `127.0.0.1:12000` and simulates ~30% packet loss.

## Learning Objectives

- TCP socket programming with concurrent client handling
- HTTP request parsing and response generation over raw sockets
- UDP socket programming, packet loss simulation, and RTT measurement

## License

This project is provided for educational purposes.
