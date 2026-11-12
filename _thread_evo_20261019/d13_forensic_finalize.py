"""Contextual corrections to first-pass source audit; original reviews preserved."""
from d13_experiment import *
from collections import Counter

def finalize(work=None, part_only=None):
 for w in ([work] if work else TAGS):
  paths=sorted((O/'forensics/reviews').glob(w+'_S*.json'))
  expected=[s['id'] for s in seg.load(w)['segments']]
  required=set(expected if part_only is None else expected[part_only*3:part_only*3+3])
  assert required<={p.stem.split('_')[-1] for p in paths},(w,'incomplete required audit',required)
  final=load(R/f'evaluations/synth/{TAGS[w]}_{w}/run.json')
  history=[h for v in final['state'].values() for h in v['hist']]
  scope=load(R/f'evaluations/pool/C25whole/{w}/manifest.json')['patterns']
  rows=[];quote_checks=[]
  for p in paths:
   d=load(p);source=load(O/f'forensics/inputs/{p.name}');actual_sec=source['sec'];raw={x['source']:x for x in source['original_drafts']}
   for t in d['targets']:
    matches={}
    for family,x in t['families'].items():
     sr=x.get('source');quote=x.get('quote','');found=raw.get(sr)
     exact=bool(found and quote and quote in json.dumps(found['current'],ensure_ascii=False))
     quote_checks.append({'work':w,'sec':actual_sec,'model_reported_sec':d.get('sec'),'target':t['index'],'family':family,'source':sr,'exact_quote_in_current':exact,'quote':quote})
     if found:matches[family]={'raw_current':found['current'],'prior_history':found['prior_history']}
    rows.append({'sec':actual_sec,'target':t,'best_source_contexts':matches})
  save(O/f'forensics/{w}_quote_checks.json',quote_checks)
  # Small section batches retain all source histories without truncation.
  secs=[s['id'] for s in seg.load(w)['segments']]
  for part in range((len(secs)+2)//3):
   if part_only is not None and part!=part_only:continue
   subset=set(secs[part*3:part*3+3])
   dst=O/f'forensics/{w}_context_part{part}.json'
   expected_targets={(x['sec'],x['target']['index']) for x in rows if x['sec'] in subset}
   assert expected_targets,('empty forensic target batch',w,part)
   if dst.exists():
    old=load(dst)
    if {(t['sec'],t['index']) for t in old.get('targets',[])}==expected_targets:continue
    rejected=O/'forensics/rejected';rejected.mkdir(exist_ok=True)
    archived=rejected/(dst.stem+'_'+sha(dst)[:12]+dst.suffix)
    if not archived.exists():shutil.copy2(dst,archived)
   pools={s:[{k:m.get(k) for k in ['id','text','premise','sources']} for m in load(O/f'forensics/inputs/{w}_{s}.json')['pool_mechanisms']] for s in sorted(subset)}
   evidence={'pool_source_patterns':scope,'actual_final_history':history,'pool_mechanisms':pools,'beads':[b for b in covjudge.beads(w) if b['sec'] in subset], 'rows':[x for x in rows if x['sec'] in subset]}
   prompt=CAL_RULES+'''\n复核上一轮来源审计的分类与原因，保留原审计但纠正上下文错误。当前旧池原本只接收d12*，因此D10/D11已有但不在池，先标source_scope_exclusion，不能冒称合并程序弄丢；D12同一机制被错误合并才叫bad_merge_loss。真正原池完整保留但未选且前提兼容，叫selection_not_used；原稿机制好但同一最终路径从未建立所需前提，叫history_incompatible。B/C主要叫generation_incomplete/generation_missing，也可同时有损耗。每项可有多个原因。
上一轮的final_prior_history字段空列表是未提供，不代表真实最终前史为空；这次给出全部真实最终History。只能引用早于当前sec的已建立事实。
纠正另一个常见错误：G25的机制不在D10/D11/D12里，并不等于G25伪因果。来源新颖性与因果有效性分开。只要G25自己当前已选前史成立且桥确有信息，就可以是有价值的新机制；不能因来源缺失判假。也不需要为每个合理心理影响再增加无限中间原因。对一条已有因果再要求解释每个“所以”的无限细分，同样会制造多余步骤。对G25价值的判断依据这次给的真实History与珠子，不把旧审计的负面标签直接照抄。
按前提结构+实质因果桥+当前结果做A/B/C，不以措辞完全一致作为标准；也不能因结果词相似判A。若G25多堆了一个没有实质增量的限定，不能为每个修饰词强行把原稿A降B。G25自身为空泛因果也要指出，不把它当标准答案。
逐字检查来源；源quote不完整时用给出的源原文复核。输出JSON {"targets":[{"sec":"S01","index":1,"class":"A|B|C","causes":["source_scope_exclusion"],"G25_valuable":true,"G25_defect":"无或具体缺陷","best_source":"...","source_quote":"逐字短引","why_same_or_missing":"...","history_compatibility":"已选前史能否满足，引用具体H及含义","pool_fate":"具体M号或来源范围排除","main_diagnosis":"..."}],"conclusion":"..."}。必须覆盖给定所有rows，不能补写机制。'''
   txt=prompt+'\n'+json.dumps(evidence,ensure_ascii=False)
   assert len(txt)<64000,(w,part,len(txt))
   j,rid=call('forensic_context_'+w+'_'+str(part),txt,model=evo.G56)
   assert {(t['sec'],t['index']) for t in j['targets']}=={(x['sec'],x['target']['index']) for x in evidence['rows']}
   save(dst,{'run_id':rid,'source_scope':scope,**j})

if __name__=='__main__':finalize(sys.argv[1] if len(sys.argv)>1 else None,int(sys.argv[2]) if len(sys.argv)>2 else None)
