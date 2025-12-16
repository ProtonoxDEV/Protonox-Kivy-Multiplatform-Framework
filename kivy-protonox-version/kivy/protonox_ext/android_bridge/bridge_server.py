"""Lightweight desktop-side bridge server for Android dev loops (opt-in).

The server accepts JSON payloads from a cooperating Android client (future
Protonox companion) and exposes queued commands for the device to pull. This is
intentionally minimal and avoids extra dependencies so it can run inside a
thread during development.
"""
from __future__ import annotations

import json
import queue
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict, Optional

from kivy.logger import Logger

try:  # pragma: no cover - optional
    from .adb import ensure_adb
except Exception:  # pragma: no cover - avoid hard fail
    ensure_adb = None


class _BridgeHandler(BaseHTTPRequestHandler):
    inbox: "queue.Queue[Dict]" = queue.Queue()
    outbox: "queue.Queue[Dict]" = queue.Queue()
    max_payload: int = 5 * 1024 * 1024

    def _write_json(self, payload: Dict):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):  # noqa: N802 - handler signature
        length = int(self.headers.get("Content-Length", "0"))
        if length > self.max_payload:
            self.send_error(413, "Payload too large")
            return
        body = self.rfile.read(length)
        try:
            payload = json.loads(body.decode("utf-8"))
            self.__class__.inbox.put(payload)
            Logger.debug("[ADB BRIDGE] received payload: %s", payload)
            self._write_json({"status": "ok"})
        except Exception as exc:  # pragma: no cover - defensive
            Logger.warning("[ADB BRIDGE] invalid payload: %s", exc)
            self.send_error(400, "Invalid JSON")

    def do_GET(self):  # noqa: N802 - handler signature
        if self.path.startswith("/commands"):
            commands = []
            while not self.__class__.outbox.empty():
                try:
                    commands.append(self.__class__.outbox.get_nowait())
                except queue.Empty:
                    break
            self._write_json({"commands": commands})
        elif self.path.startswith("/health"):
            self._write_json({"status": "ok"})
        else:
            self.send_error(404, "Not found")

    def log_message(self, format, *args):  # pragma: no cover - silence
        Logger.debug("[ADB BRIDGE] " + format % args)


class BridgeServer:
    """Manage a background HTTP bridge for Android↔desktop coordination."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8765):
        self.host = host
        self.port = port
        self._thread: Optional[threading.Thread] = None
        self._server: Optional[HTTPServer] = None

    @property
    def inbox(self) -> "queue.Queue[Dict]":
        return _BridgeHandler.inbox

    @property
    def outbox(self) -> "queue.Queue[Dict]":
        return _BridgeHandler.outbox

    def start(self) -> None:
        if self._server:
            return
        self._server = HTTPServer((self.host, self.port), _BridgeHandler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        Logger.info("[ADB BRIDGE] bridge server listening on %s:%s", self.host, self.port)

    def stop(self) -> None:
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)
        self._thread = None

    def queue_command(self, command: Dict) -> None:
        """Queue a command for the Android client to pull."""
        self.outbox.put(command)

    def drain_events(self) -> list:
        """Return and clear all pending events posted by the Android client."""
        events = []
        while not self.inbox.empty():
            try:
                events.append(self.inbox.get_nowait())
            except queue.Empty:
                break
        return events


__all__ = ["BridgeServer"]
