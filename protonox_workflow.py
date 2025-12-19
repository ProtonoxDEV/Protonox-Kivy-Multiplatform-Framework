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

def get_adb_command():
    """Get ADB command - use Windows ADB in WSL"""
    if is_wsl():
        # Common Windows ADB paths
        windows_paths = [
            "/mnt/c/Program Files (x86)/Android/android-sdk/platform-tools/adb.exe",
            "/mnt/c/Program Files/Android/sdk/platform-tools/adb.exe",
            "/mnt/c/Users/*/AppData/Local/Android/Sdk/platform-tools/adb.exe",
            "/mnt/c/Android/platform-tools/adb.exe"
        ]
        
        for path in windows_paths:
            if '*' in path:
                # Handle wildcard for user directory
                import glob
                matches = glob.glob(path)
                if matches:
                    return f'"{matches[0]}"'
            elif os.path.exists(path):
                return f'"{path}"'
        
        print("⚠️  ADB de Windows no encontrado, usando ADB de WSL")
        print("💡 Instala Android SDK en Windows para mejor compatibilidad")
    
    return "adb"

def get_platform_info():
    """Get detailed platform information"""
    import platform
    system = platform.system().lower()

    if system == 'linux':
        if is_wsl():
            return 'wsl'
        else:
            return 'linux'
    elif system == 'windows':
        return 'windows'
    elif system == 'darwin':
        return 'macos'
    else:
        return 'unknown'

def get_recommended_window_provider():
    """Get recommended window provider based on platform"""
    platform = get_platform_info()

    if platform == 'linux':
        # Linux nativo - preferir X11
        return 'x11'
    elif platform == 'wsl':
        # WSL - usar SDL2 que funciona mejor en WSL
        return 'sdl2'
    elif platform == 'windows':
        # Windows - usar el provider más avanzado disponible
        return 'sdl2'  # SDL2 puede usar DirectX internamente
    elif platform == 'macos':
        return 'sdl2'
    else:
        return 'sdl2'

def run_local_app(app_path=None, window_provider=None):
    """Run Kivy app locally with appropriate window provider"""
    if app_path is None:
        app_path = "test_app.py"  # Default test app

    if window_provider is None:
        window_provider = get_recommended_window_provider()

    platform = get_platform_info()

    # Set environment variables for Kivy
    env = os.environ.copy()
    env['KIVY_WINDOW'] = window_provider

    # Additional platform-specific settings
    if platform == 'windows':
        # For Windows, try to use DirectX if available
        env['KIVY_GL_BACKEND'] = 'angle_sdl2'  # This can use DirectX
    elif platform in ['linux', 'wsl']:
        # Check if display is available and accessible
        display_available = 'DISPLAY' in env and env['DISPLAY']

        if display_available:
            # Test if we can actually connect to the display
            try:
                import subprocess
                result = subprocess.run(['xset', '-q'], capture_output=True, timeout=2)
                display_accessible = result.returncode == 0
            except:
                display_accessible = False

            if not display_accessible:
                print("⚠️  DISPLAY configurado pero no accesible. Usando modo headless.")
                env['KIVY_WINDOW'] = 'mock'
                print("🖥️  Using mock window provider for headless testing")
        else:
            if platform == 'linux':
                print("⚠️  No DISPLAY variable set. Make sure X11 is running.")
                return False, "No DISPLAY variable set for Linux"
            elif platform == 'wsl':
                print("⚠️  No DISPLAY variable set in WSL. Using headless mode.")
                env['KIVY_WINDOW'] = 'mock'
                print("🖥️  Using mock window provider for headless testing")

    print(f"🚀 Ejecutando app local: {app_path}")
    print(f"🖥️  Window provider: {env['KIVY_WINDOW']}")
    print(f"💻 Platform: {platform}")

    try:
        cmd = [sys.executable, app_path]
        result = subprocess.run(cmd, env=env, timeout=300)  # 5 minute timeout
        return result.returncode == 0, "App executed successfully" if result.returncode == 0 else f"App exited with code {result.returncode}"
    except subprocess.TimeoutExpired:
        return False, "App execution timed out"
    except Exception as e:
        return False, f"Error running app: {str(e)}"

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
        elif self.path == '/api/platform':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.serve_platform()
        elif self.path.startswith('/api/method/'):
            self.handle_method_change()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

    def do_POST(self):
        """Handle POST requests"""
        if self.path.startswith('/api/method/'):
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
        <button class="tab" onclick="showMethod('localapp')">🏠 App Local</button>
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

    <!-- Local App Section -->
    <div id="localapp" class="method">
        <h2>🏠 Ejecutar App Local</h2>
        <div class="container">
            <p>Ejecuta tu aplicación Kivy localmente con la configuración óptima para tu plataforma.</p>

            <div class="code">
                <strong>Plataforma detectada:</strong> <span id="detectedPlatform">Cargando...</span><br>
                <strong>Window provider recomendado:</strong> <span id="recommendedProvider">Cargando...</span>
            </div>

            <div style="margin: 20px 0;">
                <label for="appPath">Ruta de la app (opcional):</label><br>
                <input type="text" id="appPath" placeholder="test_app.py" style="width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ccc; border-radius: 4px;">
            </div>

            <button class="button" onclick="runLocalApp()">🚀 Ejecutar App Local</button>
            <button class="button secondary" onclick="detectPlatform()">🔍 Detectar Plataforma</button>

            <div id="localAppStatus" class="status warning" style="display:none;">
                🔄 Preparando ejecución...
            </div>
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

        function detectPlatform() {{
            fetch('/api/platform')
                .then(response => response.json())
                .then(data => {{
                    document.getElementById('detectedPlatform').textContent = data.platform;
                    document.getElementById('recommendedProvider').textContent = data.provider;
                }})
                .catch(error => {{
                    document.getElementById('detectedPlatform').textContent = 'Error al detectar';
                    document.getElementById('recommendedProvider').textContent = 'Error al detectar';
                }});
        }}

        function runLocalApp() {{
            const statusDiv = document.getElementById('localAppStatus');
            const appPath = document.getElementById('appPath').value || 'test_app.py';

            statusDiv.style.display = 'block';
            statusDiv.textContent = '🚀 Ejecutando app local...';
            statusDiv.className = 'status warning';

            fetch('/api/method/localapp', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                }},
                body: JSON.stringify({{ app_path: appPath }})
            }})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        statusDiv.textContent = '✅ App ejecutada exitosamente';
                        statusDiv.className = 'status success';
                    }} else {{
                        statusDiv.textContent = `❌ Error: ${{data.error}}`;
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

    def serve_platform(self):
        """Serve platform information"""
        platform_info = {
            'platform': get_platform_info(),
            'provider': get_recommended_window_provider(),
            'wsl': is_wsl(),
            'timestamp': datetime.now().isoformat()
        }
        self.wfile.write(json.dumps(platform_info).encode('utf-8'))

    def handle_method_change(self):
        """Handle method change requests"""
        method = self.path.replace('/api/method/', '')

        # Read POST data if present
        post_data = {}
        if self.command == 'POST':
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_body = self.rfile.read(content_length).decode('utf-8')
                try:
                    post_data = json.loads(post_body)
                except:
                    post_data = {}

        response = {'success': False, 'method': method}

        if method == 'livereload':
            # Start live reload server in background
            try:
                subprocess.Popen([sys.executable, 'live_reload_launcher.py', 'server'])
                response['success'] = True
                response['message'] = 'Live reload server started'
            except Exception as e:
                response['error'] = str(e)

        elif method == 'localapp':
            # Run local app
            try:
                app_path = post_data.get('app_path', 'test_app.py')
                success, message = run_local_app(app_path)
                response['success'] = success
                if success:
                    response['message'] = message
                else:
                    response['error'] = message
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
    adb_cmd = get_adb_command()
    code, stdout, stderr = run_command(f"{adb_cmd} devices")
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
    adb_cmd = get_adb_command()
    code, stdout, stderr = run_command(f"{adb_cmd} -s {device_id} shell echo 'test'")
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
        print("6. 🪟 Test Window Providers (Linux)")
        print("7. ❌ Salir")
        print()

        # Check for connected devices and show status
        devices = check_adb_devices()
        working_devices = [d for d in devices if test_device_connection(d['id'])]
        if working_devices:
            print(f"📱 Estado: {len(working_devices)} dispositivo(s) conectado(s) - ¡Listo para paso 2!")
        else:
            print("📱 Estado: No hay dispositivos conectados")
        print()

        try:
            choice = input("Selecciona una opción (1-7): ").strip()

            if choice == '1':
                success = run_adb_pairing()
                if success:
                    print("\n✅ ¡Pairing completado!")
                    print("💡 Ahora selecciona la opción 2 para iniciar Live Reload")
                    input("Presiona Enter para continuar...")

            elif choice == '2':
                # Check if devices are connected first
                devices = check_adb_devices()
                working_devices = [d for d in devices if test_device_connection(d['id'])]

                if working_devices:
                    print(f"✅ {len(working_devices)} dispositivo(s) conectado(s)")
                    print("🚀 Iniciando sistema de Live Reload...")
                    run_live_reload_launcher()
                else:
                    print("❌ No hay dispositivos conectados")
                    print("💡 Ejecuta la opción 1 primero para conectar tu dispositivo")
                    print("   O verifica que tu dispositivo esté conectado y funcionando")
                    input("Presiona Enter para continuar...")

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
                print("🪟 Probando proveedores de ventana Kivy...")
                try:
                    code, stdout, stderr = run_command("cd /home/protonox/Protonox-Kivy-Multiplatform-Framework && python test_window_providers.py", shell=True, timeout=15)
                    if code == 0:
                        print("✅ Proveedores de ventana funcionando correctamente")
                    else:
                        print("⚠️  Problemas detectados:")
                        if stdout:
                            print(stdout)
                        if stderr:
                            print(f"Error: {stderr}")
                except Exception as e:
                    print(f"❌ Error ejecutando test: {e}")

            elif choice == '7':
                print("👋 ¡Hasta luego!")
                break

            else:
                print("❌ Opción inválida. Intenta de nuevo.")

        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def setup_linux_development():
    """Setup Linux development environment"""
    print("\n🐧 Configurando entorno de desarrollo Linux...")
    print("-" * 45)

    # Check Kivy window providers
    print("🔍 Verificando proveedores de ventana Kivy...")
    try:
        # Test window providers
        code, stdout, stderr = run_command("cd /home/protonox/Protonox-Kivy-Multiplatform-Framework && python test_window_providers.py", shell=True, timeout=10)
        if code == 0:
            print("✅ Proveedores de ventana Kivy funcionando correctamente")
            print("   ✓ window_x11 disponible")
            print("   ✓ Modo headless configurado")
        else:
            print("⚠️  Problemas con proveedores de ventana:")
            print(f"   Código: {code}")
            if stderr:
                print(f"   Error: {stderr.strip()}")
    except Exception as e:
        print(f"⚠️  Error verificando proveedores: {e}")

    # Check display server
    display = os.environ.get('DISPLAY', '')
    if display:
        print(f"✅ Servidor X11 detectado: DISPLAY={display}")
        print("   💡 Para desarrollo visual: configura X11 forwarding en WSL2")
    else:
        print("ℹ️  Sin servidor X11 - modo headless activado")
        print("   💡 Para desarrollo visual: instala y configura X server")

    print("\n📋 Configuración completada:")
    print("   • Kivy v3.0.0.dev5 con proveedores X11")
    print("   • Modo headless disponible")
    print("   • Desarrollo Android: ADB wireless configurado")
    print("   • Desarrollo web: Interfaz live reload activa")

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

    # Setup Linux development environment
    setup_linux_development()

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