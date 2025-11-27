#!/usr/bin/env bash
set -euo pipefail

TEMPLATE_DIR="templates/protonox-app-complete"
cd "$TEMPLATE_DIR"
buildozer android debug
