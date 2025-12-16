from __future__ import annotations

from pathlib import Path
from typing import Dict

TEMPLATES: Dict[str, Dict[str, str]] = {
    "firebase": {
        "FIREBASE_API_KEY": "",
        "FIREBASE_PROJECT_ID": "",
        "FIREBASE_APP_ID": "",
    },
    "render": {
        "PROTOBOTS_API_BASE": "https://api.protonox.online",
    },
    "local": {
        "PROTOBOTS_API_BASE": "http://localhost:8000",
    },
}


def write_env_templates(base: Path = Path.cwd(), preset: str | None = None) -> None:
    base = base.resolve()
    env_example = base / ".env.example"
    env_local = base / ".env.local"
    env_example.parent.mkdir(parents=True, exist_ok=True)

    content = []
    if preset and preset in TEMPLATES:
        for k, v in TEMPLATES[preset].items():
            content.append(f"{k}={v}\n")
    else:
        content.append("# Add your variables here\n")

    if not env_example.exists():
        env_example.write_text("".join(content), encoding="utf-8")
    if not env_local.exists():
        env_local.write_text("".join(content), encoding="utf-8")
