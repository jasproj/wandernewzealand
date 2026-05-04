# wandernewzealand v5.2 Dry-Run Report (NZD) — null-price tour re-extraction

**Generated:** 2026-05-03T21:42:05.099Z
**Branch:** `feat/nz-v52-price-extraction`
**Mode:** `--dry-run-only` (no writes to tours-data.json)

## 1. Inputs

- wandernewzealand total tours: 500
- Tours with `price: null` evaluated: **157**
- Extractor: v5.4 baseline + v5.2 dominant-price gate (ported verbatim from wanderusvi)
- Currency: **NZD**
- Page fetch: Playwright (chromium headless), 1.5 s settle wait

## 2. Result distribution

| Outcome | Count | Disposition |
|---|---:|---|
| **high** (v5.4 Method 1/2 — adult/per-person anchor) | 0 | "From $X" if applied |
| **medium** (v5.4 native — Method 3/4/6) | 0 | "From $X" if applied |
| **medium** (v5.2 dominant-price gate) | 1 | "From $X" if applied |
| **low** (Method 5 unanchored, gate FAILed) | 0 | stays "Check availability" |
| **no-price** (extractor returned null) | 156 | stays "Check availability" |
| **error** (fetch/parse) | 0 | stays "Check availability" |
| **Total** | 157 | |

**Net effect if applied --live:** 1 tours flip from "Check availability" → "From $X" (0.6% of the 157). 156 stay hidden.

## 3. Cat-E candidate sanity check

**0 Cat-E candidates** detected among gate PASSes. Disqualifier blocklist (`additional, extra, option, optional, rental, nitrox, upgrade, supplement, add-on, addon, surcharge` + `+$` literal) appears to be holding.

## 4. Sample 10 promoted tours

### 684265 — Birthday Party at Fergs - Climbing and Croc Bikes

- company: Ferg's Wellington
- extracted price: **$315** (medium, unknown)
- priceSource: `v52-dominant-gate`
- gate distinct $-values: [315]
- gate matched token: `NZ$315.65`
- gate ±40 char window:

  ```
  ream cake! 4.5 stars 456 Google reviews NZ$315.65 Climbing Birthday Party Up to 8 Climber
  ```

## 5. Sample 5 stays-hidden tours

### 480036 — The Serenity River Expedition

- outcome: no-price

### 507729 — Te Araroa Trail - Freedom Hire Canoe Journey from Whakahoro to Whanganui

- outcome: no-price

### 109315 — Kids Surf Birthday Party

- outcome: no-price

### 211203 — Valley of the Vines Wine Trail – Arrowtown to Gibbston (Self-Guided)

- outcome: no-price

### 298081 — National Park | Whakapapa Snow | Shuttles & Transfer Round trip

- outcome: no-price

## 6. Out of scope for this run

- No edits to `tours-data.json`.
- No commits, no push, no deploy.
- `--live` mode not implemented yet — adopt USVI's `apply-v52-live.js` pattern when ready.
