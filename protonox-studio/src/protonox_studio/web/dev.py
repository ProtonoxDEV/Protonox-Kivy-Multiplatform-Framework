from __future__ import annotations

import http.server
import importlib.resources as resources
import socketserver
import subprocess
import sys
import urllib.parse
from pathlib import Path
from typing import Optional

import requests

from protonox_studio.web.paths import protonox_dir


def detect_package_manager(base: Path) -> str:
    if (base / "pnpm-lock.yaml").exists():
        return "pnpm"
    if (base / "yarn.lock").exists():
        return "yarn"
    return "npm"


def detect_vite(base: Path) -> bool:
    for name in ["vite.config.ts", "vite.config.js", "vite.config.mjs", "vite.config.cjs"]:
        if (base / name).exists():
            return True
    return False


def run_web_dev(base: Path = Path.cwd(), port: Optional[int] = None) -> None:
    base = base.resolve()
    pm = detect_package_manager(base)
    cmd = [pm, "run", "dev"] if pm != "npm" else ["npm", "run", "dev"]
    env = None
    if port:
        env = {"PORT": str(port)}
    protonox_dir(base).mkdir(parents=True, exist_ok=True)
    print(f"[protonox] web dev → {' '.join(cmd)} (cwd={base})")
    subprocess.run(cmd, cwd=str(base), env=(env or None), check=False)


def run_web_dev_generic(target: str, overlay_port: int = 4173) -> None:
    """Start a lightweight reverse proxy that injects the Protonox overlay."""

    base_url = urllib.parse.urlparse(target)
    if base_url.scheme not in {"http", "https"}:
        raise SystemExit("target must include scheme, e.g. http://localhost:3000")

    try:
        overlay_js = resources.files("protonox_studio.web").joinpath("overlay_client.js").read_text(encoding="utf-8")
    except FileNotFoundError:
        overlay_js = "console.warn('protonox overlay missing');"

    class Proxy(http.server.BaseHTTPRequestHandler):
        upstream = base_url
        overlay_path = "/__protonox/studio-client.js"

        def log_message(self, fmt, *args):  # noqa: D401 - silence noisy proxy logging
            sys.stderr.write("[proxy] " + fmt % args + "\n")

        def _inject_overlay(self, body: bytes, headers: dict) -> bytes:
            content_type = headers.get("content-type", "")
            if "text/html" not in content_type.lower():
                return body
            marker = b"</body>"
            snippet = f'<script type="module" src="{self.overlay_path}"></script>'.encode("utf-8")
            if marker in body:
                return body.replace(marker, snippet + marker)
            return body + snippet

        def _proxy(self) -> None:
            url = urllib.parse.urljoin(self.upstream.geturl(), self.path)
            length = int(self.headers.get("content-length") or 0)
            body = self.rfile.read(length) if length else None
            headers = {
                k: v for k, v in self.headers.items() if k.lower() not in {"host", "content-length", "accept-encoding"}
            }
            try:
                resp = requests.request(
                    self.command, url, headers=headers, data=body, allow_redirects=False, timeout=10
                )
            except Exception as exc:  # noqa: BLE001 - user facing error
                self.send_error(502, f"proxy error: {exc}")
                return

            content = self._inject_overlay(resp.content, resp.headers)
            self.send_response(resp.status_code)
            for key, val in resp.headers.items():
                if key.lower() in {"content-encoding", "transfer-encoding", "content-length", "connection"}:
                    continue
                self.send_header(key, val)
            self.send_header("content-length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        def do_GET(self):  # noqa: N802 - http.server API
            if self.path == "/__protonox/health":
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"ok")
                return
            if self.path == self.overlay_path:
                self.send_response(200)
                self.send_header("content-type", "application/javascript")
                self.end_headers()
                self.wfile.write(overlay_js.encode("utf-8"))
                return
            if self.path.startswith("/__protonox/ws"):
                self.send_error(501, "WebSocket bridge not implemented in generic proxy")
                return
            self._proxy()

        def do_POST(self):  # noqa: N802 - http.server API
            self._proxy()

    with socketserver.ThreadingTCPServer(("", overlay_port), Proxy) as httpd:
        print(f"[protonox] proxy → {target} (injecting overlay on http://localhost:{overlay_port})")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("[protonox] proxy stopped")
