#!/usr/bin/env python3
"""
s66 season pages — static region / activity×place landing pages built from
tours-data.json, using queenstown.html as the chrome template (head block,
header, footer are sliced verbatim from that file at build time).

Usage: python3 scripts/build-season-pages.py            # writes pages
       python3 scripts/build-season-pages.py --dry-run  # counts only

Rules mirrored from app.js: price badge only when price is finite, confidence
is not 'low' and currency is NZD/USD (formatPrice); JSON-LD Offer only for
per-person price labels (classifyPriceUnit state 1). Nothing is invented.
"""
import json, re, sys, html, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
TPL = (ROOT / "queenstown.html").read_text()
DATA = json.load(open(ROOT / "tours-data.json"))["tours"]
ACTIVE = [t for t in DATA if t.get("status") == "active"]
TODAY = datetime.date.today().isoformat()
SITE = "https://wandernewzealand.com"

CURRENCY = {"NZD": "NZ$", "USD": "US$"}
MULTI = re.compile(r"\b(two|three|four|five|six|seven|eight|nine|ten|2|3|4|5|6|7|8|9|10)[\s-]*(people|persons?|adults?|passengers?|pax|players?|guests?|surfers?|paddlers?|children|kids?|occupants?)\b", re.I)
GROUP = re.compile(r"\b(family|families|group|groups|team|teams|shared|twin|double|triple|couple|companions?|pair|party|parties|seater|charter|charters)\b|\bup\s*to\s*(\d+|two|three|four|five|six|seven|eight|nine|ten)\b|\bprivate\b.*\b(tour|event|transport)\b", re.I)
PERSON = re.compile(r"\b(adults?|persons?|participants?|passengers?|child(ren)?|kids?|riders?|divers?|solo|students?|surfers?|guests?|seniors?|toddlers?|youths?|hikers?|walkers?|climbers?|cyclists?|paddlers?|paddleboarders?|sightseers?|backpackers?|travell?ers?|pillion|players?|occupanc(y|ies)|occupants?|rafters?|general\s+admission)\b", re.I)


def fmt_price(t):
    p = t.get("price")
    if not isinstance(p, (int, float)) or p <= 0 or t.get("priceConfidence") == "low":
        return "Check availability"
    sym = CURRENCY.get(t.get("currency"))
    if not sym:
        return "Check availability"
    return f"From {sym}{round(p):,}"


def per_person(t):
    lab = t.get("priceLabel") or ""
    if MULTI.search(lab) or GROUP.search(lab):
        return False
    return bool(PERSON.search(lab))


def img(url):
    m = re.match(r"https://cdn\.filestackcontent\.com/([A-Za-z0-9]+)$", url or "")
    if m:
        return f"https://cdn.filestackcontent.com/resize=w:800/output=format:webp,quality:75/{m.group(1)}"
    return url or "/images/og-image.jpg"


def short(desc, n=140):
    d = re.sub(r"\s+", " ", (desc or "")).strip()
    return d if len(d) <= n else d[:n].rsplit(" ", 1)[0] + "…"


def blob(t):
    return (t["name"] + " " + " ".join(t.get("tags") or []) + " " + (t.get("category") or "")).lower()


GLOBAL_NONE = ["golf", "miniputt", "mini putt", "driving range", "sauna", "hot tub", "escape room", "gift voucher",
               "voucher", "group booking", "car park", "parking", "birthday", "course -", "development course",
               "specialist training", "deposit", "membership", "season pass", "staff", "test ", "permit", "trail pass",
               "dog trail", "dog walk", " hut", "snowshoe", "ski package", "ski pass", "day rental", "classic vr",
               "photo / video", "lesson", "winter package", "christmas", "new year", "nye ", "transfer", "shuttle",
               "airport", "hire - no shuttle", "add-on", "add on", "upgrade", "extra", "surcharge", "clothing", "general admission",
               "private function", "private booking", "sim racing", "virtual reality", "vr ", " vr", "campground", "camping",
               "surf camp", "program", "week pass", "day pass", "ski rental", "cross-country ski", "can-am", "tent "]
CJK = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af]")


def pick(islands=None, any_words=None, none_words=None, loc_words=None, limit=24, also_any=None, boost=None, cap=4):
    out = []
    for t in ACTIVE:
        if CJK.search(t["name"]) or any(w in t["name"].lower() for w in GLOBAL_NONE):
            continue
        isl = (t.get("island") or "").lower()
        loc = (t.get("location") or "").lower()
        if islands and not (isl in islands or (loc_words and any(w in loc for w in loc_words))):
            continue
        b = blob(t)
        if any_words and not any(w in b for w in any_words):
            continue
        if also_any and not any(w in b for w in also_any):
            continue
        if none_words and any(w in b for w in none_words):
            continue
        if not t.get("image"):
            continue
        out.append(t)
    # de-dupe by pk
    seen, uniq = set(), []
    for t in out:
        key = (t["pk"],); nkey = (t["company"], t["name"].strip().lower())
        if key in seen or nkey in seen:
            continue
        seen.add(key); seen.add(nkey); uniq.append(t)
    bw = [w.lower() for w in (boost or [])]
    uniq.sort(key=lambda t: (0 if any(w in blob(t) for w in bw) else 1, -(t.get("qualityScore") or 0), -(t.get("reviewCount") or 0), t["name"]))
    # per-company cap so one operator's 12 time-slot variants don't fill the grid
    shown, percomp = [], {}
    for t in uniq:
        c = percomp.get(t["company"], 0)
        if c >= cap:
            continue
        percomp[t["company"]] = c + 1
        shown.append(t)
        if len(shown) >= limit:
            break
    return uniq, shown


def card(t):
    name = html.escape(t["name"]); comp = html.escape(t["company"])
    return f'''<article class="tour-card">
    <div class="tour-image">
        <img src="{img(t.get("image"))}" alt="{name}" loading="lazy" decoding="async" width="400" height="200" style="width:100%; height:200px; object-fit:cover;">
        <div class="tour-price">{fmt_price(t)}</div>
    </div>
    <div class="tour-content">
        <div class="tour-company">{comp}</div>
        <h3 class="tour-title">{name}</h3>
        <p class="tour-desc">{html.escape(short(t.get("description")))}</p>
        <a href="{html.escape(t["bookingUrl"])}" target="_blank" rel="noopener noreferrer" class="tour-book-btn book-now-btn" data-tour-id="{t["pk"]}" data-tour-name="{name}">Check Availability →</a>
    </div>
</article>'''


def trip_schema(t):
    o = None
    if isinstance(t.get("price"), (int, float)) and t.get("priceConfidence") != "low" and t.get("currency") in CURRENCY and per_person(t):
        o = {"@type": "Offer", "price": t["price"], "priceCurrency": t["currency"], "url": t["bookingUrl"], "availability": "https://schema.org/InStock"}
    d = {"@type": "TouristTrip", "name": t["name"], "description": short(t.get("description"), 300), "touristType": ", ".join(t.get("tags") or []), "provider": {"@type": "LocalBusiness", "name": t["company"]}}
    if o:
        d["offers"] = o
    return d


# ---- template slices -------------------------------------------------------
def slice_between(s, a, b):
    i = s.index(a); j = s.index(b, i)
    return s[i:j + len(b)]

HEAD_CSS = slice_between(TPL, "<style>", "</style>")
GA = slice_between(TPL, '<script async src="https://www.googletagmanager.com', "</script>\n<script>")
GA = slice_between(TPL, '<script async src="https://www.googletagmanager.com', "})();\n</script>")
HEADER = slice_between(TPL, '<header class="header">', "</header>")
FOOTER = slice_between(TPL, '<footer class="footer">', "</footer>")
FONTS = slice_between(TPL, '<link rel="preconnect" href="https://fonts.googleapis.com">', '<link rel="stylesheet" href="/shared-chrome.css">')
MENU_JS = slice_between(TPL, "<script>\n  /* Self-contained mobile-menu toggle", "</script>")

EXTRA_CSS = """
  .season { background: #eef6f3; padding: 40px 0; }
  .season h2 { font-size: 1.5rem; margin-bottom: 14px; }
  .season p { margin: 0 0 12px; }
  .faq { padding: 50px 0; }
  .faq h2 { font-size: 1.6rem; margin-bottom: 18px; }
  .faq details { background: #fff; border: 1px solid #e2e8ec; border-radius: 8px; padding: 14px 18px; margin-bottom: 10px; }
  .faq summary { font-weight: 600; cursor: pointer; }
  .faq p { margin: 10px 0 0; color: #333; }
  .linkgrid { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; }
  .linkgrid a { background: #fff; border: 1px solid #d9e2e7; border-radius: 20px; padding: 8px 14px; color: #0a5c4f; text-decoration: none; font-weight: 500; }
  .linkgrid a:hover { background: #0a5c4f; color: #fff; }
"""


def build(p, shown, total):
    url = f"{SITE}/{p['slug']}.html"
    title = html.escape(p["title"]); desc = html.escape(p["description"])
    dest = {"@context": "https://schema.org", "@type": "TouristDestination", "name": f"{p['h1']} — WanderNewZealand", "description": p["description"], "url": url}
    itemlist = {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": t["name"], "url": t["bookingUrl"]} for i, t in enumerate(shown)]}
    faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]}
    graph = {"@context": "https://schema.org", "@graph": [trip_schema(t) for t in shown]}
    crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": p["h1"], "item": url}]}
    faq_html = "\n".join(f"<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>" for q, a in p["faq"])
    know = "\n".join(f"<li>{html.escape(k)}</li>" for k in p["know"])
    related = "\n".join(f'<a href="{h}">{html.escape(l)}</a>' for h, l in p["related"])
    intro = "".join(f"<p>{para}</p>" for para in p["intro"])
    season = "".join(f"<p>{para}</p>" for para in p["season"])
    cards = "\n".join(card(t) for t in shown)
    countline = f"{total} available" if total > len(shown) else f"{len(shown)} available"
    j = lambda o: json.dumps(o, ensure_ascii=False)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" type="image/png" sizes="32x32" href="/images/favicon-32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/images/favicon-16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/images/apple-touch-icon.png">
<link rel="icon" type="image/x-icon" href="/images/favicon.ico">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">

<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{SITE}/images/og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{SITE}/images/og-image.jpg">

{GA}

<script type="application/ld+json">{j(dest)}</script>
<script type="application/ld+json">{j(itemlist)}</script>
<script type="application/ld+json">{j(faq)}</script>
<script type="application/ld+json">{j(crumbs)}</script>

<script src="/tracking.js" defer></script>

{FONTS}
{HEAD_CSS[:-8]}{EXTRA_CSS}</style>
        <link rel="stylesheet" href="/styles.css">

<script type="application/ld+json">
{json.dumps(graph, ensure_ascii=False, indent=1)}
</script>
</head>
<body>
{HEADER}

<section class="hero">
  <div class="container">
    <h1>{html.escape(p["h1"])}</h1>
    <p>{html.escape(p["hero"])}</p>
  </div>
</section>

<section class="intro">
  <div class="container">
    <h2>{html.escape(p["intro_h2"])}</h2>
    {intro}
  </div>
</section>

<section class="season">
  <div class="container">
    <h2>{html.escape(p["season_h2"])}</h2>
    {season}
  </div>
</section>

<section class="what-to-know">
  <div class="container">
    <h2>What to know before you book</h2>
    <ul>
{know}
    </ul>
  </div>
</section>

<section class="tours" id="tours">
  <div class="container">
    <h2>{html.escape(p["tours_h2"])} ({countline})</h2>
    <div class="tours-grid">
{cards}
    </div>
  </div>
</section>

<section class="faq" id="faq">
  <div class="container">
    <h2>{html.escape(p["faq_h2"])}</h2>
{faq_html}
  </div>
</section>

<section class="related">
  <div class="container">
    <h3>More on WanderNewZealand</h3>
    <div class="linkgrid">
{related}
    <a href="/">All tours</a>
    <a href="/blog/">Travel guides</a>
    </div>
  </div>
</section>

{FOOTER}
{MENU_JS}
</body>
</html>
'''


PAGES = json.load(open(ROOT / "scripts" / "season-pages.json"))

if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    report = []
    for p in PAGES:
        f = p["filter"]
        allm, shown = pick(islands=f.get("islands"), any_words=f.get("any"), none_words=f.get("none"), loc_words=f.get("loc"), limit=f.get("limit", 24), also_any=f.get("also"), boost=f.get("boost"), cap=f.get("cap", 4))
        report.append((p["slug"], len(allm), len(shown)))
        if len(shown) < 8:
            print(f"SKIP {p['slug']}: only {len(shown)} tours"); continue
        if not dry:
            (ROOT / f"{p['slug']}.html").write_text(build(p, shown, len(allm)))
    for r in report:
        print(f"{r[0]:40s} matched={r[1]:4d} shown={r[2]}")
