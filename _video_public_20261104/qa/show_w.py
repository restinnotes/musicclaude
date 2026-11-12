import json,sys
sys.stdout.reconfigure(encoding='utf-8')
tag=sys.argv[1]
for w in ['op60','op61']:
    d=json.load(open(f'r3/script_{w}_{tag}.json',encoding='utf-8'))
    m=json.load(open(f'r3/marks_{w}_{tag}.json',encoding='utf-8'))['marks']
    mk={(x['sec'],x['text']):x for x in m if x.get('render') is True}
    print('=====',w,[p['label'] for p in d['phases']],'标',len(mk),'/',len(m)); wc=lc=lch=0
    for s in d['sections']:
        print(s['sec'])
        for g in s['groups']:
            bs=[]
            for b in g.get('beads',[]):
                t=b['text'];wc+=1;x=mk.get((s['sec'],t))
                if b.get('emotion'): t+=f"({b['emotion']})"
                if x: t+=f"[{x['bars'][0]}-{x['bars'][-1]}/{x.get('pitch')}]"
                bs.append(t)
            print(f"  [{g['rank']}|{g['emotion']}]",' / '.join(bs))
            for l in g.get('lines',[]): print('     →',l['text']);lc+=1;lch+=len(l['text'])
    print('词',wc,'线',lc,'线均字',lch//max(lc,1))
