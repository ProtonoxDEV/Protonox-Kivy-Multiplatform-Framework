"""Convenience launcher for Protonox Kivy dev mode.

Usage:
    python -m protonox_dev --app main.py [--android] [--port 4173]

Sets PROTONOX_DEV=1, auto-detects export dir, and launches the target app.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(description="Protonox Kivy dev helper")
    parser.add_argument("--app", required=True, help="Python entrypoint to run (e.g., main.py)")
    parser.add_argument("--android", action="store_true", help="Force Android-friendly polling mode")
    parser.add_argument("--port", type=int, default=None, help="Optional port to hint Studio dev server")
    parser.add_argument("--socket", help="Socket endpoint host:port to receive reload events")
    parser.add_argument("--audit-exports", action="store_true", help="Run app in export audit mode (visual checks)")
    args = parser.parse_args(argv)

    env = os.environ.copy()
    env["PROTONOX_DEV"] = "1"
    export_dir = Path(env.get("PROTONOX_EXPORT_DIR", "protobots/protonox_export"))
    if export_dir.exists():
        env["PROTONOX_EXPORT_DIR"] = str(export_dir.resolve())
    if args.android:
        env.setdefault("PROTONOX_ANDROID_POLLING", "1")
    if args.port:
        env.setdefault("PROTONOX_STUDIO_PORT", str(args.port))
    if args.socket:
        env.setdefault("PROTONOX_EXPORT_SOCKET", args.socket)
    if args.audit_exports:
        env.setdefault("PROTONOX_AUDIT_EXPORTS", "1")

    print("[protonox-dev] hotreload ON")
    print(f"[protonox-dev] export bridge {'ON' if export_dir.exists() else 'OFF'} ({export_dir})")
    print(f"[protonox-dev] socket bridge {'ON' if args.socket else 'OFF'}")
    print(f"[protonox-dev] running {args.app}")

    cmd = [sys.executable, args.app]
    subprocess.run(cmd, env=env, check=False)


if __name__ == "__main__":
    main()
