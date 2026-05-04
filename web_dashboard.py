import socket
import threading
import time
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from collections import deque

# --- CONFIGURATION[cite: 5, 7] ---
WEB_PORT = 8080
TCP_HOST, TCP_PORT = '127.0.0.1', 12345
UDP_HOST, UDP_PORT = '127.0.0.1', 12000

# Shared message store for the web UI
messages = deque(maxlen=50)
msg_lock = threading.Lock()

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode())
        elif self.path == '/api/messages':
            with msg_lock:
                self.send_json(list(messages))

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length).decode()) if length > 0 else {}
        
        if self.path == '/api/send':
            # Har message ke liye selected user se connection banta hai[cite: 2, 5]
            self.send_to_tcp(body['user'], body['msg'])
            self.send_response(200)
            self.end_headers()
        elif self.path == '/api/ping':
            results = self.run_udp_ping()
            self.send_json(results)

    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def send_to_tcp(self, username, msg):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((TCP_HOST, TCP_PORT))
            s.recv(1024) # Handshake: Server asks for name
            s.send(username.encode())
            s.recv(1024) # Welcome message from server
            s.send(msg.encode())
            s.close()
        except Exception as e:
            print(f"TCP Send Error: {e}")

    def run_udp_ping(self):
        rtts = []
        for i in range(5):
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.8)
            t0 = time.time()
            try:
                # UDP Ping simulation with RTT measurement[cite: 6, 7]
                s.sendto(f"PING {i}".encode(), (UDP_HOST, UDP_PORT))
                s.recvfrom(1024)
                rtts.append(round((time.time()-t0)*1000, 2))
            except: 
                rtts.append(None)
            s.close()
        return rtts

# Global listener thread to sync the dashboard with server broadcasts[cite: 5]
def global_listener():
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((TCP_HOST, TCP_PORT))
            sock.recv(1024)
            sock.send("Arya_Dev_Monitor".encode())
            sock.recv(1024)
            while True:
                data = sock.recv(1024).decode()
                if not data: break
                with msg_lock:
                    messages.append(data)
        except: 
            time.sleep(2)

threading.Thread(target=global_listener, daemon=True).start()

# --- ARYA'S MULTI-CLIENT UI ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CN Socket Hub | Arya</title>
    <style>
        body { background: #0f172a; color: #f8fafc; font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 1000px; margin: auto; display: grid; grid-template-columns: 1.6fr 1fr; gap: 20px; }
        .card { background: #1e293b; border-radius: 12px; padding: 25px; border: 1px solid #334155; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); }
        h2 { color: #3b82f6; margin-top: 0; font-size: 1.4rem; border-bottom: 1px solid #334155; padding-bottom: 10px; }
        
        /* Chat Styling */
        #chatBox { height: 320px; overflow-y: auto; background: #020617; padding: 15px; border-radius: 8px; margin-bottom: 15px; font-family: 'Courier New', monospace; border: 1px solid #1e293b; }
        .msg-line { margin-bottom: 5px; color: #94a3b8; border-bottom: 1px solid #0f172a; padding-bottom: 2px; }
        
        /* User Selection */
        .controls { display: flex; flex-direction: column; gap: 10px; }
        .user-toggle { display: flex; gap: 10px; margin-bottom: 10px; background: #0f172a; padding: 10px; border-radius: 8px; }
        .user-btn { flex: 1; padding: 8px; border: 1px solid #3b82f6; background: transparent; color: #3b82f6; cursor: pointer; border-radius: 5px; font-weight: bold; }
        .user-btn.active { background: #3b82f6; color: white; }
        
        .input-row { display: flex; gap: 10px; }
        input { flex: 1; background: #0f172a; border: 1px solid #475569; color: white; padding: 12px; border-radius: 6px; }
        .send-btn { background: #2563eb; border: none; color: white; padding: 0 25px; border-radius: 6px; cursor: pointer; font-weight: bold; }
        
        /* Stats Styling */
        .ping-res { background: #0f172a; padding: 12px; border-radius: 8px; margin-top: 10px; display: flex; justify-content: space-between; font-size: 0.9rem; }
        .lost { color: #ef4444; font-weight: bold; }
        
        .footer { grid-column: span 2; text-align: center; color: #64748b; font-size: 0.8rem; margin-top: 30px; padding: 15px; border-top: 1px solid #334155; }
        .brand { color: #60a5fa; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h2>💬 TCP Chat Engine</h2>
            <div id="chatBox"></div>
            
            <div class="controls">
                <div class="user-toggle">
                    <button class="user-btn active" id="btnArya" onclick="setUser('Arya')">User: Arya</button>
                    <button class="user-btn" id="btnLux" onclick="setUser('lakshita')">User: lakshita</button>
                </div>
                <div class="input-row">
                    <input type="text" id="msgInput" placeholder="Message to server...">
                    <button class="send-btn" onclick="sendMsg()">Send</button>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>📡 UDP Diagnostics</h2>
            <button onclick="runPing()" id="pingBtn" style="width:100%; padding:12px; background:#10b981; border:none; color:white; border-radius:6px; cursor:pointer; font-weight:bold;">Start RTT Analysis</button>
            <div id="pingStats" style="margin-top:20px;"></div>
        </div>

        <div class="footer">
            <span class="brand">System Architect: Arya</span> | TCP/IP Socket Implementation v2.0 | [Course: 18B11CS311]
        </div>
    </div>

    <script>
        let currentUser = 'Arya';

        function setUser(user) {
            currentUser = user;
            document.getElementById('btnArya').classList.toggle('active', user === 'Arya');
            document.getElementById('btnLux').classList.toggle('active', user === 'Lakshita');
        }

        function updateChat() {
            fetch('/api/messages').then(r => r.json()).then(msgs => {
                const box = document.getElementById('chatBox');
                box.innerHTML = msgs.map(m => `<div class="msg-line">${m}</div>`).join('');
                box.scrollTop = box.scrollHeight;
            });
        }

        function sendMsg() {
            const input = document.getElementById('msgInput');
            if(!input.value) return;
            fetch('/api/send', {
                method: 'POST',
                body: JSON.stringify({ user: currentUser, msg: input.value })
            }).then(() => { input.value = ''; });
        }

        function runPing() {
            const btn = document.getElementById('pingBtn');
            const stats = document.getElementById('pingStats');
            btn.innerText = "Pinging..."; btn.disabled = true;
            fetch('/api/ping', {method: 'POST'}).then(r => r.json()).then(data => {
                stats.innerHTML = data.map((r, i) => `
                    <div class="ping-res">
                        <span>Sequence ${i+1}</span>
                        <span>${r ? r+' ms' : '<span class="lost">DROPPED</span>'}</span>
                    </div>`).join('');
                btn.innerText = "Start RTT Analysis"; btn.disabled = false;
            });
        }

        setInterval(updateChat, 1000);
        updateChat();
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    print("="*50)
    print(f"Hub Running: http://127.0.0.1:{WEB_PORT}")
    print("="*50)
    HTTPServer(('0.0.0.0', WEB_PORT), DashboardHandler).serve_forever()
