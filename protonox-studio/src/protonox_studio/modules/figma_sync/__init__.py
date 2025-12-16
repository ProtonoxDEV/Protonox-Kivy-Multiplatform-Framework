"""Figma OAuth + variable/helpers for Protonox Studio.

Secrets and scopes now come from environment variables to avoid hardcoding:
- FIGMA_CLIENT_ID (required)
- FIGMA_CLIENT_SECRET (required)
- FIGMA_REDIRECT_URI (default http://localhost:4173/figma-callback)
- FIGMA_SCOPES (space or comma separated; defaults cover content, comments, dev resources, libraries, projects, webhooks, profile)
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urlencode

import requests

ROOT_DIR = Path(__file__).resolve().parents[2]
FIGMA_DIR = ROOT_DIR.parent / ".protonox" / "figma"
FIGMA_DIR.mkdir(parents=True, exist_ok=True)
TOKEN_FILE = FIGMA_DIR / "figma_token.json"
STATE_FILE = FIGMA_DIR / "figma_state.txt"


def _env(key: str, default: Optional[str] = None) -> Optional[str]:
    return os.environ.get(key) or default


def _default_scopes() -> str:
    # Keep defaults generous; allow overriding with FIGMA_SCOPES.
    return " ".join(
        [
            "file_content:read",
            "file_dev_resources:read",
            "file_dev_resources:write",
            "library_content:read",
            "team_library_content:read",
            "file_comments:read",
            "file_comments:write",
            "projects:read",
            "webhooks:read",
            "webhooks:write",
            "user:read",
        ]
    )


def _config() -> Dict[str, str]:
    client_id = _env("FIGMA_CLIENT_ID")
    client_secret = _env("FIGMA_CLIENT_SECRET")
    redirect_uri = _env("FIGMA_REDIRECT_URI", "http://localhost:4173/figma-callback")
    scopes_raw = _env("FIGMA_SCOPES", _default_scopes())
    scopes = " ".join([s for part in scopes_raw.split(",") for s in part.strip().split() if s])

    if not client_id or not client_secret:
        raise RuntimeError("Configura FIGMA_CLIENT_ID y FIGMA_CLIENT_SECRET como variables de entorno.")

    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "scopes": scopes,
    }


def get_auth_url(state: str = "protonox") -> str:
    cfg = _config()
    params = {
        "client_id": cfg["client_id"],
        "redirect_uri": cfg["redirect_uri"],
        "scope": cfg["scopes"],
        "state": state,
        "response_type": "code",
    }
    return f"https://www.figma.com/oauth?{urlencode(params)}"


def _write_state(state: str) -> None:
    STATE_FILE.write_text(state)


def _read_state() -> Optional[str]:
    return STATE_FILE.read_text().strip() if STATE_FILE.exists() else None


def exchange_code(code: str, state: Optional[str] = None) -> dict:
    cfg = _config()
    if state and state != _read_state():
        raise RuntimeError("State inválido o expirado en callback de Figma.")

    r = requests.post(
        "https://www.figma.com/api/oauth/token",
        data={
            "client_id": cfg["client_id"],
            "client_secret": cfg["client_secret"],
            "redirect_uri": cfg["redirect_uri"],
            "code": code,
            "grant_type": "authorization_code",
        },
        timeout=30,
    )
    r.raise_for_status()
    token = r.json()
    _persist_token(token)
    return token


def _persist_token(token: dict) -> None:
    expires_in = token.get("expires_in")
    if expires_in:
        token["expires_at"] = time.time() + float(expires_in) - 60  # renew 1 min early
    TOKEN_FILE.write_text(json.dumps(token, indent=2))


def _load_token() -> dict:
    if TOKEN_FILE.exists():
        try:
            return json.loads(TOKEN_FILE.read_text())
        except Exception:
            pass
    return {}


def _refresh_token(token: dict) -> dict:
    cfg = _config()
    refresh = token.get("refresh_token")
    if not refresh:
        raise RuntimeError("No hay refresh_token disponible para renovar Figma.")

    r = requests.post(
        "https://www.figma.com/api/oauth/token",
        data={
            "client_id": cfg["client_id"],
            "client_secret": cfg["client_secret"],
            "grant_type": "refresh_token",
            "refresh_token": refresh,
        },
        timeout=30,
    )
    r.raise_for_status()
    new_token = token | r.json()
    _persist_token(new_token)
    return new_token


def ensure_access_token() -> str:
    token = _load_token()
    access = token.get("access_token")
    expires_at = token.get("expires_at")

    if not access:
        raise RuntimeError("No hay token de Figma. Conectá primero.")

    if expires_at and time.time() > expires_at:
        token = _refresh_token(token)
        access = token.get("access_token")
        if not access:
            raise RuntimeError("Refresh Figma falló: falta access_token tras renovar.")

    return access


def get_headers() -> dict:
    access = ensure_access_token()
    return {"X-Figma-Token": access}


def get_user_files() -> dict:
    r = requests.get("https://api.figma.com/v1/me/files", headers=get_headers(), timeout=30)
    r.raise_for_status()
    return r.json()


def get_file_variables(file_key: str) -> dict:
    r = requests.get(
        f"https://api.figma.com/v1/files/{file_key}/variables/local",
        headers=get_headers(),
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def push_component_update(file_key: str, node_id: str, updates: dict) -> dict:
    """Push live property updates to a Figma node."""
    headers = {**get_headers(), "Content-Type": "application/json"}
    payload = {"node_id": node_id, "properties": updates}
    r = requests.patch(
        f"https://api.figma.com/v1/files/{file_key}/nodes",
        headers=headers,
        json=payload,
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def figma_status() -> dict:
    token = _load_token()
    connected = bool(token.get("access_token"))
    return {
        "connected": connected,
        "expires_at": token.get("expires_at"),
        "scopes": _env("FIGMA_SCOPES", _default_scopes()),
        "token_file": str(TOKEN_FILE),
    }


def reset_state() -> None:
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()
    if STATE_FILE.exists():
        STATE_FILE.unlink()


# Public helpers to drive auth flow
__all__ = [
    "get_auth_url",
    "exchange_code",
    "get_user_files",
    "get_file_variables",
    "push_component_update",
    "figma_status",
    "reset_state",
    "_write_state",
    "_read_state",
]
