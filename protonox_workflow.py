#!/usr/bin/env python3
"""
Protonox Complete Development Workflow
ADB Pairing + Live Reload Launcher + Web Interface
Optimizado para WSL2 + Windows 11
"""

import subprocess
import sys
import os
import time
import threading
import socket
import json
import random
import http.server
import socketserver
from datetime import datetime

try:
    import qrcode
    HAS_QR = True
except ImportError:
    HAS_QR = False

def run_command(command, shell=False, timeout=30):
    """Run command and return result"""
    try:
        if shell:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        else:
            result = subprocess.run(command.split(), capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def get_local_ip():
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def is_wsl():
    """Check if running in WSL"""
    try:
        with open('/proc/version', 'r') as f:
            return 'microsoft' in f.read().lower()
    except:
        return False

def generate_pairing_code():
    """Generate 6-digit pairing code"""
    return str(random.randint(100000, 999999))

def generate_adb_qr(device_name, pairing_code):
    """Generate ADB pairing QR code"""
    payload = f"WIFI:T:ADB;S:{device_name};P:{pairing_code};;"

    try:
        # Try qrencode first
        result = subprocess.run(['qrencode', '-t', 'UTF8', payload],
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return result.stdout
    except:
        pass

    # Fallback to Python qrcode
    if HAS_QR:
        try:
            qr = qrcode.QRCode(version=1, box_size=1, border=1)
            qr.add_data(payload)
            qr.make(fit=True)

            matrix = qr.get_matrix()
            qr_art = []
            for row in matrix:
                line = ""
                for cell in row:
                    line += "█" if cell else "░"
                qr_art.append(line)

            return "\n".join(qr_art)
        except:
            pass

    return f"Payload: {payload}\n(Instala qrencode o qrcode[pil] para ver el QR)"

def open_windows_browser(url):
    """Open URL in Windows browser from WSL"""
    try:
        subprocess.run(['explorer.exe', url], check=True, timeout=5)
        print(f"🪟 Abriendo {url} en navegador de Windows...")
        return True
    except:
        print(f"💡 No se pudo abrir automáticamente. Abre manualmente: {url}")
        return False

class WorkflowWebServer(http.server.SimpleHTTPRequestHandler):
    """Web server for workflow management"""

    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.serve_main_page()
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.serve_status()
        elif self.path == '/api/devices':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.serve_devices()
        elif self.path.startswith('/api/method/'):
            self.handle_method_change()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

    def serve_main_page(self):
        """Serve main workflow interface"""
        ip = get_local_ip()
        pairing_code = generate_pairing_code()
        device_name = "ProtonoxWSL"

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>🎯 Protonox Development Workflow</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }}
        .container {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 30px;
            margin: 20px 0;
            backdrop-filter: blur(10px);
        }}
        .method {{
            background: rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
            border-left: 4px solid #4CAF50;
            display: none;
        }}
        .method.active {{ display: block; }}
        .qr-code {{
            background: white;
            color: black;
            padding: 20px;
            border-radius: 8px;
            font-family: monospace;
            white-space: pre;
            overflow-x: auto;
            margin: 10px 0;
        }}
        .code {{
            background: rgba(0, 0, 0, 0.3);
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            margin: 5px 0;
            word-break: break-all;
        }}
        .button {{
            background: #4CAF50;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            margin: 10px 5px;
            font-size: 16px;
            transition: background 0.3s;
        }}
        .button:hover {{ background: #45a049; }}
        .button.secondary {{ background: #2196F3; }}
        .button.secondary:hover {{ background: #1976D2; }}
        .status {{
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .success {{ background: rgba(76, 175, 80, 0.2); }}
        .error {{ background: rgba(244, 67, 54, 0.2); }}
        .warning {{ background: rgba(255, 152, 0, 0.2); }}
        .tabs {{
            display: flex;
            margin-bottom: 20px;
        }}
        .tab {{
            background: rgba(255, 255, 255, 0.2);
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            border-radius: 5px 5px 0 0;
            margin-right: 5px;
            color: white;
        }}
        .tab.active {{
            background: rgba(255, 255, 255, 0.3);
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <h1>🎯 Protonox Development Workflow</h1>
    <p>🐧 Optimizado para WSL2 + Windows 11 | 🔧 ADB Wireless + 🔄 Live Reload</p>

    <div class="tabs">
        <button class="tab active" onclick="showMethod('pairing')">🔧 ADB Pairing</button>
        <button class="tab" onclick="showMethod('livereload')">🔄 Live Reload</button>
        <button class="tab" onclick="showMethod('status')">📊 Estado</button>
    </div>

    <!-- ADB Pairing Section -->
    <div id="pairing" class="method active">
        <h2>🔧 ADB Wireless Pairing</h2>
        <div class="container">
            <h3>📱 Información de Conexión</h3>
            <div class="code">
                <strong>IP del servidor:</strong> {ip}<br>
                <strong>Nombre del dispositivo:</strong> {device_name}<br>
                <strong>Código de pairing:</strong> {pairing_code}
            </div>
        </div>

        <div class="container">
            <h3>🎯 Método 1: Código QR (Recomendado)</h3>
            <p>Escanea este QR con tu dispositivo Android:</p>
            <p><strong>Developer Options → Wireless debugging → Pair device with QR code</strong></p>
            <div class="qr-code">{generate_adb_qr(device_name, pairing_code)}</div>
            <p><small>Payload: WIFI:T:ADB;S:{device_name};P:{pairing_code};;</small></p>
            <button class="button" onclick="copyPayload()">📋 Copiar Payload</button>
        </div>

        <div class="container">
            <h3>🔢 Método 2: Código Numérico (Alternativo)</h3>
            <p>Si el QR no funciona (común en WSL2), usa este método:</p>
            <ol>
                <li>En tu dispositivo Android: <strong>Developer Options → Wireless debugging → 'Pair device with pairing code'</strong></li>
                <li>El teléfono mostrará una pantalla con: <strong>IP address, Port y Pairing code</strong></li>
                <li><strong>Copia estos datos del teléfono</strong> y úsalos abajo:</li>
            </ol>
            <div class="code" style="background: rgba(255, 193, 7, 0.2); border-left: 4px solid #FFC107;">
                <strong>📱 Datos que verás en tu teléfono:</strong><br>
                • IP Address: [número que aparece en el teléfono]<br>
                • Port: [número que aparece en el teléfono]<br>
                • Pairing Code: [código que aparece en el teléfono]
            </div>
            <p><strong>Una vez que tengas estos datos del teléfono, ejecuta:</strong></p>
            <div class="code">
                adb pair [IP del teléfono]:[puerto del teléfono] [código del teléfono]
            </div>
            <button class="button secondary" onclick="runNumericPairing()">🚀 Iniciar Pairing Numérico</button>
        </div>

        <div class="container">
            <h3>🖥️ Método 3: Comandos ADB Manuales</h3>
            <div class="code">
                adb pair {ip}:37329 {pairing_code}<br>
                adb connect {ip}:5555
            </div>
            <button class="button" onclick="runManualADB()">🚀 Ejecutar Comandos</button>
        </div>
    </div>

    <!-- Live Reload Section -->
    <div id="livereload" class="method">
        <h2>🔄 Live Reload System</h2>
        <div class="container">
            <p>Una vez que tu dispositivo esté conectado, puedes usar el sistema de live reload.</p>
            <button class="button" onclick="startLiveReload()">🚀 Iniciar Live Reload</button>
            <div id="livereloadStatus" class="status warning" style="display:none;">
                🔄 Iniciando servidor de live reload...
            </div>
        </div>
    </div>

    <!-- Status Section -->
    <div id="status" class="method">
        <h2>📊 Estado del Sistema</h2>
        <div id="systemStatus" class="status warning">
            🔄 Cargando estado del sistema...
        </div>
        <button class="button" onclick="refreshStatus()">🔍 Actualizar</button>
    </div>

    <script>
        let currentMethod = 'pairing';

        function showMethod(method) {{
            // Hide all methods
            document.querySelectorAll('.method').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));

            // Show selected method
            document.getElementById(method).classList.add('active');
            event.target.classList.add('active');
            currentMethod = method;

            // Refresh content if needed
            if (method === 'status') {{
                refreshStatus();
            }}
        }}

        function copyPayload() {{
            const payload = 'WIFI:T:ADB;S:{device_name};P:{pairing_code};;';
            navigator.clipboard.writeText(payload).then(() => {{
                alert('Payload copiado al portapapeles');
            }});
        }}

        function runNumericPairing() {{
            alert('🔢 Método Numérico:\\n\\n1. En tu teléfono: Developer Options → Wireless debugging → Pair device with pairing code\\n\\n2. El teléfono mostrará IP, puerto y código\\n\\n3. Ejecuta en WSL:\\n   adb pair [IP del teléfono]:[puerto del teléfono] [código del teléfono]\\n\\n4. Luego:\\n   adb connect [IP del teléfono]:5555');
        }}

        function runManualADB() {{
            alert('Ejecuta estos comandos en tu terminal WSL:\\n\\nadb pair {ip}:37329 {pairing_code}\\nadb connect {ip}:5555');
        }}

        function startLiveReload() {{
            const statusDiv = document.getElementById('livereloadStatus');
            statusDiv.style.display = 'block';
            statusDiv.textContent = '🔄 Iniciando servidor de live reload...';

            // This would trigger the live reload server
            fetch('/api/method/livereload', {{ method: 'POST' }})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        statusDiv.textContent = '✅ Live reload iniciado';
                        statusDiv.className = 'status success';
                    }} else {{
                        statusDiv.textContent = '❌ Error al iniciar live reload';
                        statusDiv.className = 'status error';
                    }}
                }})
                .catch(error => {{
                    statusDiv.textContent = '❌ Error de conexión';
                    statusDiv.className = 'status error';
                }});
        }}

        function refreshStatus() {{
            const statusDiv = document.getElementById('systemStatus');
            statusDiv.textContent = '🔄 Cargando estado del sistema...';
            statusDiv.className = 'status warning';

            fetch('/api/status')
                .then(response => response.json())
                .then(data => {{
                    let html = '<div class="success">✅ Estado del sistema:</div>';
                    html += `<div>• WSL2: ${{data.wsl ? '✅ Detectado' : '❌ No detectado'}}</div>`;
                    html += `<div>• ADB: ${{data.adb_available ? '✅ Disponible' : '❌ No disponible'}}</div>`;
                    html += `<div>• IP Local: ${{data.ip}}</div>`;
                    html += `<div>• Dispositivos: ${{data.devices_count}} conectado(s)</div>`;

                    if (data.devices && data.devices.length > 0) {{
                        html += '<div><strong>Dispositivos:</strong></div>';
                        data.devices.forEach(device => {{
                            html += `<div>  • ${{device.id}} - ${{device.status}}</div>`;
                        }});
                    }}

                    statusDiv.innerHTML = html;
                    statusDiv.className = 'status success';
                }})
                .catch(error => {{
                    statusDiv.textContent = '❌ Error al obtener estado';
                    statusDiv.className = 'status error';
                }});
        }}

        // Auto-refresh status every 10 seconds when status tab is active
        setInterval(() => {{
            if (currentMethod === 'status') {{
                refreshStatus();
            }}
        }}, 10000);

        // Initial status load
        refreshStatus();
    </script>
</body>
</html>"""
        self.wfile.write(html.encode('utf-8'))

    def serve_status(self):
        """Serve system status"""
        status = {
            'wsl': is_wsl(),
            'adb_available': run_command("adb version")[0] == 0,
            'ip': get_local_ip(),
            'devices_count': len(check_adb_devices()),
            'devices': check_adb_devices(),
            'timestamp': datetime.now().isoformat()
        }
        self.wfile.write(json.dumps(status).encode('utf-8'))

    def serve_devices(self):
        """Serve device list"""
        devices = check_adb_devices()
        response = {
            'devices': devices,
            'count': len(devices),
            'timestamp': datetime.now().isoformat()
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def handle_method_change(self):
        """Handle method change requests"""
        method = self.path.replace('/api/method/', '')

        response = {'success': False, 'method': method}

        if method == 'livereload':
            # Start live reload server in background
            try:
                subprocess.Popen([sys.executable, 'live_reload_launcher.py', 'server'])
                response['success'] = True
                response['message'] = 'Live reload server started'
            except Exception as e:
                response['error'] = str(e)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))

def start_web_interface(port=8080):
    """Start web interface for workflow management"""
    print(f"🌐 Iniciando interfaz web en puerto {port}...")

    with socketserver.TCPServer(("", port), WorkflowWebServer) as httpd:
        ip = get_local_ip()
        print(f"✅ Interfaz web disponible en:")
        print(f"   📱 WSL: http://localhost:{port}")
        print(f"   🪟 Windows: http://{ip}:{port}")
        print("   📋 Presiona Ctrl+C para detener")

        # Auto-open in Windows browser
        if is_wsl():
            open_windows_browser(f"http://{ip}:{port}")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Interfaz web detenida")

def check_adb_devices():
    """Check for connected ADB devices"""
    code, stdout, stderr = run_command("adb devices")
    if code != 0:
        return []

    lines = stdout.strip().split('\n')[1:]  # Skip header
    devices = []

    for line in lines:
        if line.strip() and not line.startswith('*'):
            parts = line.split('\t')
            if len(parts) >= 2:
                device_id = parts[0]
                status = parts[1]
                devices.append({'id': device_id, 'status': status})

    return devices

def test_device_connection(device_id):
    """Test if device is responding"""
    code, stdout, stderr = run_command(f"adb -s {device_id} shell echo 'test'")
    return code == 0 and 'test' in stdout

def run_adb_pairing():
    """Run ADB pairing script"""
    print("🔧 Iniciando proceso de pairing ADB...")
    try:
        cmd = [sys.executable, "adb_pairing_wsl.py"]
        result = subprocess.run(cmd)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error en pairing: {e}")
        return False

def run_live_reload_launcher():
    """Run live reload launcher"""
    print("🔄 Iniciando launcher de live reload...")
    try:
        cmd = [sys.executable, "live_reload_launcher.py", "--menu"]
        subprocess.run(cmd)
    except Exception as e:
        print(f"❌ Error en live reload: {e}")

def show_workflow_menu():
    """Show the complete workflow menu"""
    while True:
        print("\n🚀 PROTONOX COMPLETE DEVELOPMENT WORKFLOW")
        print("=" * 50)
        print("1. 🔧 ADB Wireless Pairing (Conectar dispositivo)")
        print("2. 🔄 Live Reload System (Una vez conectado)")
        print("3. 📊 Ver Estado de Dispositivos")
        print("4. 🌐 Abrir Interfaz Web (Recomendado)")
        print("5. 🧪 Test Completo (Pairing + Live Reload)")
        print("6. ❌ Salir")
        print()

        try:
            choice = input("Selecciona una opción (1-6): ").strip()

            if choice == '1':
                run_adb_pairing()

            elif choice == '2':
                # Check if devices are connected first
                devices = check_adb_devices()
                working_devices = [d for d in devices if test_device_connection(d['id'])]

                if working_devices:
                    print(f"✅ {len(working_devices)} dispositivo(s) conectado(s)")
                    run_live_reload_launcher()
                else:
                    print("❌ No hay dispositivos conectados")
                    print("💡 Ejecuta la opción 1 primero para conectar tu dispositivo")

            elif choice == '3':
                print("\n📊 ESTADO DE DISPOSITIVOS ADB")
                print("=" * 35)
                devices = check_adb_devices()

                if devices:
                    for device in devices:
                        status_icon = "🟢" if device['status'] == 'device' else "🟡"
                        connection_ok = test_device_connection(device['id'])
                        conn_icon = "✅" if connection_ok else "❌"
                        print(f"   {status_icon} {device['id']} - {device['status']} {conn_icon}")
                else:
                    print("❌ No hay dispositivos conectados")
                    print("💡 Conecta tu dispositivo Android por USB o wireless")

            elif choice == '4':
                print("🌐 Iniciando interfaz web...")
                try:
                    start_web_interface()
                except KeyboardInterrupt:
                    print("\n👋 Interfaz web detenida")

            elif choice == '5':
                print("🧪 Ejecutando test completo...")
                print("1. Verificando dispositivos actuales...")
                initial_devices = check_adb_devices()

                print("2. Iniciando pairing ADB...")
                if run_adb_pairing():
                    print("3. Verificando nueva conexión...")
                    time.sleep(2)  # Wait a bit
                    final_devices = check_adb_devices()
                    new_devices = len(final_devices) - len(initial_devices)

                    if new_devices > 0:
                        print(f"✅ ¡Éxito! {new_devices} dispositivo(s) conectado(s)")
                        print("4. Iniciando live reload...")
                        run_live_reload_launcher()
                    else:
                        print("❌ No se detectaron nuevos dispositivos")
                else:
                    print("❌ Falló el proceso de pairing")

            elif choice == '6':
                print("👋 ¡Hasta luego!")
                break

            else:
                print("❌ Opción inválida. Intenta de nuevo.")

        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main function"""
    print("🎯 Protonox Complete Development Workflow")
    print("🐧 Optimizado para WSL2 + Android Wireless Debugging")
    print("=" * 55)

    # Check environment
    if is_wsl():
        print("✅ Entorno WSL2 detectado")
        print("🪟 Interfaz web accesible desde Windows")
    else:
        print("ℹ️  Entorno Linux nativo")

    # Check ADB
    code, stdout, stderr = run_command("adb version")
    if code == 0:
        version = stdout.split('\n')[0] if stdout else "Unknown"
        print(f"✅ ADB disponible: {version}")
    else:
        print("⚠️  ADB no encontrado - instala Android SDK Platform Tools")

    # Check qrencode
    code, stdout, stderr = run_command("qrencode --version")
    if code == 0:
        print("✅ qrencode disponible para QR codes")
    else:
        print("⚠️  qrencode no encontrado - instala con: sudo apt-get install qrencode")

    # Start menu
    show_workflow_menu()

if __name__ == "__main__":
    main()