# s48 — WNZ renderer currency-awareness (port of WENG #92 / 9e851fc)

Base origin/main `ba57cefd…` (#110 squash) == local HEAD at gate 0. Chrome extension DARK this session — no served-bytes
read was possible pre-merge; every render figure here is node-vm over `createTourCard`/`generateTourSchema` against
the branch tree (`render-harness.mjs`, same loader predicate as `app.js` `status !== 'inactive' && !bookingDead`).

## Port
`app.js` only. `CURRENCY_SYMBOL = { NZD: 'NZ$', USD: 'US$' }`; `formatPrice(price, confidence, currency)` picks the symbol
from the row; `generateTourSchema` gates the offer on the same map and emits `priceCurrency: tour.currency` verbatim.
Removed hard-coded `From NZ$` (was app.js:191) and `"priceCurrency": "NZD"` (was app.js:219). Adaptations vs WENG:
map contents (site currencies), comment tag, and WNZ's existing `priceUnit()` suffix left in place.

## Detector (`detector.py`)
Fires on renderer code baking a symbol into output (template literal `From NZ$${` or literal `"priceCurrency": "XXX"`),
silent on prose/static content. Pre-change tree: 2 fires (app.js:191, app.js:219), 98 `NZ$` control lines not fired.
Post-change: 0 fires, 99 controls (the map line itself is now a control — it is data, not a baked template).

## Population
3121 rows, all carry `currency` (**no-currency-field rows = 0**, enumerated). NZD 3120 / USD 1 (pk 340836) — carried
"1 USD row, restamped, null price" → Δ0. Pre-port the renderer assumed NZD for every row; post-port an unmapped or
missing currency renders "Price on request" with no offer (fixture `fx-eur`, `fx-nocur`) — that population is empty on
the live data.

## airkaikoura pk 340836 (`probe-340836-live.json`)
Stored: USD, price null, priceConfidence high, priceEnrichmentStatus error, stale breakdown Adult 205.17 / Child 121 /
Infant 0 / Family pass (2A2C) 626.04. Live `include_breakdown=yes` probe 2026-08-24T22:02Z: HTTP 400 "Company with
shortname airkaikoura not found" — single pk, 4-pk batch, and bounded retry (single pk + `date=`); company items page
renders FareHarbor "Not found". **HELD stays HELD.** No customer type could be confirmed live, so no floor is anchored.
Row untouched; it renders "Price on request" with no offer before and after (null price fails `isFinite` first).

## Static badges
66 (auckland 24 / queenstown 24 / rotorua 18) paired to rows by `data-tour-id`: every paired row is NZD; 340836 is on no
static page. **0 badges change symbol.**

## Render gate (`render-evidence.json`, `fixture-evidence.json`)
Live data: 3112 loaded rows, **3112 byte-identical pre/post** (html + JSON-LD); visiblePrice 2001 == jsonLdOffers 2001;
visibleBySymbol {NZ$: 2001} == visibleByCurrency {NZD: 2001}; offers.priceCurrency == row.currency on all 2001; the 4
low rows (200995, 347361, 380505, 389217) render "Price on request" with no offer; 340836 "Price on request", no offer.
Fixture (6 synthetic rows): USD 205.17 high → pre `From NZ$205.17`/NZD, post `From US$205.17`/USD; EUR and no-currency
rows → post "Price on request", no offer; NZD row byte-identical. sha256s computed in Python (`render-evidence.json`).
