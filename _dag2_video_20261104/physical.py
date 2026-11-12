"""Conservative physical bindings from explicit bar + hand statements only."""
import re
from dag2 import ROOT, WORKS, read, write, bounds, sha

def compile_one(w):
 src=read(ROOT/f'input/{w}.json');m=read(ROOT/f'input/{w}_music.json');p=read(ROOT/f'plans/{w}_v1.json');times=dict(m['bars']);out=[];withheld=[]
 for si,s in enumerate(src['segments']):
  sa,sb=bounds(s['bars'])
  for b in s['beads']:
   for match in re.finditer(r'(?:第|约)?(\d{1,3})(?:[–—-](\d{1,3}))?小节([^。；]{0,140})',b['text']):
    clause=match.group(3);hands=[h for h in ['左手','右手'] if h in clause]
    if len(hands)!=1:continue
    a=int(match.group(1));z=int(match.group(2) or a)
    if not sa<=a<=z<=sb:continue
    reason=None
    if any(x in clause for x in ['内声部','最高声部','最上方','两条旋律']):reason='Only whole-hand data available; no verified inner-voice identity'
    if '起' in clause and not match.group(2):reason='Open-ended range does not identify a bounded note interval'
    groups={x['group'] for x in p['links'] if x['bead_id']==b['id'] and x['strength']=='相近' and x.get('group',99)<6}
    if len(groups)!=1:reason='No unique accepted semantic colour for this bead'
    t0=times[a];t1=times.get(z+1,m['dur']);hand=0 if hands[0]=='左手' else 1
    notes=[n for n in m['notes'] if t0<=n['s']<t1 and n['h']==hand]
    if not notes:reason='No matching notes; a statement of silence cannot light notes'
    item={'sec':s['sec'],'bead_id':b['id'],'quote':match.group(0),'span':[match.start(),match.end()],'bars':[a,z],'hand':hand,'t0':t0,'t1':t1,'notes':len(notes)}
    if reason:withheld.append({**item,'reason':reason})
    else:out.append({**item,'group':next(iter(groups))})
 result={'source_sha256':sha(ROOT/f'input/{w}.json'),'music_sha256':sha(ROOT/f'input/{w}_music.json'),'policy':'Explicit bounded bar range plus one hand; no melody/inner-voice inference. Narrative links never create note identities. Uncertain matches remain neutral.','bindings':out,'withheld':withheld}
 write(ROOT/f'plans/{w}_physical.json',result);print(w,'physical bindings',len(out),'withheld',len(withheld),flush=True);return result

if __name__=='__main__':
 for w in WORKS:compile_one(w)
