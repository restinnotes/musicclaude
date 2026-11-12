"""Export only explicitly accepted artifacts, with semantic hashes and complete bead disposition."""
import hashlib
import json
import sys
from pathlib import Path
import covjudge
import evo
import synth_v2

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def render(g,work):
 title='肖邦《船歌》Op.60' if work=='op60' else '肖邦《幻想波兰舞曲》Op.61'
 lines=[title,'Center：'+g['center'],'']
 items={i['id']:(s['bars'],i) for s in g['segments'] for i in s['items']}
 for s in g['segments']:
  lines.extend([s['sec']+' ｜ '+s['bars']+'小节 ｜ '+s['relation'],''])
  for i in s['items']:
   lines.append(('→ ' if i.get('follows') else '• ')+i['text'])
   for a in s.get('because',[]):
    if a['to']==i['id']:
     bars,b=items[a['from']]
     lines.append('  ← '+bars+'「'+b['key']+'」〔'+a['rel']+'〕'+(('：'+a['how']) if a.get('how') else ''))
  lines.append('')
 return '\n'.join(lines).rstrip()+'\n'

if __name__=='__main__':
 gatepath=Path(sys.argv[1]);gate=json.loads(gatepath.read_text(encoding='utf-8'))
 if gate.get('decision')!='accept_complete':raise ValueError('final content acceptance has not been recorded')
 out=Path(r'C:\Users\zuoyi\Documents\Codex\2026-10-25\n-n\outputs');out.mkdir(parents=True,exist_ok=True)
 for work,info in gate['works'].items():
  p=evo.ROOT/info['graph_path']
  if sha(p)!=info['graph_sha256']:raise ValueError('accepted graph changed after review')
  graph=json.loads(p.read_text(encoding='utf-8'))
  sourcepath=evo.ROOT/f"evaluations/synth/{info['source_tag']}_{work}/run.json"
  if sha(sourcepath)!=info['source_sha256']:raise ValueError('accepted synthesis changed after review')
  source=json.loads(sourcepath.read_text(encoding='utf-8'))
  run=synth_v2.Run(info['source_tag'],work,'g6',source['pool']);run.state=source['state']
  graph['center']=info['center']
  relation={r['sec']:r['relation'] for r in info['relations']}
  if set(relation)!={s['sec'] for s in graph['segments']}:raise ValueError('Center relations incomplete')
  for s in graph['segments']:s['relation']=relation[s['sec']]
  beads=covjudge.beads(work);coverage=[]
  for b in beads:
   st=source['state'][b['sec']]
   check=next((x for x in st['check'].get('coverage',[]) if x['id']==b['id']),None)
   coverage.append({**b,'author_fate':st['pick']['fate'].get(b['id'],'演奏条件，不要求主线逐项解释'),'independent_check':check})
  prefix='Op60_船歌' if work=='op60' else 'Op61_幻想波兰舞曲'
  (out/(prefix+'_Thread.txt')).write_text(render(graph,work),encoding='utf-8-sig')
  reviewroot=evo.ROOT/'evaluations/continuation_20261025/finalization'
  reviewkey=info['source_tag']+'_'+work
  package={'work':work,'graph':graph,'beads':coverage,'candidate_pools':{sec:run.mechs(sec) for sec in source['state']},'selected_synthesis':source['state'],'acceptance':info,
   'fidelity_reviews':json.loads((evo.ROOT/info['fidelity_review_path']).read_text(encoding='utf-8')),
   'center_candidates':json.loads((reviewroot/(reviewkey+'_center_candidates.json')).read_text(encoding='utf-8')),
   'center_reviews':json.loads((reviewroot/(reviewkey+'_center_reviews.json')).read_text(encoding='utf-8')),
   'provenance':{'claude_transcript':r'C:\Users\zuoyi\.claude\projects\D--musicclaude\7c623294-a1ea-40eb-b513-ae6588ad2c39.jsonl','source_path':str(sourcepath),'source_sha256':sha(sourcepath),'graph_sha256':sha(p),'final_gate_path':str(gatepath),'final_gate_sha256':sha(gatepath)},
   'center_relation_main_review':info.get('relation_review',{}),
   'post_review_main_change':info.get('post_review_main_change',{}),
   'reading_note':'同段→表示真实因果或心理推出，跨段←标真实历史作用；主线没有强并的替代读法完整保留在beads.author_fate及原文中。解释池与全部原始评审保存在项目目录。'}
  (out/(prefix+'_Thread_完整记录.json')).write_text(json.dumps(package,ensure_ascii=False,indent=2),encoding='utf-8')
 (out/'本次续作_验收记录.txt').write_text(gate['human_report'],encoding='utf-8-sig')
 print('exported',str(out),flush=True)
