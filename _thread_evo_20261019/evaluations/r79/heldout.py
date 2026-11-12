"""留出评委：Gemini 没参与过盲比票和回补，只用来检查有没有迎合 GPT 评委。提示词与盲比完全相同。"""
import os,sys,json
os.environ.setdefault('JV','2')
sys.path.insert(0,'.')
import evo, v6fix as V, screen_flow as F
from concurrent.futures import ThreadPoolExecutor
tag,base=sys.argv[1:3]
def one(job):
    w,s=job
    a,b=V.graph_of(w,base),V.graph_of(w,tag)
    x,y=(b,a) if s=='newX' else (a,b)
    rid=f'ho_{w}_gem_{tag}_vs{base}_{s}'
    msg=V.BLIND2.format(NAME=V.covjudge.NAME[w],WHAT=V.WHAT2,X=V.view(x),Y=V.view(y),BEADS=V.beads(w))
    if not evo.done(rid): evo.call_gemini_direct(rid,msg,meta={'stage':'heldout','web':False})
    d=V.parse(rid) if evo.done(rid) else None
    if not d: return (w,s,None)
    new,old=('X','Y') if s=='newX' else ('Y','X')
    secs=d['sections']
    return (w,s,'选新' if d['better']==new else '选旧','不退步' if d.get(f'{new}_replacing_{old}_regress')=='否' else '退步',{k:sum((c[k]==new)-(c[k]==old) for c in secs) for k in F.DIMENSIONS},(d.get('better_why') or '').replace(new,'新').replace(old,'旧')[:300])
with ThreadPoolExecutor(2) as p:
    for r in p.map(one,[(w,s) for w in F.WORKS for s in('newX','newY')]): print(r,flush=True)
