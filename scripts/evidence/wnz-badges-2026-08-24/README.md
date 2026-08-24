# s47 — gated static badges re-derived vs high-confidence rows (2026-08-24)

Base origin/main `dbe9c45b7bc1d56b11b82ad006763b7f303d1eb5` (#109, Δ0). Served `tours-data.json` sha256
`d8fea7aa…6516` == disk at tip (curl substitution — Chrome extension disconnected). Gate fallback read from
`app.js:188-190` `formatPrice()` → `"Price on request"`.

## Census
All 66 hand-authored `class="tour-price"` badges on auckland/queenstown/rotorua (24/24/18) paired to rows by the
card's `data-tour-id` pk. 34 carry figures. Badge convention = floor of row price (s46 README). Disagreeing with a
high-confidence row under floor: **13** (auckland 4 / queenstown 8 / rotorua 1) — carried 15 → Δ−2 (the carried
4+8+1 breakdown never summed to 15). All 13 class (a) (row high-confidence, 2026-08-24 stamp); (b)/(c) 0.

## Amendment probes (standard protocol: `probe-live.py`, undated + 17 dates 2026-08-25..09-10, include_breakdown=yes,
`date=` validated by `availability.start_at` tracking the requested date on 414735)
- **414735 crystalmountain "Ultimate Experience Pass"** (`probe-414735-live.json`): 18/18 NZD, 4 customer types every
  reading — Family 11574¢ (note "2 adults aged 13+ and 2 children/Infants aged 12 and under"), Adult 2630¢ ("Aged 13+"),
  Child 3683¢, Infant 2104¢; 0 zero tiers. Family is a 2+2 bundle, not a per-person fare → the v7 row anchor (115.74
  Family) was wrong. **Re-anchored per the adult-anchor rule: price 26.30 / label Adult / high**, stamps
  priceSource·priceBasis·priceTiers·priceEnrichment{Source,At,Status} naming s47. Badge follows: 115 → 26.
- **569893 canyoningnewzealand "Aspiring XXL Full Day Canyoning Adventure"** (`probe-569893-live.json`): 18/18 NZD.
  The two "Per Person" tiers share customer_type id 508332 and differ only by departure option: 52503¢
  "10.30am - Meeting in Makarora - Self Drive" vs 63025¢ "8.30am - Queenstown Departure" (transfer included).
  Same product → floor anchors at **525.03** (row unchanged in figure; stamps added). "Private Tour - up to 6 people"
  378151¢ is a whole-group tier. Next departure is 2026-11-16 08:30 on every requested date (seasonal).
- **200995 totallytarawera**: price null / status none (v7 live probe `items:[]`) but priceConfidence `high` —
  unearned; set **low** with a priceSource stamp naming s47. Renders "Price on request" either way.

## Sweep
Every old figure (incl. the amended 115) grepped across all tracked HTML; every pk/name grepped across other files:
only hits were the badges themselves. Post-write floor census: 0 disagreements; `tours-data.json` rows changed: exactly
3 (414735, 569893, 200995), 3118 rows byte-identical, JSON round-trip `stringify(d,null,2)+"\n"` asserted pre-write.
