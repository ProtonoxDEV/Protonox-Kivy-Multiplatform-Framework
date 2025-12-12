"""Protonox Studio lightweight dev server with Figma OAuth + token sync."""
from __future__ import annotations

import json
import logging
import webbrowser
import os
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, Tuple
from urllib.parse import parse_qs, urlparse

from modules.figma_sync import (
    exchange_code,
    get_auth_url,
    get_file_variables,
    get_user_files,
    push_component_update,
)

ROOT_DIR = Path(__file__).resolve().parents[2]


class ProtonoxStudioServer(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT_DIR), **kwargs)

    # === OAuth handshake ===
    def do_GET(self):
        if self.path.startswith("/__health"):
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
            return

        if self.path.startswith("/figma-auth"):
            state = "protonox2025"  # cambiar por algo random en producción
            auth_url = get_auth_url(state)
            logging.info("Redirecting to Figma OAuth…")
            self.send_response(302)
            self.send_header("Location", auth_url)
            self.end_headers()
            # Optionally open browser when accessed locally
            try:
                webbrowser.open(auth_url)
            except Exception:
                pass
            return

        if self.path.startswith("/figma-callback"):
            query = parse_qs(urlparse(self.path).query)
            code = query.get("code", [None])[0]
            if code:
                tokens = exchange_code(code)
                (ROOT_DIR.parent / "figma_token.json").write_text(json.dumps(tokens))
                html = """
                <script>
                  alert("Figma conectado! Volvé a Protonox Studio");
                  window.close();
                </script>
                """
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(html.encode())
                logging.info("FIGMA CONECTADO! Token guardado.")
            return

        return super().do_GET()

    def _json_body(self) -> Tuple[Dict, bytes]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length > 0 else b""
        try:
            return json.loads(raw or b"{}"), raw
        except Exception:
            return {}, raw

    def do_POST(self):
        if self.path == "/__dev_tools":
            payload, raw = self._json_body()
            t = payload.get("type")

            if t == "figma-sync-tokens":
                try:
                    files = get_user_files().get("files", [])
                    if not files:
                        raise RuntimeError("No hay archivos disponibles en Figma.")

                    file_key = files[0]["key"]
                    data = get_file_variables(file_key)

                    tokens = {"color": {}, "radius": {}, "spacing": {}, "typography": {}}
                    meta = data.get("meta", {})
                    variables = meta.get("variables", {})

                    for var_id, var in variables.items():
                        values_by_mode = var.get("valuesByMode") or {}
                        if not values_by_mode:
                            continue
                        value = next(iter(values_by_mode.values()))
                        name = (
                            var.get("name", "unnamed")
                            .lower()
                            .replace("/", "-")
                            .replace(" ", "-")
                        )
                        resolved_type = var.get("resolvedType", "").lower()

                        if isinstance(value, dict) and {"r", "g", "b"}.issubset(value.keys()):
                            tokens["color"][name] = f"rgb({int(value['r']*255)}, {int(value['g']*255)}, {int(value['b']*255)})"
                        elif isinstance(value, (int, float)):
                            bucket = "radius" if "radius" in name or "corner" in name else "spacing"
                            tokens[bucket][name] = value
                        elif isinstance(value, str) or resolved_type == "string":
                            tokens["typography"][name] = value
                        else:
                            tokens.setdefault("misc", {})[name] = value

                    tokens_dir = ROOT_DIR.parent / "tokens"
                    tokens_dir.mkdir(exist_ok=True)
                    output_file = tokens_dir / "figma-tokens.json"
                    output_file.write_text(json.dumps(tokens, indent=2))
                    logging.info("FIGMA TOKENS SYNCED → %s", output_file)
                    self.send_response(HTTPStatus.OK)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "ok", "file": str(output_file)}).encode())
                    return
                except Exception as e:
                    logging.error("Figma sync falló: %s", e)
                    self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode())
                    return

            if t == "figma-push-update":
                try:
                    node_id = payload.get("node_id")
                    updates = payload.get("updates") or {}
                    file_key = payload.get("file_key")

                    if not node_id:
                        raise RuntimeError("Falta node_id para actualizar en Figma.")
                    if not updates:
                        raise RuntimeError("No hay cambios para sincronizar.")

                    if not file_key:
                        files = get_user_files().get("files", [])
                        if not files:
                            raise RuntimeError("No hay archivos disponibles en Figma.")
                        file_key = files[0]["key"]

                    result = push_component_update(file_key=file_key, node_id=node_id, updates=updates)

                    self.send_response(HTTPStatus.OK)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "pushed", "result": result}).encode())
                    logging.info("Figma push OK for node %s in %s", node_id, file_key)
                    return
                except Exception as e:
                    logging.error("Figma push falló: %s", e)
                    self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode())
                    return

        return super().do_POST()


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    port = int(os.environ.get('PORT', '4173'))

    # If FastAPI is installed and the env var USE_FASTAPI=1 is set, expose a
    # lightweight ASGI app that mirrors the same health + figma endpoints.
    # This makes it easier to run under `uvicorn` during development.
    use_fastapi = os.environ.get('USE_FASTAPI') in {'1', 'true', 'True'}
    try:
        if use_fastapi:
            from fastapi import FastAPI, Response, Request
            import uvicorn

            app = FastAPI()

            @app.get('/__health')
            def health():
                return {"status": "ok"}

            @app.get('/figma-auth')
            def figma_auth():
                state = "protonox2025"
                return {"redirect": get_auth_url(state)}

            @app.get('/figma-callback')
            def figma_callback(request: Request):
                q = dict(request.query_params)
                code = q.get('code')
                if code:
                    tokens = exchange_code(code)
                    (ROOT_DIR.parent / "figma_token.json").write_text(json.dumps(tokens))
                    return Response(content="<script>alert('Figma conectado! Volvé a Protonox Studio');window.close();</script>", media_type='text/html')
                return {"error": "missing code"}

            @app.post('/__dev_tools')
            async def dev_tools(req: Request):
                payload = await req.json()
                t = payload.get('type')
                # Reuse existing logic by calling same helpers; keep behavior minimal
                if t == 'figma-sync-tokens':
                    files = get_user_files().get('files', [])
                    if not files:
                        return Response(status_code=500, content=json.dumps({"error": "No hay archivos disponibles en Figma."}), media_type='application/json')
                    file_key = files[0]['key']
                    data = get_file_variables(file_key)
                    # ... (same token extraction as the SimpleHTTPRequestHandler path)
                    tokens = {"color": {}, "radius": {}, "spacing": {}, "typography": {}}
                    meta = data.get('meta', {})
                    variables = meta.get('variables', {})
                    for var_id, var in variables.items():
                        values_by_mode = var.get('valuesByMode') or {}
                        if not values_by_mode:
                            continue
                        value = next(iter(values_by_mode.values()))
                        name = (var.get('name', 'unnamed').lower().replace('/', '-').replace(' ', '-'))
                        resolved_type = var.get('resolvedType', '').lower()
                        if isinstance(value, dict) and {"r", "g", "b"}.issubset(value.keys()):
                            tokens['color'][name] = f"rgb({int(value['r']*255)}, {int(value['g']*255)}, {int(value['b']*255)})"
                        elif isinstance(value, (int, float)):
                            bucket = 'radius' if 'radius' in name or 'corner' in name else 'spacing'
                            tokens[bucket][name] = value
                        elif isinstance(value, str) or resolved_type == 'string':
                            tokens['typography'][name] = value
                        else:
                            tokens.setdefault('misc', {})[name] = value

                    tokens_dir = ROOT_DIR.parent / 'tokens'
                    tokens_dir.mkdir(exist_ok=True)
                    output_file = tokens_dir / 'figma-tokens.json'
                    output_file.write_text(json.dumps(tokens, indent=2))
                    return {"status": "ok", "file": str(output_file)}

            logging.info("Starting FastAPI dev app at http://127.0.0.1:%s", port)
            uvicorn.run(app, host='127.0.0.1', port=port)
            return
    except Exception:
        logging.debug('FastAPI/uvicorn not available or failed to start; falling back to SimpleHTTPServer')

    server = ThreadingHTTPServer(("127.0.0.1", port), ProtonoxStudioServer)
    logging.info("Protonox Studio dev server running at http://localhost:%s", port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("Server stopped")


if __name__ == "__main__":
    main()
