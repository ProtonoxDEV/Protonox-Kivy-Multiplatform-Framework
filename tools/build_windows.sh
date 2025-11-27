#!/usr/bin/env bash
set -euo pipefail

TEMPLATE_DIR="templates/protonox-app-complete"
cd "$TEMPLATE_DIR/app"
python -m pip install -r ../requirements.txt 2>/dev/null || true
pyinstaller --noconfirm --onefile main.py
