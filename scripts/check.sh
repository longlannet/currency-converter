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
grep -q -- "--source" /tmp/currency-converter-help.txt || fail "help output missing --source"
log "help check: OK"

if [ "$RUN_SMOKE" = "1" ]; then
  log "running auto-source smoke test: 1 USD to CNY"
  python3 "$CONVERT_SCRIPT" 1 USD CNY >/tmp/currency-converter-auto.txt || fail "auto-source smoke test failed"
  grep -q "USD" /tmp/currency-converter-auto.txt || fail "auto-source output missing source currency"
  grep -q "CNY" /tmp/currency-converter-auto.txt || fail "auto-source output missing target currency"
  grep -q "数据来源" /tmp/currency-converter-auto.txt || fail "auto-source output missing provider"
  log "auto-source smoke test: OK"

  log "running explicit fxapi smoke test: 1 USD to CNY"
  python3 "$CONVERT_SCRIPT" 1 USD CNY --source fxapi >/tmp/currency-converter-fxapi.txt || fail "fxapi smoke test failed"
  grep -q "fxapi" /tmp/currency-converter-fxapi.txt || fail "fxapi output missing source marker"
  log "fxapi smoke test: OK"

  log "running explicit moneyconvert smoke test: 1 USD to CNY"
  python3 "$CONVERT_SCRIPT" 1 USD CNY --source moneyconvert >/tmp/currency-converter-moneyconvert.txt || fail "moneyconvert smoke test failed"
  grep -q "moneyconvert" /tmp/currency-converter-moneyconvert.txt || fail "moneyconvert output missing source marker"
  log "moneyconvert smoke test: OK"

  log "running explicit ecb smoke test: 1 EUR to USD"
  python3 "$CONVERT_SCRIPT" 1 EUR USD --source ecb >/tmp/currency-converter-ecb.txt || fail "ecb smoke test failed"
  grep -q "ECB" /tmp/currency-converter-ecb.txt || fail "ecb output missing ECB marker"
  log "ecb smoke test: OK"

  log "running local same-currency test: 1 USD to USD"
  python3 "$CONVERT_SCRIPT" 1 USD USD >/tmp/currency-converter-same.txt || fail "same-currency test failed"
  grep -q "same currency" /tmp/currency-converter-same.txt || fail "same-currency output missing local marker"
  log "same-currency test: OK"

  log "running local zero-amount test: 0 EUR to GBP"
  python3 "$CONVERT_SCRIPT" 0 EUR GBP >/tmp/currency-converter-zero.txt || fail "zero-amount test failed"
  grep -q "zero amount" /tmp/currency-converter-zero.txt || fail "zero-amount output missing local marker"
  log "zero-amount test: OK"
fi

log "check complete"
