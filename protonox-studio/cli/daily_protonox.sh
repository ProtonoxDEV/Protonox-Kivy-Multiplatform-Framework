#!/usr/bin/env bash
# Wrapper script maintained for backward compatibility. Delegates to the packaged CLI.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_SCRIPT="$SCRIPT_DIR/../src/protonox_studio/cli/daily_protonox.sh"
exec "$PACKAGE_SCRIPT" "$@"
