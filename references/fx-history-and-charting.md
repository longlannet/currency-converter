# Historical FX and chart verification

Cleaned oc2 procedural snapshot; no current rate or endpoint was queried during migration. Preserve the main currency-converter skill's existing spot-source policy; this reference only adds historical analysis.

## Quote and source conventions

- Historical Frankfurter route observed in the source: `https://api.frankfurter.app/YYYY-MM-DD..YYYY-MM-DD?from=JPY&to=CNY,USD`. Verify the current service/API documentation, supported currencies, date bounds and actual response before relying on this old endpoint.
- Distinguish an ECB reference observation from a retail bank, cash, card or remittance quote with spreads/fees. A reference history is not a real-time executable price.
- For a Chinese-language generic yen comparison, use **CNY per 100 JPY** and state that lower means weaker yen against RMB. Where useful, add **USD/JPY**, explicitly defined as **JPY per 1 USD**; higher means weaker yen against USD. Never label USD/JPY as “美元/日元” without defining the units.
- If an API returns CNY and USD per JPY, calculate `CNY_per_100_JPY = CNY_per_JPY * 100` and `JPY_per_USD = 1 / USD_per_JPY` in code. Reject missing, non-finite or non-positive rate inputs before inversion.

## Data and analysis checks

1. Save the fetched series and provenance. Verify currency direction, units, returned observation dates, time conventions and any pagination/limits.
2. Filter prior-period carry-in rows; sort and deduplicate observations. Do not fill weekends/holidays silently. Label the latest available reference/business day, not the retrieval date as the rate date.
3. Compute first/latest, highs/lows with dates and percentage changes in code, with an explicit tie rule. Do not confuse yen-strength percentage with the percentage move of its inverse quote.
4. Separate the requested recent interval from year-to-date performance. Avoid saying “crashing now” from an earlier fall if recent observations show a rebound.
5. For inconsistent sources, compare observation time, base currency and quote type before treating a difference as an error.

## Actual chart deliverable

Render a real image or supported document artifact when requested. Include explicit units/direction, date ticks, source, latest observation date, range and readable annotations. Reopen it and visually inspect clipping, source text, overlays, labels and the opposite direction of the two panels. If image inspection is unavailable, disclose that rather than claiming visual QA.

A safe local SVG/HTML rendering path can substitute for an unavailable plotting package, but verify the output and obey existing browser sandbox/CDP isolation. No source endpoint, credentials, browser configuration or rate value is migrated as runtime state.
