import socket
import threading
import time
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from collections import deque

# --- CONFIGURATION ---
WEB_PORT = 8080
TCP_HOST, TCP_PORT = '127.0.0.1', 12345
UDP_HOST, UDP_PORT = '127.0.0.1', 12000

# Chat Store
messages = deque(maxlen=100)
msg_lock = threading.Lock()

# Persistent User Connections (Prevents Joined/Left spam)
user_sockets = {}

class DashboardHandler(BaseHTTPRequestHandler):
    # Ye function HTTP Request logs ko terminal par print hone se rokega
    def log_message(self, format, *args):
        pass 

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
            # Agar user pehli baar message bhej raha hai, toh naya connection banao
            if username not in user_sockets:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((TCP_HOST, TCP_PORT))
                s.recv(1024) 
                s.send(username.encode())
                s.recv(1024)
                user_sockets[username] = s
                time.sleep(0.1) # Wait slightly for handshake
            
            # Message bhejo (connection open rahega)
            user_sockets[username].send(msg.encode())
        except Exception:
            if username in user_sockets:
                del user_sockets[username]

    def run_udp_ping(self):
        rtts = []
        lost = 0
        # Exactly 10 pings bhejo, jaise terminal ping karta hai
        for i in range(1, 11):
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(1.0)
            t0 = time.time()
            try:
                s.sendto(f"PING {i}".encode(), (UDP_HOST, UDP_PORT))
                s.recvfrom(1024)
                rtts.append(round((time.time()-t0)*1000, 2))
            except: 
                rtts.append(None)
                lost += 1
            s.close()
            time.sleep(0.1)
        
        valid = [r for r in rtts if r is not None]
        # Calculate terminal-like statistics
        return {
            "rtts": rtts, "sent": 10, "received": len(valid), "lost": lost,
            "loss_pct": int((lost/10)*100),
            "min": min(valid) if valid else 0, "max": max(valid) if valid else 0,
            "avg": round(sum(valid)/len(valid), 2) if valid else 0
        }

def global_listener():
    # Ye background process chat server se saare messages fetch karke UI ko degi
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((TCP_HOST, TCP_PORT))
            sock.recv(1024)
            sock.send("Dashboard_Logger".encode())
            sock.recv(1024)
            while True:
                data = sock.recv(1024).decode()
                if not data: break
                with msg_lock:
                    messages.append(data)
        except: time.sleep(2)

threading.Thread(target=global_listener, daemon=True).start()

# --- TERMINAL-STYLE HTML UI ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CN Socket Terminal Hub | Arya</title>
    <style>
        body { background: #0a0a0a; color: #10b981; font-family: 'Consolas', 'Courier New', monospace; margin: 0; padding: 20px; }
        .container { max-width: 1000px; margin: auto; display: grid; grid-template-columns: 1.4fr 1.2fr; gap: 20px; }
        .card { background: #111; border-radius: 8px; padding: 20px; border: 1px solid #333; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        h2 { color: #facc15; margin-top: 0; font-size: 1.2rem; border-bottom: 1px dashed #444; padding-bottom: 10px; text-transform: uppercase; }
        
        #chatBox, #pingStats { height: 350px; overflow-y: auto; background: #000; padding: 15px; border: 1px solid #222; margin-bottom: 15px; font-size: 0.9rem; line-height: 1.4; color: #e5e5e5; }
        .msg-line { margin-bottom: 4px; }
        .server-msg { color: #f59e0b; font-style: italic; }
        
        .user-toggle { display: flex; gap: 10px; margin-bottom: 10px; }
        .user-btn { flex: 1; padding: 10px; border: 1px solid #2563eb; background: transparent; color: #2563eb; cursor: pointer; font-family: inherit; font-weight: bold; transition: 0.2s; }
        .user-btn.active { background: #2563eb; color: white; }
        
        .input-row { display: flex; gap: 10px; }
        input { flex: 1; background: #000; border: 1px solid #444; color: #10b981; padding: 10px; font-family: inherit; }
        input:focus { outline: none; border-color: #10b981; }
        .send-btn, #pingBtn { background: #10b981; border: none; color: #000; padding: 10px 20px; cursor: pointer; font-weight: bold; font-family: inherit; text-transform: uppercase; }
        #pingBtn { width: 100%; margin-bottom: 10px; }
        
        .footer { grid-column: span 2; text-align: center; color: #555; font-size: 0.8rem; margin-top: 20px; border-top: 1px dashed #333; padding-top: 15px; }
        
        /* Ping Stats Formatting */
        .ping-res { display: flex; justify-content: space-between; color: #9ca3af; }
        .lost { color: #ef4444; font-weight: bold; }
        .stat-summary { color: #3b82f6; margin-top: 10px; border-top: 1px dashed #333; padding-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h2>> TCP_CHAT_CONSOLE</h2>
            <div id="chatBox">Waiting for messages...</div>
            <div class="user-toggle">
                <button class="user-btn active" id="btn1" onclick="setUser('User_1')">[ Select: User_1 ]</button>
                <button class="user-btn" id="btn2" onclick="setUser('User_2')">[ Select: User_2 ]</button>
            </div>
            <div class="input-row">
                <input type="text" id="msgInput" placeholder="C:\\TCP\\Message> Type here..." onkeypress="if(event.key === 'Enter') sendMsg()">
                <button class="send-btn" onclick="sendMsg()">SEND</button>
            </div>
        </div>

        <div class="card">
            <h2>> UDP_PING_DIAGNOSTICS</h2>
            <button onclick="runPing()" id="pingBtn">EXECUTE PING 127.0.0.1</button>
            <div id="pingStats">Ready to transmit 10 UDP packets...</div>
        </div>

        <div class="footer">
            [ SYSTEM ADMIN: ARYA ] | TCP/UDP/HTTP SOCKET IMPLEMENTATION | COURSE: 18B11CS311
        </div>
    </div>

    <script>
        let currentUser = 'User_1';
        
        function setUser(user) {
            currentUser = user;
            document.getElementById('btn1').classList.toggle('active', user === 'User_1');
            document.getElementById('btn2').classList.toggle('active', user === 'User_2');
        }

        function updateChat() {
            fetch('/api/messages').then(r => r.json()).then(msgs => {
                const box = document.getElementById('chatBox');
                let isAtBottom = box.scrollHeight - box.scrollTop <= box.clientHeight + 10;
                
                box.innerHTML = msgs.map(m => {
                    let cls = m.includes('[SERVER]') ? 'server-msg' : '';
                    return `<div class="msg-line ${cls}">${m}</div>`;
                }).join('');
                
                if (isAtBottom) box.scrollTop = box.scrollHeight;
            });
        }

        function sendMsg() {
            const input = document.getElementById('msgInput');
            if(!input.value.trim()) return;
            fetch('/api/send', {
                method: 'POST',
                body: JSON.stringify({ user: currentUser, msg: input.value })
            }).then(() => { input.value = ''; updateChat(); });
        }

        function runPing() {
            const btn = document.getElementById('pingBtn');
            const stats = document.getElementById('pingStats');
            btn.innerText = "TRANSMITTING..."; btn.disabled = true;
            stats.innerHTML = "Pinging 127.0.0.1 with 32 bytes of data...<br><br>";
            
            fetch('/api/ping', {method: 'POST'}).then(r => r.json()).then(data => {
                let html = data.rtts.map((r, i) => {
                    let res = r ? `time=${r}ms` : `<span class="lost">Request timed out.</span>`;
                    return `<div class="ping-res">Reply from 127.0.0.1: seq=${i+1} ${res}</div>`;
                }).join('');
                
                html += `
                    <div class="stat-summary">
                        <b>Ping statistics for 127.0.0.1:</b><br>
                        &nbsp;&nbsp;&nbsp;&nbsp;Packets: Sent = ${data.sent}, Received = ${data.received}, Lost = ${data.lost} (${data.loss_pct}% loss)<br>
                    </div>`;
                
                if (data.received > 0) {
                    html += `
                    <div style="color: #10b981;">
                        <b>Approximate round trip times in milli-seconds:</b><br>
                        &nbsp;&nbsp;&nbsp;&nbsp;Minimum = ${data.min}ms, Maximum = ${data.max}ms, Average = ${data.avg}ms
                    </div>`;
                }
                
                stats.innerHTML += html;
                btn.innerText = "EXECUTE PING 127.0.0.1"; btn.disabled = false;
            });
        }

        setInterval(updateChat, 1000);
        updateChat();
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    print("==================================================")
    print(f"  WEB DASHBOARD TERMINAL STARTED")
    print(f"  Access UI at: http://127.0.0.1:{WEB_PORT}")
    print(f"  (HTTP logs are muted for a cleaner terminal)")
    print("==================================================")
    HTTPServer(('0.0.0.0', WEB_PORT), DashboardHandler).serve_forever()
