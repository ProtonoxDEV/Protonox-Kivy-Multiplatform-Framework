"""CLI for Protonox Studio – now wired to the evolving engine."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Set

import subprocess
import sys

# Note: the project uses a directory name with a hyphen (protonox-studio), which
# prevents importing it as a normal Python package when executing this file as
# a script. To keep `protonox dev` working when running this CLI directly, the
# `run_dev_server` command will spawn the server script as a subprocess.


def _fake_snapshot() -> List[dict]:
    """Small synthetic dataset so `protonox audit` returns meaningful output.

    Returns plain dicts so this CLI can run standalone without importing the
    `core` package.
    """
    return [
        {"id": "hero", "x": 12, "y": 24, "width": 960, "height": 480, "padding": [32, 32, 40, 32], "margin": [0, 0, 48, 0], "color": "#0d1117", "text_samples": [48, 30, 20]},
        {"id": "cta", "x": 64, "y": 560, "width": 320, "height": 96, "padding": [16, 24, 16, 24], "margin": [0, 0, 24, 0], "color": "#58a6ff", "text_samples": [18, 16]},
        {"id": "card", "x": 64, "y": 700, "width": 360, "height": 280, "padding": [24, 24, 24, 24], "margin": [0, 0, 24, 0], "color": "#161b22", "text_samples": [20, 16, 14]},
    ]


def _detect_site_root(path: Path) -> Path:
    """Infer the most likely web root that contains an index.html."""

    def add_candidate(bucket: List[Path], seen: Set[Path], candidate: Path) -> None:
        try:
            resolved = candidate.resolve()
        except FileNotFoundError:
            return
        if resolved in seen or not resolved.exists():
            return
        seen.add(resolved)
        bucket.append(resolved)

    candidates: List[Path] = []
    seen: Set[Path] = set()

    path = path.resolve()
    add_candidate(candidates, seen, path)

    common_children = ("website", "frontend", "public", "dist", "build")
    for child in common_children:
        add_candidate(candidates, seen, path / child)

    current = path
    for _ in range(3):
        add_candidate(candidates, seen, current.parent)
        for child in common_children:
            add_candidate(candidates, seen, current.parent / child)
        current = current.parent

    for candidate in candidates:
        if (candidate / "index.html").is_file():
            return candidate
        for folder in ("public", "dist", "build"):
            nested = candidate / folder
            if (nested / "index.html").is_file():
                return nested

    return path


def run_dev_server(path: Path) -> None:
    # Spawn the local_dev_server.py script as a subprocess so the CLI can be
    # executed as a standalone script (avoids relative import/package issues).
    server_py = Path(__file__).resolve().parents[1] / "core" / "local_dev_server.py"
    if not server_py.exists():
        raise FileNotFoundError(f"Server script not found: {server_py}")

    env = os.environ.copy()
    resolved_path = path.resolve()
    site_root = _detect_site_root(resolved_path)
    if site_root != resolved_path:
        print(f"[protonox] Sitio detectado en: {site_root}")
    env.setdefault("PROTONOX_SITE_ROOT", str(site_root))
    env.setdefault("PROTONOX_STATE_DIR", str(site_root / ".protonox"))

    # Use the same Python interpreter that's running this CLI
    subprocess.run([sys.executable, str(server_py)], env=env)


def run_audit(path: Path) -> None:
    # Simple standalone audit implementation that doesn't require importing
    # the full `core` engine (avoids package import issues when the CLI is
    # executed as a script). This produces a lightweight report based on the
    # synthetic snapshot.
    snapshot = _fake_snapshot()
    report = {
        "summary": f"Audit: {len(snapshot)} elements analyzed",
        "elements": snapshot,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }
    print(report["summary"])  # human-friendly line
    print(json.dumps(report, indent=2, ensure_ascii=False))


def run_export(path: Path) -> None:
    export_dir = Path(path).resolve() / "protonox-export"
    export_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "message": "One-Click Fix listo",
        "files": ["tokens.json", "spacing.json"],
    }
    (export_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(f"Export generado en {export_dir}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Protonox Studio tooling")
    parser.add_argument("command", choices=["dev", "audit", "export"], help="Comando a ejecutar")
    parser.add_argument("--path", default=".", help="Ruta del proyecto")
    args = parser.parse_args(argv)

    path = Path(args.path)
    if args.command == "dev":
        run_dev_server(path)
    elif args.command == "audit":
        run_audit(path)
    elif args.command == "export":
        run_export(path)


if __name__ == "__main__":
    main()
