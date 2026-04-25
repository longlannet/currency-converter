---
name: currency-converter
description: Multi-source currency conversion and exchange-rate lookup. Uses fast no-key sources such as fxapi.app and MoneyConvert for frequently updated reference rates, with Frankfurter / ECB daily reference rates available via --source ecb. Use when the task involves currency conversion, exchange rates, FX lookup, USD/CNY or other fiat pairs, or comparing fast free rates versus official ECB daily reference rates. Rates are informational, not trading-grade.
metadata:
  homepage: https://github.com/longlannet/currency-converter
  openclaw:
    emoji: "💱"
    requires:
      bins: ["python3"]
---

# Currency Converter

Use this skill for read-only currency conversion and exchange-rate lookup. It supports multiple free sources:

- `auto` / `fast` (default): try `fxapi.app`, then `MoneyConvert`, then Frankfurter / ECB as fallback.
- `fxapi`: no-key fast source, advertised 5-minute updates, direct pair endpoint.
- `moneyconvert`: no-key fast fallback, advertised 5-minute updates, USD-based all-rates endpoint.
- `ecb`: Frankfurter API backed by European Central Bank daily reference rates.

All rates are informational reference rates, not trading-grade quotes.

## When to use
Use this skill when the user wants:
- 货币换算 / 汇率转换
- 查询美元人民币、欧元美元等常见币种汇率
- 免费快速汇率（无 API key）
- ECB / 欧洲央行每日官方参考汇率
- 比较 USD、EUR、CNY、JPY、GBP、HKD 等常见币种

## Quick start
Run commands from the skill root:

```bash
bash scripts/install.sh
bash scripts/check.sh
python3 scripts/convert.py 100 USD CNY
```

## Workflow
1. Normalize currency codes to 3-letter uppercase codes such as `USD`, `EUR`, `CNY`, `JPY`, `GBP`, or `HKD`.
2. Choose the source:
   - Use default `auto` for a fast no-key answer.
   - Use `--source ecb` when the user asks for official ECB / daily reference rates.
   - Use `--source fxapi` or `--source moneyconvert` when testing a specific fast source.
3. Run `python3 scripts/convert.py <amount> <from_currency> <to_currency> [--source SOURCE]` from the skill root.
4. Report the converted amount, source, rate timestamp/date, and freshness note.
5. Make clear that free fast sources are not trading-grade, and ECB is daily reference data rather than real-time market data.

## Commands
```bash
# Install / permission check
bash scripts/install.sh

# Full health check with API smoke tests
bash scripts/check.sh

# Skip network smoke test when offline or only validating local files
RUN_SMOKE=0 bash scripts/check.sh

# Default: auto/fast source with fallback
python3 scripts/convert.py 100 USD CNY

# Explicit fast no-key sources
python3 scripts/convert.py 100 USD CNY --source fxapi
python3 scripts/convert.py 100 USD CNY --source moneyconvert

# Official daily reference source
python3 scripts/convert.py 100 USD CNY --source ecb

# Same-currency and zero-amount conversions are local
python3 scripts/convert.py 100 USD USD
python3 scripts/convert.py 0 EUR GBP
```

## Source notes
- `fxapi.app`: no API key, CORS-enabled JSON, advertised 5-minute updates. Good default for quick free lookups, but not a long-established institutional data provider.
- `MoneyConvert`: no authentication, CDN JSON API, advertised 5-minute updates, attribution/terms apply. Good fallback for fast no-key lookup.
- `Frankfurter / ECB`: no API key, official-style daily ECB reference data, strongest for accounting/reference context, but not real-time and covers fewer currencies.
- Same-currency and zero-amount conversion are handled locally without an API request.
- The skill does not perform trading, payments, account access, or financial advice.
- If setup is missing or stale, re-run `bash scripts/install.sh`.
- Keep detailed human-facing usage in `README.md`.
