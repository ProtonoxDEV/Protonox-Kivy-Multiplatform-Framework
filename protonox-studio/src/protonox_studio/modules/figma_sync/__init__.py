"""Figma OAuth + variable fetching helpers for Protonox Studio.

These helpers intentionally keep the OAuth secret in-code for now to mirror the
requested demo flow. In production, move them to environment variables or a
secure secret store.
"""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlencode

import requests

CLIENT_ID = "JOLQ3th1dFsARai8eQx3l6"
CLIENT_SECRET = "OoCL5954DPl0CMQMIwGjs2Mijl8U6m"
REDIRECT_URI = "http://localhost:4173/figma-callback"


def get_auth_url(state: str = "protonox") -> str:
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "file_content:read,file_dev_resources:read,file_dev_resources:write,library_content:read,team_library_content:read",
        "state": state,
        "response_type": "code",
    }
    return f"https://www.figma.com/oauth?{urlencode(params)}"


def exchange_code(code: str) -> dict:
    r = requests.post(
        "https://www.figma.com/api/oauth/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "code": code,
            "grant_type": "authorization_code",
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def get_headers() -> dict:
    token_file = Path(__file__).parents[2] / "figma_token.json"
    if not token_file.exists():
        raise RuntimeError("No hay token de Figma. Conectá primero.")
    token = json.loads(token_file.read_text()).get("access_token")
    if not token:
        raise RuntimeError("Token de Figma inválido o faltante.")
    return {"X-Figma-Token": token}


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
    """
    Push live property updates to a Figma node.

    updates = {
        "width": 420,
        "height": 280,
        "fills": [{"type": "SOLID", "color": {"r": 0.1, "g": 0.7, "b": 0.9}}],
        "cornerRadius": 16,
    }
    """

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
