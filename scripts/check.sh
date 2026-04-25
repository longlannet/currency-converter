#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CONVERT_SCRIPT="$BASE_DIR/scripts/convert.py"
RUN_SMOKE="${RUN_SMOKE:-1}"

log() { printf '[currency-converter] %s\n' "$*"; }
fail() { printf '[currency-converter] ERROR: %s\n' "$*" >&2; exit 1; }

log "base dir: $BASE_DIR"
command -v python3 >/dev/null 2>&1 || fail "python3 not found"
log "python3: OK ($(command -v python3))"

[ -f "$CONVERT_SCRIPT" ] || fail "converter script not found: $CONVERT_SCRIPT"
[ -x "$CONVERT_SCRIPT" ] || chmod +x "$CONVERT_SCRIPT"
log "converter script: OK ($CONVERT_SCRIPT)"

log "checking help output"
python3 "$CONVERT_SCRIPT" --help >/tmp/currency-converter-help.txt || fail "help check failed"
log "help check: OK"

if [ "$RUN_SMOKE" = "1" ]; then
  log "running smoke test: 1 EUR to USD"
  python3 "$CONVERT_SCRIPT" 1 EUR USD >/tmp/currency-converter-smoke.txt || fail "smoke test failed"
  grep -q "EUR" /tmp/currency-converter-smoke.txt || fail "smoke output missing source currency"
  grep -q "USD" /tmp/currency-converter-smoke.txt || fail "smoke output missing target currency"
  log "smoke test: OK"

  log "running local same-currency test: 1 USD to USD"
  python3 "$CONVERT_SCRIPT" 1 USD USD >/tmp/currency-converter-same.txt || fail "same-currency test failed"
  grep -q "same currency" /tmp/currency-converter-same.txt || fail "same-currency output missing local marker"
  log "same-currency test: OK"
fi

log "check complete"
