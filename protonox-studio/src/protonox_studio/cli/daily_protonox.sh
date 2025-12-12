#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

TARGET_PATH=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --path)
            TARGET_PATH="$2"
            shift 2
            ;;
        --python)
            PYTHON_BIN="$2"
            shift 2
            ;;
        *)
            # allow positional path without flag
            if [[ -z "$TARGET_PATH" ]]; then
                TARGET_PATH="$1"
                shift
            else
                break
            fi
            ;;
    esac
done

if [[ -z "$TARGET_PATH" ]]; then
    TARGET_PATH="$PWD"
fi

TARGET_PATH="$(cd "$TARGET_PATH" && pwd)"

# Determine requirements file (only present in repo checkout)
REQUIREMENTS_FILE=""
for candidate in \
    "$SCRIPT_DIR/../../../requirements.txt" \
    "$SCRIPT_DIR/../../requirements.txt" \
    "$SCRIPT_DIR/../requirements.txt"
do
    if [[ -z "$REQUIREMENTS_FILE" && -f "$candidate" ]]; then
        REQUIREMENTS_FILE="$candidate"
    fi
done

if [[ -n "$REQUIREMENTS_FILE" ]]; then
    upgrade_args=(-m pip install --upgrade pip)
    install_args=(-m pip install -r "$REQUIREMENTS_FILE")

    if ! "$PYTHON_BIN" "${upgrade_args[@]}" >/dev/null 2>&1; then
        upgrade_args+=(--break-system-packages)
        "$PYTHON_BIN" "${upgrade_args[@]}" >/dev/null 2>&1 || true
    fi

    if ! "$PYTHON_BIN" "${install_args[@]}"; then
        install_args+=(--break-system-packages)
        "$PYTHON_BIN" "${install_args[@]}"
    fi
fi

CLI_SCRIPT="$SCRIPT_DIR/protonox.py"

STATE_DIR="${PROTONOX_STATE_DIR:-$TARGET_PATH/.protonox}"
LOG_DIR="$STATE_DIR/logs"

mkdir -p "$LOG_DIR" "$TARGET_PATH/protonox-export" "$TARGET_PATH/dev-reports"

"$PYTHON_BIN" "$CLI_SCRIPT" audit --path "$TARGET_PATH" | tee "$LOG_DIR/audit.log"
"$PYTHON_BIN" "$CLI_SCRIPT" export --path "$TARGET_PATH" | tee "$LOG_DIR/export.log"
