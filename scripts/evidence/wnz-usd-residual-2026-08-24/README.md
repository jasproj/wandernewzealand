# s45 — re-probe of the 39 `currency:"USD"` residual rows (2026-08-24)

## Recon (served bytes, all Δ0 vs claim)
- Live `https://wandernewzealand.com/tours-data.json` sha256 `d4bd8e0c…ea3f`, 9,188,564 B == disk at origin/main
  `952e0b038f1e709273697a240a9df57ccaf87342` (#105).
- `currency:"USD"` rows: 39 (Δ0) · all `price:null`: 39 (Δ0) · `priceEnrichmentStatus` 38 `none` / 1 `error` (Δ0).
- `v7-reextract-2026-08-24/merge-report.json#usdRemaining` vs derived set: identical both directions (Δ0).
- pk 489299 (D-612 charter-unit row, the sole stampless row) excluded; asserted byte-identical post-write.

## Method
- Writer: tracked `scripts/extract-prices-v7-api.js`, sha256 `584e1463…5a41f`, **unedited**. Writer targets
  `price==null` + FH `bookingUrl`, and the full file has 1,119 such rows, so scope was expressed as input scoping:
  the 39 rows were cloned into a scratch file (wrapper preserved), the writer ran on that file
  (`--batch 4`, tee preload `fetch-tee.js` → `api-responses.ndjson`), results merged back by pk in one write.
- Shortname/pk parsed from `bookingUrl` by the writer; no pk references more than one shortname anywhere in the file
  (enumeration check for the "items[] absence ≠ dead" rule: nothing further to enumerate).
- Pre-write round-trip `JSON.stringify(d,null,2)+"\n"` asserted equal to disk bytes; post-write asserted.
  Float-token count pre/post 14,190 / 14,190 (no int→float re-spelling).

## Outcome (39/39 processed, 23 requests, 13.5 s, 0 timeouts)
- high 0 · zero_price 0 · none 38 · error 1 (airkaikoura pk 340836: `HTTP 400 Company with shortname airkaikoura
  not found`, both attempts).
- Live `details.currency` (recorded per row in `obs-usd-residual.json`): **NZD for all 21 reachable operators
  (38 rows)**; `null` for airkaikoura. Every 200 response returned `items: []` for the requested pks.
- D-620: no row's live currency differs from NZD → 0 rows gated `priceConfidence:low`. Renderer untouched.
- D-606 / zero-tier rules: no items returned → no tiers, no FALLBACK/date echoes; `zeroOnlyDates` and
  `fallbackEchoDates` empty on every row.
- The stored `currency:"USD"` therefore remains as-is on the 39 rows (the verbatim writer only rewrites
  `currency` when the item is returned). It is contradicted by the operator-level live currency (NZD) but with
  `price:null` it has no render effect ("Price on request"). Correcting the stale stamp without an item is a
  separate ruling, not a side-effect of this probe.

## Diff
- `tours-data.json`: exactly 39 hunks, each a single `priceEnrichmentAt` line; 3,082 other rows byte-identical.
