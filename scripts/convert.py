#!/usr/bin/env python3
"""Convert currencies with Frankfurter API (ECB reference rates)."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

API_BASE = "https://api.frankfurter.app/latest"
USER_AGENT = "OpenClaw-Skill/currency-converter/1.0"


def usage() -> None:
    print("Usage: convert.py <amount> <from_currency> <to_currency>")
    print("Example: convert.py 100 USD CNY")


def fail(message: str, code: int = 1) -> None:
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(code)


def parse_args(argv: list[str]) -> tuple[float, str, str]:
    if len(argv) == 2 and argv[1] in {"-h", "--help"}:
        usage()
        sys.exit(0)

    if len(argv) != 4:
        usage()
        sys.exit(1)

    try:
        amount = float(argv[1])
    except ValueError:
        fail("amount must be a number")

    if amount < 0:
        fail("amount must be non-negative")

    base = argv[2].strip().upper()
    target = argv[3].strip().upper()

    if len(base) != 3 or not base.isalpha():
        fail(f"invalid source currency code: {base!r}")
    if len(target) != 3 or not target.isalpha():
        fail(f"invalid target currency code: {target!r}")

    return amount, base, target


def fetch_conversion(amount: float, base: str, target: str) -> dict:
    params = urllib.parse.urlencode({"amount": amount, "from": base, "to": target})
    url = f"{API_BASE}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        fail(f"Frankfurter API returned HTTP {exc.code}: {body or exc.reason}")
    except urllib.error.URLError as exc:
        fail(f"Frankfurter API request failed: {exc.reason}")
    except json.JSONDecodeError as exc:
        fail(f"Frankfurter API returned invalid JSON: {exc}")


def print_result(amount: float, base: str, target: str, result: float, rate_date: str, note: str | None = None) -> None:
    query_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("💰 汇率转换结果")
    print("----------------")
    print(f"{amount:g} {base} = {result:g} {target}")
    print("----------------")
    print(f"📅 汇率日期: {rate_date} (欧洲央行数据)")
    print(f"🕒 查询时间: {query_time}")
    print("📡 数据来源: Frankfurter API")
    if note:
        print(f"ℹ️ 说明: {note}")


def main() -> None:
    amount, base, target = parse_args(sys.argv)

    if base == target:
        print_result(
            amount=amount,
            base=base,
            target=target,
            result=amount,
            rate_date="N/A",
            note="same currency; converted locally without API request",
        )
        return

    data = fetch_conversion(amount, base, target)
    rate_date = data.get("date", "Unknown")
    rates = data.get("rates", {})

    if target not in rates:
        fail(f"target currency {target} not found in Frankfurter response")

    print_result(
        amount=amount,
        base=data.get("base", base),
        target=target,
        result=float(rates[target]),
        rate_date=rate_date,
    )


if __name__ == "__main__":
    main()
