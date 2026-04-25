#!/usr/bin/env python3
"""Convert currencies with multiple free exchange-rate sources."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Any

ECB_API_BASE = "https://api.frankfurter.app/latest"
FXAPI_PAIR_BASE = "https://fxapi.app/api"
MONEYCONVERT_LATEST = "https://cdn.moneyconvert.net/api/latest.json"
USER_AGENT = "OpenClaw-Skill/currency-converter/1.1"

SOURCE_CHOICES = ("auto", "fast", "fxapi", "moneyconvert", "ecb")


class ConversionError(Exception):
    """Raised when a conversion source cannot produce a result."""


class RateResult(dict):
    """Typed-ish dict holder for conversion result data."""


def fail(message: str, code: int = 1) -> None:
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(code)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="convert.py",
        description="Convert currencies using free exchange-rate sources.",
    )
    parser.add_argument("amount", type=float, help="Amount to convert, non-negative")
    parser.add_argument("from_currency", help="Source currency code, e.g. USD")
    parser.add_argument("to_currency", help="Target currency code, e.g. CNY")
    parser.add_argument(
        "--source",
        choices=SOURCE_CHOICES,
        default="auto",
        help=(
            "Rate source: auto/fast tries fxapi.app then MoneyConvert then ECB; "
            "fxapi and moneyconvert are no-key fast sources; ecb uses Frankfurter/ECB daily reference rates. "
            "Default: auto"
        ),
    )
    args = parser.parse_args(argv[1:])

    if args.amount < 0:
        fail("amount must be non-negative")

    args.from_currency = normalize_code(args.from_currency, "source")
    args.to_currency = normalize_code(args.to_currency, "target")
    return args


def normalize_code(value: str, label: str) -> str:
    code = value.strip().upper()
    if len(code) != 3 or not code.isalpha():
        fail(f"invalid {label} currency code: {code!r}")
    return code


def fetch_json(url: str) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise ConversionError(f"HTTP {exc.code}: {body or exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise ConversionError(f"request failed: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise ConversionError(f"invalid JSON: {exc}") from exc


def convert_ecb(amount: float, base: str, target: str) -> RateResult:
    params = urllib.parse.urlencode({"amount": amount, "from": base, "to": target})
    data = fetch_json(f"{ECB_API_BASE}?{params}")
    rates = data.get("rates", {})
    if target not in rates:
        raise ConversionError(f"target currency {target} not found in Frankfurter response")
    result = float(rates[target])
    return RateResult(
        result=result,
        base=data.get("base", base),
        target=target,
        provider="Frankfurter API / European Central Bank (ECB)",
        source="ecb",
        rate_time=data.get("date", "Unknown"),
        freshness="ECB daily reference rate; not real-time or trading-grade",
        rate=result / amount,
    )


def convert_fxapi(amount: float, base: str, target: str) -> RateResult:
    url = f"{FXAPI_PAIR_BASE}/{base.lower()}/{target.lower()}.json"
    data = fetch_json(url)
    rate = data.get("rate")
    if rate is None:
        raise ConversionError("fxapi.app response missing rate")
    response_base = str(data.get("base", base)).upper()
    response_target = str(data.get("target", target)).upper()
    if response_base != base or response_target != target:
        raise ConversionError(f"fxapi.app response pair mismatch: {response_base}/{response_target}")
    return RateResult(
        result=amount * float(rate),
        base=base,
        target=target,
        provider="fxapi.app",
        source="fxapi",
        rate_time=data.get("timestamp", "Unknown"),
        freshness="free no-key source; advertised 5-minute updates; not trading-grade",
        rate=float(rate),
    )


def convert_moneyconvert(amount: float, base: str, target: str) -> RateResult:
    data = fetch_json(MONEYCONVERT_LATEST)
    rates = data.get("rates", {})
    response_base = str(data.get("base", "USD")).upper()
    if response_base != "USD":
        raise ConversionError(f"MoneyConvert base changed unexpectedly: {response_base}")
    if base not in rates and base != "USD":
        raise ConversionError(f"source currency {base} not found in MoneyConvert response")
    if target not in rates and target != "USD":
        raise ConversionError(f"target currency {target} not found in MoneyConvert response")

    base_per_usd = 1.0 if base == "USD" else float(rates[base])
    target_per_usd = 1.0 if target == "USD" else float(rates[target])
    rate = target_per_usd / base_per_usd
    return RateResult(
        result=amount * rate,
        base=base,
        target=target,
        provider="MoneyConvert / CDN JSON API",
        source="moneyconvert",
        rate_time=data.get("ts", "Unknown"),
        freshness="free no-key source; advertised 5-minute updates; not trading-grade",
        rate=rate,
    )


def convert_with_source(amount: float, base: str, target: str, source: str) -> RateResult:
    if base == target:
        return RateResult(
            result=amount,
            base=base,
            target=target,
            provider="local",
            source="local",
            rate_time="N/A",
            freshness="same currency; converted locally without API request",
            rate=1.0,
        )

    if amount == 0:
        return RateResult(
            result=0.0,
            base=base,
            target=target,
            provider="local",
            source="local",
            rate_time="N/A",
            freshness="zero amount; converted locally without API request",
            rate=0.0,
        )

    if source in {"auto", "fast"}:
        errors: list[str] = []
        for name, fn in (
            ("fxapi", convert_fxapi),
            ("moneyconvert", convert_moneyconvert),
            ("ecb", convert_ecb),
        ):
            try:
                result = fn(amount, base, target)
                result["requested_source"] = source
                if errors:
                    result["fallback_note"] = "; ".join(errors)
                return result
            except ConversionError as exc:
                errors.append(f"{name}: {exc}")
        raise ConversionError("all sources failed: " + "; ".join(errors))

    if source == "fxapi":
        return convert_fxapi(amount, base, target)
    if source == "moneyconvert":
        return convert_moneyconvert(amount, base, target)
    if source == "ecb":
        return convert_ecb(amount, base, target)
    raise ConversionError(f"unsupported source: {source}")


def print_result(amount: float, base: str, target: str, data: RateResult) -> None:
    query_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = float(data["result"])

    print("💰 汇率转换结果")
    print("----------------")
    print(f"{amount:g} {base} = {result:g} {target}")
    if "rate" in data and base != target and amount not in {0, 1}:
        print(f"1 {base} = {float(data['rate']):g} {target}")
    print("----------------")
    print(f"📅 汇率时间: {data.get('rate_time', 'Unknown')}")
    print(f"🕒 查询时间: {query_time}")
    print(f"📡 数据来源: {data.get('provider', 'Unknown')}")
    print(f"🔎 来源模式: {data.get('source', 'Unknown')}")
    print(f"ℹ️ 说明: {data.get('freshness', 'reference rate; not trading-grade')}")
    if data.get("fallback_note"):
        print(f"↩️ 备用源: {data['fallback_note']}")


def main() -> None:
    args = parse_args(sys.argv)
    try:
        data = convert_with_source(
            amount=args.amount,
            base=args.from_currency,
            target=args.to_currency,
            source=args.source,
        )
    except ConversionError as exc:
        fail(str(exc))
    print_result(args.amount, args.from_currency, args.to_currency, data)


if __name__ == "__main__":
    main()
