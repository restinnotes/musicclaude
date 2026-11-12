import json,sys
sys.stdout.reconfigure(encoding='utf-8')
for w in ('op60','op61'):
    d=json.load(open(f'r3/script_{w}_w6.json',encoding='utf-8'))
    src=json.load(open(f'r2/{w}_src.json',encoding='utf-8'))
    P={p['id']:p['text'] for s in src['sections'] for b in s['beads'] for p in b['points']}
    u=[set(x for s in json.load(open(f'r3/read_{w}_{j}_w6.json',encoding='utf-8'))['sections'] for x in s.get('unclear',[])) for j in ('g6','g56')]
    both=u[0]&u[1]
    print('==',w,'原珠子点数',len(P),'平均字数',sum(map(len,P.values()))//len(P))
    n=0
    for s in d['sections']:
        for g in s['groups']:
            for b in g.get('beads',[]):
                if b['text'] in both and n<24:
                    n+=1
                    print(f"[{b['text']}] <- {' | '.join(P.get(f,'?'+f) for f in b.get('from',[]))}")
