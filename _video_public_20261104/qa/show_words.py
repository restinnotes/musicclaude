import json,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0,'.')
import pub2
tag=sys.argv[1]; R=Path('../_thread_evo_20261019/runs')
for w in ['op60','op61']:
    d=pub2.parse((R/f'pub3_write_{w}_{tag}'/'output.txt').read_text(encoding='utf-8'))
    print('=====',w,[(p['label'],p['emotion']) for p in d['phases']]); wc=0;lc=0;lch=0
    for s in d['sections']:
        print(s['sec'])
        for g in s['groups']:
            bs=[b['text']+(f"({b['emotion']})" if b.get('emotion') else '') for b in g.get('beads',[])]; wc+=len(bs)
            print(f"  [{g['rank']}|{g['emotion']}]",' / '.join(bs))
            for l in g.get('lines',[]): print('     →',l['text']); lc+=1; lch+=len(l['text'])
    print('词',wc,'线',lc,'线均字',lch//max(lc,1))
