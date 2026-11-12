import sys,os,json,zipfile,hashlib
from pathlib import Path
from collections import Counter
os.environ['JV']='2'
sys.path.insert(0,'.')
import v6fix as V, prepare_i10_mainline as P
out=Path('deliver_20261106_r79d');out.mkdir(exist_ok=True)
names={'op60':'《船歌》Op.60','op61':'《幻想波兰舞曲》Op.61'}
report={}
for w in('op60','op61'):
    g=V.graph_of(w,'r79d')
    (out/f'{w}_只看线_r79d.md').write_text(f'# {names[w]}：只看线（版本 r79d）\n\n'+V.view(g,center=True),encoding='utf-8')
    t=(V.OUT/f'合写_{w}_r79d.md').read_text(encoding='utf-8')
    (out/f'{w}_线与珠子_r79d.md').write_text(t,encoding='utf-8')
    exp=Counter('> '+('也可以听成：' if b['role']=='另一种理解' else '')+b['text'] for b in P.visible_beads(w))
    act=Counter(l for l in t.splitlines() if l.startswith('> ') and not l.startswith('> <small>'))
    items=[i['text'] for s in g['segments'] for i in s['items']]
    assert exp==act and all(i in t for i in items)
    report[w]={'线条数':len(items),'字数':sum(map(len,items)),'珠子数':sum(exp.values()),'珠子逐字一致':exp==act,'线逐字在合写内':True,
      '每段条数':[len(s['items']) for s in g['segments']],'线哈希':hashlib.sha256('\n'.join(items).encode()).hexdigest()[:16]}
(out/'integrity.json').write_text(json.dumps(report,ensure_ascii=False,indent=1),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False)[:700])
