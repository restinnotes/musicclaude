from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def put(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
proposal=read(R/'reviews'/'pilot_repair_proposals.json')
fixes=read(R/'EDITORIAL_FIXES.json')
for f in proposal['fixes']:
 f=f.copy()
 if f['block_id']=='S02-B01':
  # Keep technical facts in the trace; here restore the distinctive bodily experience.
  f['new']=f['new'].split('\n\n',1)[1]
 if f not in fixes:fixes.append(f)
put(R/'EDITORIAL_FIXES.json',fixes)
mapping={'S02-B13':'S02-B01','S02-B14':'S02-B02','S02-B15':'S02-B06','S02-B16':'S02-B12','S04-B11':'S04-B07','S04-B12':'S04-B01','S07-B11':'S07-B07','S07-B12':'S07-B04'}
adopt=[]
for a in proposal['additions']:
 if a['id']=='S07-B11':
  # The line belongs to an auditory observation; heat returning remains a separate reading.
  a=a.copy();a['text']='另一种听感里，先前的平静被打破，热度又回来；内声部像暗涌，不断向上攀爬。'
 if a['id']=='S02-B16':
  a=a.copy();a['text']=a['text'].replace('也可以听成呼吸','另一种听法里，呼吸')
 adopt.append({'segment':a['segment'],'target_block':mapping[a['id']],'text':a['text'],'evidence':a['evidence'],'restored_ids':a['meaning_ids'],'reason':a['reason']})
put(R/'PILOT_ADDITIONS.json',adopt)
print('prepared',len(proposal['fixes']),'precise repairs and',len(adopt),'in-place parallel observations')
