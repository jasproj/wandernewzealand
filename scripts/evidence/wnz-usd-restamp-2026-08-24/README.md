# s45 — stamps-only currency correction on the USD-residual rows (2026-08-24)

- Base: origin/main `d8d68acb86976bef230eddde1cbe34301035c9c8`; served `tours-data.json` sha `b4dba09a…` == disk (asserted).
- Population re-derived from served bytes: 39 `currency:"USD"` rows (Δ0), all `price:null`, all present in
  `../wnz-usd-residual-2026-08-24/obs-usd-residual.json` (both directions).
- Partition by that task-1 evidence: **38** rows whose live operator `details.currency == "NZD"`, **1** row
  (pk 340836, airkaikoura) whose live currency is `null` (HTTP 400, unreachable) — skipped.
- Write (38 rows only): `currency` `"USD"` → `"NZD"` + `currencyProvenance` stamp naming this pass, the evidence
  file, the basis, the shortname and the prior value. **No price field touched on any row (D-618).**
- Asserted: exactly 38 rows differ; changed fields = `currency` ×38, `currencyProvenance` ×38 only; pk 340836 and
  pk 489299 byte-identical; float-token count unchanged; `JSON.stringify(d,null,2)+"\n"` round-trip pre and post.
- **No new FareHarbor calls** — this pass runs entirely off task-1's tracked evidence.
- Render effect: none — all 38 remain `price:null` → `formatPrice` fallback "Price on request".
