# s46 — NZ$ prose literals re-derived from zero (2026-08-24)

Base origin/main `833a9b620021fee58588b2f10cb24c56ffc4077b` (== local main, no delta).
Served `tours-data.json` sha256 `d8fea7aa8da3571be56dc2c024e7d1ba1a4abc94b6a083e36d5002f76ab76516` == disk at tip (asserted, curl no-cache).
Chrome extension disconnected — served bytes via curl (labelled substitution).

## Recon
- Regex `NZ\$\s?[\d,]+ | NZD\s?[\d,.]*\d | (?<![A-Za-z])\$[\d,]+` over all 37 tracked `*.html` (body, headings, FAQ,
  meta/og, JSON-LD, inline card descriptions).
- Excluded: renderer-emitted badges (none exist in tracked HTML — app.js emits them) and the hand-authored static
  city-page `class="tour-price"` divs: **66** exist (auckland 24 / queenstown 24 / rotorua 18), 34 carrying figures
  — the carried "73" was recall, measured 66.
- **Prose literal count: 122** (carried figure 92 → delta **+30**). Table: `table.md` / `literals.json` (86 line-rows).
  Classes: PAIRED 62 rows · RANGE 5 · EDITORIAL 19.
- Pairing: card href `items/<pk>` resolved within the card block (href follows the price in every card), product-name
  match for blog prose, explicit reference for milford-sound.html sections/JSON-LD/meta.
- Verification source: data layer. Every PAIRED pk carries a high-confidence 2026-08-24 (s45 v7) stamp — 0 probes
  needed for them. The only stale-stamped rows referenced are the two `index.html` JSON-LD `priceRange` endpoints
  (catalog min/max, 2026-05-28 stamps): probed live, standard protocol — undated + 17 dates 2026-08-25..09-10,
  `include_breakdown=yes`, $0 tiers discarded (none present):
  - 525692 hotpools "Te Manaroa Spring Eco Walk": 18/18 NZD, Adult/Child/Infant = 421¢ → **4.21** (`probe-525692-live.json`)
  - 479397 glaciercountryhelicopters "Franz to Fiords": 18/18 NZD, Group 1-3 = 2630435¢ → **26304.35**, Group 4-6 = 36826.09
    (`probe-479397-live.json`; 08-25..08-28 requests tracked forward to the 08-29 departure — same pattern as the 489299 probe).

## Stale (7 line-rows, all high-confidence 08-24 data) → fixed
| file:line | old | new | pk | evidence |
|---|---|---|---|---|
| blog/best-milford-sound-tours-from-queenstown.html:41 | NZ$174 | NZ$179 | 694946 Milford Sound Classic Cruise | Adult 179 |
| blog/best-milford-sound-tours-from-queenstown.html:43 | NZ$188 | NZ$199 | 272184 Milford Sound Boutique Small Boat Cruise | Adult 198.86 (site prose convention rounds: 199 on milford-sound.html:335, north-island blog:141) |
| rotorua.html:253 | Adult NZ$200, Child NZ$155 | Adult NZ$230, Child NZ$180 | 94047 Eco Thermal Park Half Day – Morning | tiers 230/180 |
| rotorua.html:248 | From NZ$200 (badge) | From NZ$230 | 94047 | whole-file sweep of the same old figure/pk |
| rotorua.html:313 | Adult NZ$180, Child NZ$125 | Adult NZ$190, Child NZ$135 | 94044 Elite Rotorua Cultural Half day | tiers 190/135 |
| rotorua.html:308 | From NZ$180 (badge) | From NZ$190 | 94044 | whole-file sweep |
| index.html:57 (JSON-LD priceRange) | NZ$15–NZ$9464 | NZ$4–NZ$26304 | 525692 / 479397 | RANGE, both endpoints live-verified; floor convention as before (15.9→15, 9464.3→9464) |

Sweep notes: `174`/`188` occur nowhere else in the blog file; `NZ$200`/`NZ$155` at rotorua.html:356/361 belong to pk 667097
whose tiers ARE 200/155 — left as-is; rotorua JSON-LD carries no prices; `15`/`9464` occur nowhere else in index.html.

## Deferred / untouched
- RANGE deferred: milford-sound.html:253 `NZ$383–398` — 383 = 295392 (current); 398 has no Doubtful referent in the data
  layer (only dirt-bike rows price at 398). Half-correct → not touched.
- RANGE current: milford-sound.html:10/16 meta+og `NZ$169–199`, `NZ$359+`; :196 `NZ$169–199` (257745=169, 272184=198.86, 257750=359).
- EDITORIAL untouched (19 rows): faq.html:29/99/103/108 (NZeTA ~NZ$23, SIM ~NZ$30, "NZ$200-300" bus+cruise, "~NZ$100"
  cruise-only — note the cheapest listed Milford cruise is 169, flagged for editorial review); blog/milford-sound-vs-doubtful-sound.html:123/124/166/168
  cost bands; milford-sound.html:312 "NZ$80–220 more"; advertise.html ×6 ($99/$299/$599 WNZ ad tiers); tours.html ×4 quiz buckets.
- Attribution flag (not a price literal): blog/best-milford…:43 credits "Mitre Peak Cruises" for a product that is Cruise Milford's
  (272184) in the data layer; no Mitre Peak rows exist. Price fixed; operator wording left for an editorial pass.
- Data-layer note: rows 94047/94044 `description` fields still quote the operator's old "Adult NZ$200, Child NZ$155" /
  "NZ$180, NZ$125" text (rendered on dynamic cards). Out of scope for this HTML-only task.
- Follow-up (out of scope, #104 gate domain): 15 high-confidence gated badges disagree with data by ≥1:
  auckland.html:164/176/260/284, queenstown.html:236/272/308/320/344/404/416/428, rotorua.html:344 (plus 248/308 swept here).
