# s45 — charter-unit render path + 489299 re-rule (2026-08-24)

Base origin/main `0fd59e70e7c68a858eef818214a78249afd82654`; served `tours-data.json` sha `a3fda032…` == disk (asserted).

## Recon
1. **Sibling mechanisms**
   - KWST `keywestsandbartours/app.js:143-150` `priceUnit(tour)` reads the **explicit** string
     `_unknownFields.priceUnit` and returns it or `''` — no inference. Rendered at `app.js:242-244` as
     `<small>` inside `.tour-price` after `formatPrice()`; CSS `styles.css:1032-1039`. JSON-LD (`app.js:579-585`)
     unchanged — the offer price is the row price. Copy pattern in data: `"whole boat · up to 6 people"`.
   - FST `floridasandbartours/card-format.js:203-222` `unitPhrase(tour)` prefers explicit `_unknownFields.unit`
     (enum) but **falls back to word-inference** on `priceLabel` ("charter"/"whole boat"…) at :206-212.
   - **Chosen: KWST** — purely explicit-field driven. FST's fallback is the inference defect class.
2. **WNZ today**: `app.js:177-181` `formatPrice` → `From NZ$<price>`; `app.js:196-215` `generateTourSchema`,
   `emitPrice` at :197 (`Number.isFinite(price) && priceConfidence !== 'low'`); card at :250/:276.
   489299 rendered `From NZ$1262` with an offer of 1262 NZD (priceConfidence `medium`, label `charter`) —
   a whole-vehicle rate reading like a seat price.
3. **Rows affected by the new path**: it fires only on `_unknownFields.priceUnit`; 0 rows carried it, this PR
   stamps exactly 1 (489299) → Δ0 vs expectation. Label-inference sweep finds 49 rows with charter/private-tour
   wording (listed in the PR body) — out of scope, and inference is not evidence.
4. **489299 live** (`probe-489299-live.json`): undated + 17 dates 2026-08-25..09-10, 18/18 readings
   `details.currency=NZD`, one customer type `Private Charter` 126261¢ ($1262.61), min_party_size 1, note
   "Max 4 adults or 2 adult & 2 children (All ages)". 0 zero tiers, 0 zero-only dates, 0 FALLBACK echoes;
   `availability.start_at` tracked each requested date (08-25 had no departure → 08-26 13:30; 08:00 thereafter).
   Stored 1262 / medium / "charter" vs live 1262.61 / Private Charter.

## Write
- `app.js`: `priceUnit()` ported verbatim (explicit field only); card emits `<small>` unit after the price.
  `formatPrice` and JSON-LD untouched, matching KWST.
- `styles.css`: `.tour-price small` rule ported. 0 `.tour-price … <small>` matches in tracked HTML before.
- `tours-data.json` pk 489299 only: price 1262.61, priceConfidence high, priceLabel "Private Charter",
  priceSource / priceBasis / priceTiers stamps, `_unknownFields.priceUnit = "whole vehicle · up to 4 people"`.
  Every other row byte-identical (asserted). Float tokens 14190 → 14192 (the two 1262.61 spellings; no re-spelling).
- Gate: rendered 3112; visible priced 2001 == JSON-LD offers 2001, before and after. 489299 offer: 1262.61 NZD.
- Simulated badge: `<div class="tour-price">From NZ$1262.61<small>whole vehicle · up to 4 people</small></div>`.
