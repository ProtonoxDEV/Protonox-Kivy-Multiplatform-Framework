"""
Wireless debugging client for Protonox Studio.

Connects to Kivy apps running wireless debug servers and receives real-time
data streams (logs, UI state, touch events, etc.).
"""

from __future__ import annotations

import asyncio
import json
import logging
import threading
from typing import Any, Callable, Dict, Optional

try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False
    websockets = None

from .engine import Viewport


class WirelessDebugClient:
    """Client for connecting to wireless debug servers."""
    
    def __init__(self):
        self.websocket = None
        self.connected = False
        self.url = ""
        self._thread: Optional[threading.Thread] = None
        self._loop: "Optional[asyncio.AbstractEventLoop]" = None
        self._task: "Optional[asyncio.Task]" = None
        self._callbacks: Dict[str, list] = {}
        
    def on(self, event_type: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Register a callback for a specific event type."""
        if event_type not in self._callbacks:
            self._callbacks[event_type] = []
        self._callbacks[event_type].append(callback)
    
    def off(self, event_type: str, callback: Optional[Callable] = None) -> None:
        """Remove a callback for an event type."""
        if event_type in self._callbacks:
            if callback:
                self._callbacks[event_type].remove(callback)
            else:
                self._callbacks[event_type].clear()
    
    def _emit(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit an event to registered callbacks."""
        if event_type in self._callbacks:
            for callback in self._callbacks[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    logging.error(f"Callback error for {event_type}: {e}")
    
    async def _connect_and_listen(self, url: str) -> None:
        """Connect to the WebSocket and listen for messages."""
        try:
            async with websockets.connect(url) as websocket:
                self.websocket = websocket
                self.connected = True
                self.url = url
                logging.info(f"Connected to wireless debug server: {url}")
                
                self._emit("connected", {"url": url})
                
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        event_type = data.get("type", "unknown")
                        self._emit(event_type, data)
                        self._emit("message", data)
                    except json.JSONDecodeError:
                        logging.warning(f"Invalid JSON received: {message}")
                        
        except Exception as e:
            logging.error(f"WebSocket connection error: {e}")
            self._emit("error", {"error": str(e)})
        finally:
            self.connected = False
            self.websocket = None
            self._emit("disconnected", {"url": url})
    
    def _run_client(self, url: str) -> None:
        """Run the client in a separate thread."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._task = self._loop.create_task(self._connect_and_listen(url))
        self._loop.run_until_complete(self._task)
    
    def connect(self, url: str) -> bool:
        """Connect to a wireless debug server."""
        if not HAS_WEBSOCKETS:
            logging.error("websockets library not installed. Install with: pip install websockets")
            return False
        
        if self.connected:
            self.disconnect()
        
        self._thread = threading.Thread(target=self._run_client, args=(url,), daemon=True)
        self._thread.start()
        
        # Wait a bit for connection
        import time
        time.sleep(0.5)
        
        return self.connected
    
    def disconnect(self) -> None:
        """Disconnect from the server."""
        if self._task and not self._task.done():
            self._task.cancel()
        
        if self._loop:
            self._loop.stop()
        
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        
        self.connected = False
        self.websocket = None
        self.url = ""
    
    async def _send_message(self, data: Dict[str, Any]) -> None:
        """Send a message to the server."""
        if self.websocket and self.connected:
            try:
                await self.websocket.send(json.dumps(data))
            except Exception as e:
                logging.error(f"Failed to send message: {e}")
    
    def send_command(self, command: str, **kwargs) -> None:
        """Send a command to the server."""
        if not self.connected or not self._loop:
            return
        
        data = {"type": "command", "command": command, **kwargs}
        asyncio.run_coroutine_threadsafe(self._send_message(data), self._loop)
    
    def reload_app(self, module: str = None) -> None:
        """Trigger a reload of the remote app."""
        self.send_command("reload", module=module)
    
    def reload_file(self, file_path: str, file_content: str) -> None:
        """Reload a specific file on the remote app."""
        self.send_command("reload_file", file_path=file_path, file_content=file_content)


# Global client instance
_client = WirelessDebugClient()


def get_client() -> WirelessDebugClient:
    """Get the global wireless debug client."""
    return _client


def connect_to_device(url: str) -> bool:
    """Connect to a device running wireless debug."""
    return _client.connect(url)


def disconnect_from_device() -> None:
    """Disconnect from the current device."""
    _client.disconnect()


def is_connected() -> bool:
    """Check if connected to a device."""
    return _client.connected


def get_connected_url() -> str:
    """Get the URL of the connected device."""
    return _client.url


def send_command_to_device(command: str, **kwargs) -> None:
    """Send a command to the connected device."""
    _client.send_command(command, **kwargs)


def reload_remote_app(module: str = None) -> None:
    """Trigger a reload of the remote app."""
    _client.reload_app(module)


def reload_remote_file(file_path: str, file_content: str) -> None:
    """Reload a specific file on the remote app."""
    _client.reload_file(file_path, file_content)


def on_device_event(event_type: str, callback: Callable[[Dict[str, Any]], None]) -> None:
    """Register a callback for device events."""
    _client.on(event_type, callback)


def off_device_event(event_type: str, callback: Optional[Callable] = None) -> None:
    """Remove a callback for device events."""
    _client.off(event_type, callback)