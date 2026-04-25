#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CONVERT_SCRIPT="$BASE_DIR/scripts/convert.py"

log() { printf '[currency-converter] %s\n' "$*"; }
fail() { printf '[currency-converter] ERROR: %s\n' "$*" >&2; exit 1; }

log "base dir: $BASE_DIR"
command -v python3 >/dev/null 2>&1 || fail "python3 not found"
[ -f "$CONVERT_SCRIPT" ] || fail "converter script not found: $CONVERT_SCRIPT"
chmod +x "$CONVERT_SCRIPT"

log "python3: OK ($(command -v python3))"
log "converter script: OK ($CONVERT_SCRIPT)"
log "install complete"
