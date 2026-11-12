"""Focused independent recheck against the exact old best explanations, with previous defects exposed."""
import hashlib
import json
import sys
import evo
import node2b
import review_pilot
import synth_v2

if __name__=='__main__':
 tag=sys.argv[1]
 d=json.loads((evo.ROOT/f'evaluations/synth/{tag}_op60/run.json').read_text(encoding='utf-8'))
 if len(d['state'])!=5 or any(not s['check'].get('pass') for s in d['state'].values()):raise ValueError('local gate pending; global/non-regression checks may run independently')
 original=json.loads((evo.ROOT/'evaluations/continuation_20261025/pilot_review_23195bf76768.json').read_text(encoding='utf-8'))
 old=[{'id':f'O{i}','source':name,'segments':segments} for i,(name,segments) in enumerate(review_pilot.historical(),1) if f'O{i}' in ('O11','O12')]
 current=[{'sec':s,'chosen':st['chosen'],'hist':st['hist'],'fate':st['pick']['fate']} for s,st in d['state'].items()]
 prior=[{'model':m,'problems':r['new'][0]['problems'],'non_regression':r['new'][0]['non_regression']} for m,r in original['reviews'].items()]
 beads=[b for b in review_pilot.covjudge.beads('op60') if b['sec']<='S05' and b['role']!='演奏条件']
 msg=review_pilot.RULES+'\n本轮不是改动验收标准：保留先前全部具体性、深度、不虚构与旧值不回退要求。先前完整旧材料已找出的两个最佳旧稿原文如下，重点重新绝对验收当前的增量因果。\n固定轻处境或初段当下心理问题本身不等于提前计算Center；须指出它是否实际阻止后文新增经验，不可仅因开头有明确在乎就禁用。正式Center仍在全曲后归纳。\n【听感】'+json.dumps(beads,ensure_ascii=False)+'\n【旧最佳原文】'+json.dumps(old,ensure_ascii=False)+'\n【前次批评】'+json.dumps(prior,ensure_ascii=False)+'\n【新试跑 N1】'+json.dumps(current,ensure_ascii=False)
 digest=hashlib.sha256(msg.encode()).hexdigest()[:12];jobs=[]
 for mdl in ('g6','g56'):
  rid='pilot_depth_'+mdl+'_'+digest
  if not evo.done(rid):jobs.append(node2b.job(rid,msg,{'stage':'pilot_depth_non_regression'},w=mdl))
 evo.run_parallel(jobs,len(jobs) or 1)
 result={'tag':tag,'reviews':{m:synth_v2.judge_synth_v3.parse(evo.output('pilot_depth_'+m+'_'+digest)) for m in ('g6','g56')}}
 out=evo.ROOT/f'evaluations/continuation_20261025/pilot_depth_{tag}.json';synth_v2.dump(out,result)
 for m,r in result['reviews'].items():
  print(m,json.dumps(r['new'],ensure_ascii=False),flush=True)
