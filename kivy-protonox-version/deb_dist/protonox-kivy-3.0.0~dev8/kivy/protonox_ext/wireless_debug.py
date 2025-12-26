"""
Wireless debugging for Protonox Kivy apps.

This module enables real-time debugging of Kivy apps running on devices by
starting a WebSocket server that streams logs, UI state, and other telemetry
to connected clients (e.g., Protonox Studio).

Features:
- WebSocket server for live data streaming
- QR code generation for easy device pairing
- Opt-in via PROTONOX_WIRELESS_DEBUG=1
- Automatic IP detection for network access
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import socket
import threading
import time
from typing import Any, Dict, List, Optional

try:
    import qrcode
    import websockets
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False
    qrcode = None
    websockets = None

from kivy.clock import Clock
from kivy.logger import Logger
from kivy.utils import platform

# Global state
_server_thread: Optional[threading.Thread] = None
_server_task: Optional[asyncio.Task] = None
_connected_clients: List[websockets.WebSocketServerProtocol] = []
_data_queue: asyncio.Queue = asyncio.Queue()
_enabled = False


def _get_local_ip() -> str:
    """Get the local IP address for network access."""
    try:
        # Create a socket to determine the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def generate_qr(text: str) -> str:
    """Generate a QR code as ASCII art for the given text."""
    if not HAS_DEPS:
        Logger.warning("[WIRELESS_DEBUG] qrcode not installed; install with: pip install qrcode[pil]")
        return f"QR Text: {text}"
    
    qr = qrcode.QRCode(version=1, box_size=1, border=1)
    qr.add_data(text)
    qr.make(fit=True)
    return qr.print_ascii()


async def _websocket_handler(websocket: websockets.WebSocketServerProtocol, path: str) -> None:
    """Handle WebSocket connections from clients."""
    Logger.info("[WIRELESS_DEBUG] Client connected: %s", websocket.remote_address)
    _connected_clients.append(websocket)
    
    try:
        # Send initial handshake
        await websocket.send(json.dumps({
            "type": "handshake",
            "message": "Connected to Protonox Wireless Debug",
            "timestamp": time.time()
        }))
        
        # Keep connection alive and handle incoming messages
        async for message in websocket:
            try:
                data = json.loads(message)
                Logger.debug("[WIRELESS_DEBUG] Received: %s", data)
                
                # Handle client commands
                if data.get("type") == "command":
                    command = data.get("command")
                    if command == "reload":
                        await _handle_reload_command(data)
                    elif command == "reload_file":
                        await _handle_reload_file_command(data)
                    else:
                        Logger.warning("[WIRELESS_DEBUG] Unknown command: %s", command)
                        
            except json.JSONDecodeError:
                Logger.warning("[WIRELESS_DEBUG] Invalid JSON received")
                
    except websockets.exceptions.ConnectionClosed:
        Logger.info("[WIRELESS_DEBUG] Client disconnected: %s", websocket.remote_address)
    finally:
        if websocket in _connected_clients:
            _connected_clients.remove(websocket)


async def _handle_reload_command(data: Dict[str, Any]) -> None:
    """Handle reload command from client."""
    try:
        Logger.info("[WIRELESS_DEBUG] Triggering hot reload")
        
        # Import reload functionality
        from kivy.factory import Factory
        from kivy.lang import Builder
        from kivy.app import App
        from kivy.clock import Clock
        import sys
        import importlib
        
        # Get current app
        app = App.get_running_app()
        if not app:
            raise RuntimeError("No running Kivy app found")
        
        # Snapshot current state
        from .hotreload_plus import hooks
        snapshot = hooks.snapshot_runtime()
        
        try:
            # Clear caches
            Factory._classes.clear()
            Builder.rulectx.clear()
            
            # Reload main module if specified
            module_name = data.get("module", app.__class__.__module__)
            if module_name in sys.modules:
                Logger.info("[WIRELESS_DEBUG] Reloading module: %s", module_name)
                importlib.reload(sys.modules[module_name])
            
            # Rebuild app
            if hasattr(app, 'build'):
                new_root = app.build()
                if new_root:
                    from kivy.core.window import Window
                    if Window and Window.children:
                        Window.remove_widget(Window.children[0])
                        Window.add_widget(new_root)
                        Logger.info("[WIRELESS_DEBUG] App rebuilt successfully")
            
            # Send confirmation back to client
            send_data({
                "type": "command_response",
                "command": "reload",
                "status": "success",
                "message": "Reload completed"
            })
            
        except Exception as reload_error:
            Logger.warning("[WIRELESS_DEBUG] Reload failed, rolling back: %s", reload_error)
            # Rollback on failure
            hooks.rollback(snapshot)
            
            send_data({
                "type": "command_response",
                "command": "reload",
                "status": "error",
                "message": f"Reload failed: {str(reload_error)}"
            })
        
    except Exception as e:
        Logger.error("[WIRELESS_DEBUG] Reload failed: %s", e)
        send_data({
            "type": "command_response", 
            "command": "reload",
            "status": "error",
            "message": str(e)
        })


async def _handle_reload_file_command(data: Dict[str, Any]) -> None:
    """Handle reload file command from client."""
    try:
        file_path = data.get("file_path")
        file_content = data.get("file_content")
        
        if not file_path or not file_content:
            raise ValueError("Missing file_path or file_content")
        
        # Handle Android file push if needed
        if platform == 'android':
            await _push_file_to_android(file_path, file_content)
        else:
            # Write file content locally
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
        
        Logger.info("[WIRELESS_DEBUG] File updated: %s", file_path)
        
        # Trigger reload
        await _handle_reload_command({"module": data.get("module")})
        
    except Exception as e:
        Logger.error("[WIRELESS_DEBUG] File reload failed: %s", e)
        send_data({
            "type": "command_response",
            "command": "reload_file", 
            "status": "error",
            "message": str(e)
        })


async def _push_file_to_android(file_path: str, file_content: str) -> None:
    """Push file content to Android device."""
    try:
        # Write to temporary local file first
        import tempfile
        import os
        from ..android_bridge import adb
        
        with tempfile.NamedTemporaryFile(mode='w', suffix=os.path.basename(file_path), delete=False) as f:
            f.write(file_content)
            temp_path = f.name
        
        try:
            # Ensure ADB is available
            adb_bin = adb.ensure_adb()
            
            # Push file to device (assuming app has write access to its directory)
            # This is a simplified approach - in practice, you'd need to know the app's data directory
            device_path = f"/sdcard/{os.path.basename(file_path)}"
            
            import subprocess
            result = subprocess.run([adb_bin, "push", temp_path, device_path], 
                                  capture_output=True, text=True, check=True)
            
            Logger.info("[WIRELESS_DEBUG] File pushed to Android: %s -> %s", file_path, device_path)
            
        finally:
            # Clean up temp file
            os.unlink(temp_path)
            
    except Exception as e:
        Logger.error("[WIRELESS_DEBUG] Failed to push file to Android: %s", e)
        raise


async def _broadcast_data() -> None:
    """Broadcast queued data to all connected clients."""
    while True:
        try:
            data = await _data_queue.get()
            if _connected_clients:
                message = json.dumps(data)
                await asyncio.gather(
                    *[client.send(message) for client in _connected_clients],
                    return_exceptions=True
                )
        except Exception as e:
            Logger.error("[WIRELESS_DEBUG] Broadcast error: %s", e)


async def _run_server(host: str, port: int) -> None:
    """Run the WebSocket server."""
    Logger.info("[WIRELESS_DEBUG] Starting WebSocket server on %s:%d", host, port)
    
    # Start broadcast task
    broadcast_task = asyncio.create_task(_broadcast_data())
    
    try:
        async with websockets.serve(_websocket_handler, host, port):
            Logger.info("[WIRELESS_DEBUG] WebSocket server running")
            await asyncio.Future()  # Run forever
    except Exception as e:
        Logger.error("[WIRELESS_DEBUG] Server error: %s", e)
    finally:
        broadcast_task.cancel()


def _server_thread_func(host: str, port: int) -> None:
    """Thread function to run the asyncio event loop."""
    global _server_task
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        _server_task = loop.create_task(_run_server(host, port))
        loop.run_until_complete(_server_task)
    except Exception as e:
        Logger.error("[WIRELESS_DEBUG] Thread error: %s", e)


def start_server(host: str = "0.0.0.0", port: int = 8765) -> str:
    """Start the wireless debug server.
    
    Returns the URL that clients should connect to.
    """
    global _server_thread, _enabled
    
    if not HAS_DEPS:
        Logger.error("[WIRELESS_DEBUG] Missing dependencies. Install: pip install 'kivy-protonox-version[wireless]'")
        return ""
    
    if _enabled:
        Logger.warning("[WIRELESS_DEBUG] Server already running")
        return f"ws://{_get_local_ip()}:{port}"
    
    _enabled = True
    
    # Start server thread
    _server_thread = threading.Thread(target=_server_thread_func, args=(host, port), daemon=True)
    _server_thread.start()
    
    # Wait a bit for server to start
    time.sleep(0.5)
    
    url = f"ws://{_get_local_ip()}:{port}"
    Logger.info("[WIRELESS_DEBUG] Server started at %s", url)
    
    # Generate and display QR code based on platform
    if platform == 'android':
        # For Android, show ADB wireless IP:port for pairing
        adb_target = f"{_get_local_ip()}:5555"
        qr_code = generate_qr(adb_target)
        Logger.info("[WIRELESS_DEBUG] Android detected. Enable ADB wireless and scan QR for IP:port, then use protonox wireless-connect --adb-wireless-ip-port %s\n%s", adb_target, qr_code)
        Logger.info("[WIRELESS_DEBUG] After ADB connect and forward, WebSocket will be at ws://localhost:%d", port)
    else:
        # For other platforms, show WebSocket URL
        qr_code = generate_qr(url)
        Logger.info("[WIRELESS_DEBUG] Scan QR code to connect:\n%s", qr_code)
    
    return url


def stop_server() -> None:
    """Stop the wireless debug server."""
    global _server_thread, _server_task, _enabled, _connected_clients
    
    if not _enabled:
        return
    
    _enabled = False
    Logger.info("[WIRELESS_DEBUG] Stopping server")
    
    # Close all client connections
    for client in _connected_clients[:]:
        try:
            asyncio.create_task(client.close())
        except Exception:
            pass
    _connected_clients.clear()
    
    # Cancel server task
    if _server_task:
        _server_task.cancel()
        _server_task = None
    
    # Wait for thread to finish
    if _server_thread and _server_thread.is_alive():
        _server_thread.join(timeout=2.0)
    
    Logger.info("[WIRELESS_DEBUG] Server stopped")


def send_data(data: Dict[str, Any]) -> None:
    """Send data to connected clients."""
    if not _enabled:
        return
    
    try:
        # Add timestamp if not present
        if "timestamp" not in data:
            data["timestamp"] = time.time()
        
        # Queue for async broadcast
        asyncio.create_task(_data_queue.put(data))
    except Exception as e:
        Logger.error("[WIRELESS_DEBUG] Failed to queue data: %s", e)


def send_log(level: str, message: str, **kwargs) -> None:
    """Send a log message to clients."""
    send_data({
        "type": "log",
        "level": level,
        "message": message,
        **kwargs
    })


def send_ui_state(state: Dict[str, Any]) -> None:
    """Send UI state information."""
    send_data({
        "type": "ui_state",
        **state
    })


def send_touch_event(event: Dict[str, Any]) -> None:
    """Send touch event data."""
    send_data({
        "type": "touch",
        **event
    })


# Integration with Kivy logger
class WirelessDebugHandler(logging.Handler):
    """Logging handler that sends logs to wireless debug clients."""
    
    def emit(self, record):
        if _enabled:
            send_log(
                level=record.levelname,
                message=record.getMessage(),
                logger=record.name,
                filename=record.filename,
                lineno=record.lineno
            )


# Auto-start if enabled via environment
if os.environ.get("PROTONOX_WIRELESS_DEBUG", "0").lower() in ("1", "true", "yes"):
    # Start server on app launch
    def _auto_start_server(*args):
        start_server()
        # Add logging handler
        handler = WirelessDebugHandler()
        Logger.addHandler(handler)
    
    Clock.schedule_once(_auto_start_server, 0)


# Kivy integration hooks
def _setup_kivy_hooks():
    """Setup hooks to send UI events to clients."""
    from kivy.core.window import Window
    from kivy.base import EventLoop
    
    def on_touch_down(touch):
        send_touch_event({
            "action": "down",
            "x": touch.x,
            "y": touch.y,
            "id": touch.id,
            "button": getattr(touch, 'button', 'touch')
        })
    
    def on_touch_move(touch):
        send_touch_event({
            "action": "move", 
            "x": touch.x,
            "y": touch.y,
            "id": touch.id
        })
    
    def on_touch_up(touch):
        send_touch_event({
            "action": "up",
            "x": touch.x,
            "y": touch.y,
            "id": touch.id
        })
    
    def send_ui_snapshot(*args):
        """Send current UI state snapshot."""
        try:
            from kivy.protonox_ext.observability import export_observability
            
            # Get root widget
            root = None
            if hasattr(EventLoop, 'window') and EventLoop.window:
                root = EventLoop.window.children[0] if EventLoop.window.children else None
            
            if root:
                # Use observability to export UI state
                payload = export_observability(root)
                send_ui_state(payload)
        except Exception as e:
            Logger.warning("[WIRELESS_DEBUG] Failed to send UI snapshot: %s", e)
    
    if _enabled:
        Window.bind(on_touch_down=on_touch_down)
        Window.bind(on_touch_move=on_touch_move) 
        Window.bind(on_touch_up=on_touch_up)
        
        # Send UI snapshots periodically
        Clock.schedule_interval(send_ui_snapshot, 1.0)  # Every second


# Setup hooks when module loads
if os.environ.get("PROTONOX_WIRELESS_DEBUG", "0").lower() in ("1", "true", "yes"):
    Clock.schedule_once(lambda *args: _setup_kivy_hooks(), 1.0)


__all__ = [
    "start_server",
    "stop_server",
    "send_data",
    "send_log",
    "send_ui_state",
    "send_touch_event",
    "generate_qr",
]
