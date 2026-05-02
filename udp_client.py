"""
UDP Ping Client with RTT Statistics
Project: Computer Networks - Socket Programming
Course: 18B11CS311 - Computer Networks & IoT

THEORY:
- Sends 10 ping messages over UDP
- Measures Round Trip Time (RTT) for each packet
- RTT = time for packet to go from sender → receiver → back
- Shows: min RTT, max RTT, avg RTT, packet loss %
- Demonstrates: UDP unreliability, RTT measurement (taught in Kurose Ch. 2-3)
"""

import socket
import time

HOST = '127.0.0.1'
PORT = 12000
TIMEOUT = 1.0    # Wait 1 second max for reply (then = packet lost)
NUM_PINGS = 10   # Send 10 pings (standard like real ping command)

def run_ping_client():
    """Send 10 UDP pings and display RTT statistics."""
    # SOCK_DGRAM = UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(TIMEOUT)  # Non-blocking with timeout

    print("=" * 55)
    print(f"  UDP PING to {HOST}:{PORT}")
    print(f"  Sending {NUM_PINGS} pings | Timeout = {TIMEOUT}s")
    print("=" * 55)

    rtts = []
    lost = 0

    for seq_num in range(1, NUM_PINGS + 1):
        message = f"PING {seq_num} {time.time()}"
        send_time = time.time()

        try:
            # Send UDP packet (no connection needed - just send)
            client_socket.sendto(message.encode(), (HOST, PORT))

            # Wait for echo reply
            reply, _ = client_socket.recvfrom(1024)
            recv_time = time.time()

            rtt = (recv_time - send_time) * 1000  # convert to milliseconds
            rtts.append(rtt)
            print(f"  Reply from {HOST}: seq={seq_num}  RTT = {rtt:.2f} ms")

        except socket.timeout:
            lost += 1
            print(f"  Request timeout for seq={seq_num}  (PACKET LOST)")

        time.sleep(0.5)  # Small delay between pings

    # ─── STATISTICS ───────────────────────────────────
    print("=" * 55)
    print(f"  PING STATISTICS for {HOST}")
    print(f"  Packets Sent: {NUM_PINGS} | Received: {len(rtts)} | Lost: {lost}")
    loss_pct = (lost / NUM_PINGS) * 100
    print(f"  Packet Loss: {loss_pct:.0f}%")

    if rtts:
        print(f"  Min RTT : {min(rtts):.2f} ms")
        print(f"  Max RTT : {max(rtts):.2f} ms")
        print(f"  Avg RTT : {sum(rtts)/len(rtts):.2f} ms")
    print("=" * 55)

    client_socket.close()

if __name__ == "__main__":
    run_ping_client()
