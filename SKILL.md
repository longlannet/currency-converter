---
name: currency-converter
description: Frankfurter API / 欧洲央行 ECB 每日参考汇率查询与货币换算（非实时/非交易级汇率）。Use when the task involves reference currency conversion, daily exchange rates, FX lookup, or converting amounts between currencies such as USD, EUR, CNY, JPY, GBP, HKD, and others.
metadata:
  homepage: https://www.frankfurter.app/
  openclaw:
    emoji: "💱"
    requires:
      bins: ["python3"]
---

# Currency Converter

Use this skill for read-only currency conversion and exchange-rate lookup using Frankfurter API data sourced from the European Central Bank (ECB). These are daily reference rates, not real-time or trading-grade rates.

## When to use
Use this skill when the user wants:
- 货币换算 / 汇率转换
- 查询每日可用 ECB 参考汇率（非实时行情）
- 将金额从一种币种换成另一种币种
- 快速比较 USD、EUR、CNY、JPY、GBP、HKD 等常见币种

## Quick start
Run commands from the skill root:

```bash
bash scripts/install.sh
bash scripts/check.sh
python3 scripts/convert.py 100 USD CNY
```

## Workflow
1. Normalize currency codes to 3-letter uppercase codes such as `USD`, `EUR`, `CNY`, `JPY`, `GBP`, or `HKD`.
2. Run `python3 scripts/convert.py <amount> <from_currency> <to_currency>` from the skill root.
3. Report the source amount, converted amount, ECB rate date, and Frankfurter as the data source.
4. Make clear that the rate is an ECB daily reference rate, not a real-time market quote.
5. Mention that weekends and ECB holidays may return the latest prior business-day rate when date precision matters.

## Commands
```bash
# Install / permission check
bash scripts/install.sh

# Full health check with API smoke test
bash scripts/check.sh

# Skip network smoke test when offline or only validating local files
RUN_SMOKE=0 bash scripts/check.sh

# Convert currencies
python3 scripts/convert.py 100 USD CNY
python3 scripts/convert.py 1 EUR USD
python3 scripts/convert.py 100 USD USD
```

## Notes
- This skill is read-only and requires no API key.
- It does not perform trading, payments, account access, or financial advice.
- Frankfurter rates are ECB daily reference rates and update on ECB business days; they are not real-time or trading-grade market rates.
- Same-currency and zero-amount conversion are handled locally without an API request.
- If setup is missing or stale, re-run `bash scripts/install.sh`.
- Keep detailed human-facing usage in `README.md`.
