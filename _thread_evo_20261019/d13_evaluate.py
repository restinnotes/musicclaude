"""D13 evaluation and pool-only coherent path. Never supplies feedback to frozen drafts."""
from d13_experiment import *

EVAL=CAL_RULES+CAL_V2_EXTRA+'''
审查一条独立生成的Thread，音乐生成输入没有珠子；现在珠子只作验收。不要改稿或补写。
对每段因果增量做三格测试；核查所引History的实际文本、前提是否真被建立，不只看编号。新History若只是更在乎/更复杂/新分量，判无效；若靠音乐偷换外部事实，判无效。首段或延续不必强有历史因果，但不能由此宣布解释了所有体验。
每颗非演奏条件珠子标explained / compatible independent / alternative / gap。前三项是有着落的类型，gap是尚无充分着落的失败状态。explained必须给已有机制的具体增量与来源短引；只同义描述/抽象因果不能算explained。不因为侧面而忽略；段落核心大量只有compatible independent须判解释力不足。alternative须真的互斥，不能把没想到的核心随便扔掉。想象类比不是现实发生的事件。
对照本段G25和历史最佳局部价值：保住了哪个具体机制、没有哪个、是否回退；不是要求照抄G25，G25本身也可能伪因果。
输出JSON {"sections":[{"sec":"S01","causal_pass":true,"increment":{"new_fact":"...","bridge":"...","without":"..."},"invalid_history":[{"id":"H1","why":"..."}],"unsupported":[],"pseudo_causality":[],"core_pass":true,"coverage":[{"id":"S01-B1","status":"gap","quote":"来自稿件的逐字短引，缺就空","why":"..."}],"G25_mechanisms":[{"index":1,"independently_reproduced":false,"why":"同前提+桥+结果才算，不是结果词相似"}],"regressions":[],"why":"..."}],"path_coherent":true,"path_problems":[],"upstream_main_source_ready":false,"specific_prompt_failure":"..."}。
'''

def evaluator_dossier(d):
 w='op61' if '_op61_' in d['name'] else 'op60'; secids={x['sec'] for x in d['sections']}
 final=load(R/f'evaluations/synth/{TAGS[w]}_{w}/run.json')
 benchmarks=load(R/'evaluations/continuation_20261025/historical_local_inventory.json')
 old=[{'source':x['source'],'sections':{k:v for k,v in x['sections'].items() if k in secids}} for x in benchmarks[w] if x['source'].startswith('n8_') or x['source'] in ('b0_op60','60d','60f','61d','61f')]
 return {'draft':d,'beads':[b for b in covjudge.beads(w) if b['sec'] in secids and b['role']!='演奏条件'],
  'G25_comparison':{s:final['state'][s]['chosen'] for s in sorted(secids)},
  'non_regression_benchmarks':old,
  'note':'G25不是真值，必须同样做因果增量审查。未提供的后段不推测；这是前缀实验，不是全曲结论。'}

def draft_files(version='v1',long=False):
 ps=sorted((O/'drafts').glob(f'd13{version}*.json'))
 if long:return [p for p in ps if len(load(p)['sections'])>5]
 return [(O/'draft_prefixes/v2_op60_S01-S05'/p.name) if version=='v2' and (O/'draft_prefixes/v2_op60_S01-S05'/p.name).exists() else p for p in ps]

def evaluate(version='v1',long=False):
 passed=load(O/'calibration_v2'/f'{evo.G56}.json')['passed']; assert passed,'judge not calibrated'
 def one(p):
  d=load(p)
  if d.get('pipeline_valid') is False:return
  digest=sha(p)[:12]; dst=O/f'reviews_v2/{p.stem}_{digest}.json'
  if dst.exists():return
  j,rid=call('evaluate_'+p.stem+'_'+digest,EVAL+'\n'+json.dumps(evaluator_dossier(d),ensure_ascii=False))
  assert [s['sec'] for s in j['sections']]==[s['sec'] for s in d['sections']]
  w='op61' if '_op61_' in p.stem else 'op60'
  want={b['id'] for b in covjudge.beads(w) if b['sec'] in {s['sec'] for s in d['sections']} and b['role']!='演奏条件'}
  got=[c['id'] for s in j['sections'] for c in s['coverage']]
  assert len(got)==len(set(got)) and set(got)==want,(p.name,'coverage incomplete',want-set(got))
  save(dst,{'draft_path':str(p),'draft_sha256':sha(p),'run_id':rid,**j})
 with ThreadPoolExecutor(8) as ex:
  fs=[ex.submit(one,p) for p in draft_files(version,long)]
  for f in as_completed(fs):
   try:f.result()
   except Exception as e:print('EVAL FAILED',repr(e),flush=True)

def latest_review(p):
 xs=list((O/'reviews_v2').glob(p.stem+'_'+sha(p)[:12]+'.json'))
 return load(xs[0]) if xs else None

def pool_build(version='v1',work=None):
 for w in ([work] if work else TAGS):
  pools={}
  for p in [p for p in draft_files(version) if f'_{w}_' in p.stem]:
   d=load(p)
   if d.get('pipeline_valid') is False:continue
   review=latest_review(p)
   assert review,p
   hist=[]
   for x,j in zip(d['sections'],review['sections']):
    # One generated semantic mechanism per section; its fields are not expanded into graph nodes.
    m={'id':d['name']+'_'+x['sec'],'source':d['name'],'source_run':x['run_id'],'sec':x['sec'],
       'premise':x['why_now']['earlier_fact'],'mechanism':x['why_now']['bridge'],
       'current_result':x['why_now']['current'],'original_text':x['understanding'],
       'counterfactual':x['why_now']['without'],
       'history_requirements':[h for h in hist if h['id'] in x['used']],
       'adds_history':x['established_history'],'explains':[b['id'] for b in j['coverage'] if b['status']=='explained'],
       'coverage_review':j['coverage'],'causal_pass':j['causal_pass'],'core_pass':j['core_pass'],
       'invalid_history':j['invalid_history'],'unsupported':j['unsupported'],'pseudo_causality':j['pseudo_causality'],
       'review':j,'members':[d['name']+'_'+x['sec']]}
    # No semantic merging without evidence. Exact three-part+history equality only.
    pools.setdefault(x['sec'],[]).append(m)
    hist.extend(x['established_history'])
  for sec,ms in pools.items(): save(O/f'pools/{version}/{w}/{sec}.json',{'work':w,'sec':sec,'merge_policy':'no lossy merge; premise+bridge+result+history retained; no quota','mechanisms':ms})

SELECT=CAL_RULES+CAL_V2_EXTRA+'''
从独立Thread池选择一条历史自洽路径，禁止任何G25/新补缺/改写原因/移植未选前史。每段可选一个或多个真正相容的原始机制；只允许选给定ID，不改其文本。
机制的history_requirements必须逐项在前面已选机制的adds_history中由实质蕴含满足；来源自己的前史不能当最终路径已经经历。可以回头重选早段，不能为使后段可用而空降新历史。相似结论不代表同前提。没有合法选择时保留缺口；不要求每段新增事件。
可以选某个机制但不采用其无效History；未采用的History之后绝对不可用。若机制本身只依赖无效/外加前史，不能选。不得把伪因果当作解释。独立原稿已有的无效内容保留在池作失败证据，选择时拒绝。
逐颗珠子只依据实际选中机制判explained / compatible independent / alternative / gap，核心大量无因果须判失败。选中相容体验不自动提高解释覆盖。不要用兼容作垃圾桶。
这是有限池的可行路径搜索，不宣称数学最优。输出JSON {"sections":[{"sec":"S01","selected":["完整机制ID"],"requirement_mapping":[{"mechanism_id":"...","required_source_history_id":"H1","required_text":"...","established_by_mechanism":"前段ID","established_history_id":"H2","why_entailed":"..."}],"unused_invalid_history":[{"mechanism_id":"...","history_id":"...","why":"..."}],"coverage":[{"id":"S01-B1","status":"gap","mechanism_id":"有则列，没则空","why":"..."}],"core_pass":false,"why":"..."}],"path_coherent":true,"problems":[],"search_backtracking":"试过哪些真实备选，不捏造已经运行的搜索","scope":"prefix only","conclusion":"..."}。
'''
def path_select(version='v1',work=None):
 def one(w):
  pools=[load(p) for p in sorted((O/f'pools/{version}/{w}').glob('S*.json'))]
  # Keep all candidates, concise deterministic projection; raw text/requirements preserved, no review-target G25 input.
  keep=['id','sec','premise','mechanism','current_result','original_text','history_requirements','adds_history','causal_pass','invalid_history','unsupported','pseudo_causality']
  ps=[{'sec':p['sec'],'mechanisms':[{k:m[k] for k in keep} for m in p['mechanisms']]} for p in pools]
  secids={p['sec'] for p in ps}
  inp={'pools':ps,'beads':[b for b in covjudge.beads(w) if b['sec'] in secids and b['role']!='演奏条件']}
  txt=SELECT+'\n'+json.dumps(inp,ensure_ascii=False)
  assert len(txt)<64000,('path input too long',w,len(txt))
  j,rid=call('path_'+version+'_'+w,txt)
  validate_path_ids(j,pools,w)
  save(O/f'paths/{version}_{w}_selection.json',{'run_id':rid,'pool_hashes':{p.name:sha(p) for p in sorted((O/f'pools/{version}/{w}').glob('S*.json'))},**j})
 with ThreadPoolExecutor(2) as ex:list(ex.map(one,[work] if work else TAGS))

def validate_path_ids(j,pools,w):
 allm={m['id']:m for p in pools for m in p['mechanisms']}
 assert [s['sec'] for s in j['sections']]==[p['sec'] for p in pools]
 selected=set(); history=set()
 for s in j['sections']:
  for m in s['selected']:assert m in allm and allm[m]['sec']==s['sec'],m
  used={(x['mechanism_id'],x['history_id']) for x in s.get('unused_invalid_history',[])}
  for mapping in s['requirement_mapping']:
   assert mapping['mechanism_id'] in s['selected']
   assert (mapping['established_by_mechanism'],mapping['established_history_id']) in history,mapping
  for m in s['selected']:
   req=allm[m]['history_requirements']
   for h in req:assert any(a['mechanism_id']==m and a['required_source_history_id']==h['id'] for a in s['requirement_mapping']),(m,h)
   for h in allm[m]['adds_history']:
    if (m,h['id']) not in used:history.add((m,h['id']))
  selected.update(s['selected'])
  want={b['id'] for b in covjudge.beads(w) if b['sec']==s['sec'] and b['role']!='演奏条件'}
  got=[c['id'] for c in s['coverage']];assert set(got)==want and len(got)==len(want)
  for c in s['coverage']:
   if c['status']=='explained':assert c['mechanism_id'] in s['selected']

def path_verify(version='v1',work=None):
 assert load(O/'calibration_v2'/f'{evo.G6}.json')['passed'],'second judge not calibrated'
 def one(w):
  path=load(O/f'paths/{version}_{w}_selection.json')
  pools=[load(p) for p in sorted((O/f'pools/{version}/{w}').glob('S*.json'))]
  ms={m['id']:m for p in pools for m in p['mechanisms']}
  chosen=[ms[m] for s in path['sections'] for m in s['selected']]
  prompt=CAL_RULES+CAL_V2_EXTRA+'''\n独立反驳以下有限池选取路径。不准补写内容。检查所有requirement_mapping的实质蕴含，不能把同词/相容当已经建立；同源历史编号也不自动成立。核查遗漏要求、无效History、违背已选前史、语义与音乐偷换。逐颗重新给explained/compatible independent/alternative/gap，宁留缺口。输出JSON {"path_coherent":true,"problems":[],"sections":[{"sec":"S01","causal_pass":true,"core_pass":false,"coverage":[{"id":"...","status":"...","mechanism_id":"...","why":"..."}],"why":"..."}],"upstream_main_source_ready":false,"conclusion":"..."}。'''
  dossier={'selection':path,'selected_original_mechanisms':chosen,'beads':[b for b in covjudge.beads(w) if b['sec'] in {s['sec'] for s in path['sections']} and b['role']!='演奏条件']}
  j,rid=call('path_verify_'+version+'_'+w,prompt+'\n'+json.dumps(dossier,ensure_ascii=False),model=evo.G6)
  save(O/f'paths/{version}_{w}_verification.json',{'run_id':rid,**j})
 with ThreadPoolExecutor(2) as ex:list(ex.map(one,[work] if work else TAGS))

def table():
 rows=[]
 for p in sorted((O/'drafts').glob('*.json')):
  d=load(p)
  if d.get('pipeline_valid') is False:continue
  j=latest_review(p)
  if not j:continue
  coverage=[c for s in j['sections'] for c in s['coverage']]
  rows.append({'name':d['name'],'sections':len(d['sections']),'explained':sum(c['status']=='explained' for c in coverage),'total':len(coverage),'core_pass':sum(s['core_pass'] for s in j['sections']),'causal_pass':sum(s['causal_pass'] for s in j['sections']),'path_coherent':j['path_coherent'],'ready':j['upstream_main_source_ready'],'failure':j['specific_prompt_failure']})
 save(O/'experiment_summary.json',rows)
 print(json.dumps(rows,ensure_ascii=False,indent=1))

if __name__=='__main__':
 op=sys.argv[1];v=sys.argv[2] if len(sys.argv)>2 else 'v1';w=sys.argv[3] if len(sys.argv)>3 else None
 if op=='eval':evaluate(v)
 elif op=='eval_long':evaluate(v,long=True)
 elif op=='pool':pool_build(v,w)
 elif op=='path':path_select(v,w)
 elif op=='verify':path_verify(v,w)
 elif op=='table':table()
