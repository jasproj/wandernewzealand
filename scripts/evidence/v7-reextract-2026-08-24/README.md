# v7 re-extract — unversioned-writer rows + currency:"USD" rows (2026-08-24)

## Writer lineage (gate passed)
- **Finding: WNZ's v7 writer was never committed.** Commit `31cb016` ("backfill price field via FH embed
  price-preview API (v7…)") changed only `tours-data.json`; no `extract-prices-v7-api*` file exists anywhere
  in this repo's history. Tracked extractors (`extract-price-v5.js`, `enrich-tours.js`) do not emit the v7 stamp.
- Adopted by ruling: `wanderpuertorico/extract-prices-v7-api.js`, tracked in WPR at commit
  `53c0dc565dc4de12fb9441b4d77a3ddad6402d28` (2026-05-28), WPR HEAD `3ddaec27123c3955ac19db2098ce573c0c82e2b5`.
  sha256 `584e1463c2b25ae14dfd8626b77d906059d54c94a87433d4f7e23415bc95a41f` — copied **verbatim** to
  `scripts/extract-prices-v7-api.js` (hash identical).
- Field-set diff vs what `31cb016` wrote: identical. Stamp `extract-prices-v7-api`; fields
  `priceEnrichmentSource/At/Status` (statuses high|zero_price|none|error), `priceIncludesBookingFees`,
  `priceIncludesTaxes`, `currency`, `price`, `priceConfidence`, `priceLabel`, `priceBreakdown[]` with keys
  `id,singular,plural,note,priceCents,price,minPartySize`. Shortname + pk are parsed from each row's
  `bookingUrl` (no hardcoding).

## Populations (recon, all Δ0 vs claim)
- no `priceEnrichmentSource`: 344 (incl. the 2 rows hand-edited in 62f9202) · `currency:"USD"`: 156 (102 priced)
- overlap 0 → union 500; pk 489299 excluded by ruling → **499 processed**.

## Method
- The verbatim script targets `price == null` only, and every in-scope row was priced, so selection was done by
  data prep, not code change: the 499 rows were cloned to a scratch file with `price:null`, the script ran on that
  file, and results were merged back by pk in one write (D-599: pre-write bytes round-trip
  `JSON.stringify(d,null,2)+"\n"` asserted; post-write asserted).
- Live FareHarbor, `include_breakdown=yes`, $0 customer types skipped by the script (D-575).
- Date-validity instrument: `fetch-tee.js` (node `-r` preload) teed every raw API response to
  `api-responses.ndjson`; per-item `availability.start_at/end_at` summarised in `date-validity.json`.
- Pass 1 (`--batch 20`): processed 499/499 asserted. 84 errors: 80 = script's 15 s timeout on two slow operators
  (wayfaregroup, aucklandandbeyond-nz), 4 = `HTTP 400 Company with shortname airkaikoura not found`.
- Pass 2 (`--batch 4`, the 80 timeout rows only): processed 80/80, 70 high, 10 none, 0 error.
  The stale `priceEnrichmentError` left from pass 1 was removed on the 80 rows whose final status is not `error`.

## Outcome (499)
- high 442 · zero_price 8 · none 45 · error 4 (airkaikoura ×4, stamped `error`/`HTTP 400`)
- unversioned 343: high 333 / none 7 / error 3 · USD 156: high 109 / zero_price 8 / none 38 / error 1
- Assertions: row count 3121 unchanged; 2622 outside-union rows byte-identical; 489299 byte-identical;
  stampless remaining = [489299] (excluded); USD remaining = 39, each named in `merge-report.json`
  (38 `none` — item absent from API = dead/no availability, 1 `error`); currency is only rewritten when the
  API returns the item, so these keep `USD` with `price:null` and render "Price on request".

## index.html render-gate counts (rendered = status!=inactive && !bookingDead, 3112 both sides)
| predicate | pre | post | Δ |
|---|---|---|---|
| formatPrice priced (finite, >0, conf≠low) | 1927 | 2001 | +74 |
| emitPrice schema (finite, conf≠low) | 1927 | 2001 | +74 |
