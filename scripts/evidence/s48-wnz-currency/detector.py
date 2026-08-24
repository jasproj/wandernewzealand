#!/usr/bin/env python3
"""s48-wnz-currency hard-coded-symbol detector.
FIRES on renderer code that bakes a currency symbol/code into output: a JS template literal
containing `From NZ$` or a JSON-LD `"priceCurrency": "<literal>"`. Does NOT fire on prose or
static-badge content (controls). Scans git-tracked *.js / *.html. Exit 1 if any hit."""
import re,subprocess,sys,json
files=subprocess.check_output(['git','ls-files','*.js','*.html']).decode().split()
FIRE=re.compile(r'`[^`]*From NZ\$\$\{|"priceCurrency"\s*:\s*"[A-Z]{3}"')
CTRL=re.compile(r'NZ\$')
hits,controls=[],[]
for f in files:
    if f.startswith('scripts/evidence/'): continue
    for i,l in enumerate(open(f,encoding='utf-8',errors='replace'),1):
        if FIRE.search(l): hits.append(f'{f}:{i}:{l.strip()[:90]}')
        elif CTRL.search(l): controls.append(f'{f}:{i}:{l.strip()[:90]}')
print(json.dumps({'fires':hits,'controlCount':len(controls),'controlSample':controls[:6]},indent=1))
sys.exit(1 if hits else 0)
