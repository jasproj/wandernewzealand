import json,urllib.request,sys,datetime
short,pk=sys.argv[1],sys.argv[2]
dates=['undated']+[(datetime.date(2026,8,25)+datetime.timedelta(i)).isoformat() for i in range(17)]
out=[]
for d in dates:
    url=f"https://fareharbor.com/api/embed/{short}/price-preview/per-item/v2/?item_pks={pk}&include_breakdown=yes"+("" if d=="undated" else f"&date={d}")
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req,timeout=20) as r: st=r.status; body=json.load(r)
    except urllib.error.HTTPError as e: st=e.code; body={'error':e.read().decode()[:300]}
    items=body.get('items',[]); it=items[0] if items else None
    cts=[f"{c['singular']}={c['price']}[min{c.get('min_party_size')}]{(' note='+c['note']) if c.get('note') else ''}" for c in (it or {}).get('price',{}).get('breakdown',{}).get('customer_types',[])] if it else []
    out.append({'date':d,'status':st,'cur':body.get('details',{}).get('currency'),'itemReturned':bool(it),'low':(it or {}).get('price',{}).get('low'),'start_at':((it or {}).get('availability') or {}).get('start_at'),'cts':cts,'zeroTiers':[c for c in cts if '=0[' in c],'raw':body})
    print(d,st,body.get('details',{}).get('currency'),bool(it),(it or {}).get('price',{}).get('low'),((it or {}).get('availability') or {}).get('start_at'),cts)
json.dump(out,open(f'scripts/evidence/wnz-badges-2026-08-24/probe-{pk}-live.json','w'),indent=1)
