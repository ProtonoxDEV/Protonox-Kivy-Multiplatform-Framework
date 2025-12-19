#!/usr/bin/env python3
"""
Simple HTTP server for ADB wireless setup automation.
Serves a web page with a button to trigger ADB connect from the phone.
"""

import http.server
import socketserver
import subprocess
import threading
import time
from urllib.parse import parse_qs, urlparse

PORT = 8081
LOCAL_IP = "172.24.175.151"

class ADBSetupHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Protonox ADB Wireless Setup</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: Arial, sans-serif; text-align: center; padding: 20px; }}
        button {{ font-size: 18px; padding: 10px 20px; margin: 10px; }}
        #status {{ margin-top: 20px; }}
        .preview {{ border: 1px solid #ccc; padding: 10px; margin: 20px auto; max-width: 300px; background: #f9f9f9; }}
    </style>
</head>
<body>
    <h1>Protonox ADB Wireless Setup</h1>
    <p>Conecta tu dispositivo Android inalámbricamente al PC.</p>
    
    <div class="preview">
        <h3>Preview de la App</h3>
        <p><strong>Hello from Protonox!</strong></p>
        <p>KivyMD + ScissorPush/ScissorPop funcionando</p>
        <p>Ready for wireless debug</p>
        <p style="color: green;">[Simulación - App real se ejecuta en Kivy]</p>
    </div>
    
    <button onclick="connectADB()">Connect ADB</button>
    <div id="status"></div>

    <script>
        async function connectADB() {{
            const status = document.getElementById('status');
            status.innerHTML = 'Conectando...';
            try {{
                const response = await fetch('/connect');
                const result = await response.text();
                status.innerHTML = result;
            }} catch (error) {{
                status.innerHTML = 'Error: ' + error.message;
            }}
        }}
    </script>
</body>
</html>
            """
            self.wfile.write(html.encode())
        elif self.path.startswith('/connect'):
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            try:
                # Run adb connect
                result = subprocess.run(['adb', 'connect', f'{LOCAL_IP}:5555'],
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    response = "ADB connected successfully!"
                else:
                    response = f"ADB connect failed: {result.stderr}"
            except Exception as e:
                response = f"Error: {str(e)}"
            self.wfile.write(response.encode())
        else:
            self.send_error(404)

def run_server():
    with socketserver.TCPServer(("", PORT), ADBSetupHandler) as httpd:
        print(f"ADB Setup Server running at http://{LOCAL_IP}:{PORT}")
        print("Scan the QR code with your Android camera to open this page.")
        httpd.serve_forever()

if __name__ == '__main__':
    run_server()