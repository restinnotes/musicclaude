import json,sys
sys.stdout.reconfigure(encoding='utf-8')
tag=sys.argv[1]; w=sys.argv[2]; secs=sys.argv[3:]
d=json.load(open(f'r3/script_{w}_{tag}.json',encoding='utf-8'))
print(len(d['sections']),'段')
for s in d['sections']:
    if secs and s['sec'] not in secs: continue
    print('##',s['sec'])
    for g in s['groups']:
        print(' ',g['rank'],g['emotion'],'|',' '.join(l['text'] for l in g.get('lines',[])))
        print('    词:',' / '.join(b['text'] for b in g.get('beads',[])))
