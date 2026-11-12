"""Evidence bundle: original responses, causal audits, no UI or new music finalization."""
from d13_experiment import *
from d13_evaluate import latest_review,draft_files
from collections import Counter
import zipfile
from datetime import datetime,timezone

DEST=Path('C:/Users/zuoyi/Documents/Codex/2026-10-25/n-n/outputs')

def summarize():
 rows=[];details=[]
 sources=[]
 for version in ('v1','v2','v3','v4','v5','v6','v7','v8'):
  sources.extend(draft_files(version))
  if version=='v2':sources.extend(draft_files(version,long=True))
 for p in sources:
  d=load(p)
  if d.get('pipeline_valid') is False:continue
  j=latest_review(p)
  if not j:continue
  cs=[c for s in j['sections'] for c in s['coverage']]
  counts=Counter(c['status'] for c in cs)
  rows.append({'name':d['name'],'version':d['version'],'variant':d['variant'],'repeat':d['repeat'],'work':'op61' if '_op61_' in d['name'] else 'op60',
   'scope':'long_distance' if len(d['sections'])>5 else 'prefix','sections':len(d['sections']),'explained':counts['explained'],'compatible_independent':counts['compatible independent'],'alternative':counts['alternative'],'gap':counts['gap'],'total':len(cs),
   'causal_pass_sections':sum(s['causal_pass'] for s in j['sections']),'core_pass_sections':sum(s['core_pass'] for s in j['sections']),
   'path_coherent':j['path_coherent'],'ready':j['upstream_main_source_ready'],'failure':j['specific_prompt_failure']})
  for s in j['sections']:details.append({'draft':d['name'],'sec':s['sec'],'core_pass':s['core_pass'],'causal_pass':s['causal_pass'],'regressions':s['regressions'],'g25_comparison':s['G25_mechanisms'],'coverage':s['coverage']})
 save(O/'experiment_summary.json',rows);save(O/'section_comparison.json',details)
 fs=[]
 for w in TAGS:
  contextual={}
  for p in sorted((O/'forensics').glob(w+'_context_part*.json')):
   for t in load(p)['targets']:
    contextual[(t['sec'],t['index'])]=t
  for p in sorted((O/'forensics/reviews').glob(w+'_S*.json')):
   original=load(p);sec=p.stem.split('_')[-1]
   for first in original['targets']:
    key=(sec,first['index'])
    if key in contextual:
     fs.append({'work':w,**contextual[key],'review_status':'context_review_complete','families':first['families']})
    else:
     fs.append({'work':w,'sec':sec,'index':first['index'],'class':first['class'],
      'review_status':'first_pass_provisional_context_review_missing',
      'causes':[first.get('cause','unresolved')],'G25_valuable':first.get('valuable'),
      'main_diagnosis':first.get('why',''),'G25_defect':first.get('g25_weaknesses',[]),
      'families':first['families']})
 save(O/'G25_source_attribution.json',fs)
 for file,records in [('D13_重复实验.csv',rows),('G25_逐机制来源诊断.csv',fs)]:
  if not records:continue
  with (O/file).open('w',newline='',encoding='utf-8-sig') as f:
   keys=list(dict.fromkeys(k for r in records for k in r));wr=csv.DictWriter(f,fieldnames=keys);wr.writeheader()
   for row in records:wr.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in row.items()})
 print('SUMMARY',len(rows),'reviewed drafts;',sum(x['explained'] for x in rows),'explained ratings;',sum(x['ready'] for x in rows),'ready')
 print('ATTRIBUTION',dict(Counter(t['class'] for t in fs)),len(fs))

def provenance():
 records=[];generation=[]
 for d in sorted(evo.RUNS.glob('D13_*')):
  cp=d/'call.log'
  if not cp.exists():
   failures=[load(p) for p in d.glob('call_fail*')];records.append({'run_id':d.name,'success':False,'failure_evidence_files':[str(p) for p in d.glob('call_fail*')],'submitted':any(x.get('submitted') for x in failures)});continue
  c=load(cp);job=Path(c['job_directory']);result=load(job/'result.json');text=rd(job/'response.txt')
  assert c['completed'] and result.get('ok') is True,(d.name,'not completed')
  assert c['model']==result['model'] and c['thinking_effort']=='max' and result['thinkingEffort']=='max'
  assert rd(d/'output.txt').strip()==text.strip(),(d.name,'response mismatch')
  assert rd(d/'input.txt').strip()==rd(job/'prompt.txt').strip(),(d.name,'prompt mismatch')
  records.append({'run_id':d.name,'success':True,'model':c['model'],'thinking_effort':c['thinking_effort'],'job_directory':str(job),'input_sha256':sha(d/'input.txt'),'response_sha256':sha(d/'output.txt'),'attach':c.get('attach',[]),'seconds':c['seconds']})
  if c.get('meta',{}).get('key','').startswith('d13v'):
   assert c['model']==evo.G56 and not c.get('attach'),d.name
   generation.append(records[-1])
 assert len({r['job_directory'] for r in generation})==len(generation),'different generation samples share same backend task'
 for x in load(O/'frozen_outputs.json'):assert sha(x['path'])==x['sha256'],('frozen artifact changed',x['path'])
 # Replication equality at S01; later input histories may legitimately differ.
 repetitions=[]
 for version in ['v1','v2','v3','v4','v7']:
  for w in TAGS:
   for var in VAR:
    ps=sorted((O/'drafts').glob(f'd13{version}{var}_56_{w}_r*.json'))
    if len(ps)<3:continue
    firsts=[load(p)['sections'][0] for p in ps]
    hashes={x['input_sha256'] for x in firsts};assert len(hashes)==1,(version,w,var,'first inputs differ')
    jobs=[load(evo.RUNS/x['run_id']/'call.log')['job_directory'] for x in firsts];assert len(set(jobs))==len(jobs)
    goal=5 if w=='op60' else 3
    repetitions.append({'version':version,'work':w,'variant':var,'repeats_started':len(ps),
     'prefix_target_sections':goal,'completed_prefix_repeats':sum(len(load(p)['sections'])>=goal for p in ps),
     'actual_section_counts':{p.stem:len(load(p)['sections']) for p in ps},
     'same_first_input_sha256':next(iter(hashes)),'independent_backend_jobs':len(set(jobs))})
 save(O/'provenance_verification.json',{'created_at':datetime.now(timezone.utc).isoformat(),'verified_calls':records,'generation_calls':len(generation),'generation_model':evo.G56,'distinct_generation_tasks':len(generation),'replication_checks':repetitions,'old_semantics_and_graphs_frozen':True})
 print('PROVENANCE',len(records),len(generation),'generation samples; all frozen originals unchanged')

def bundle():
 summarize();provenance()
 stage=Path('C:/Users/zuoyi/Documents/Codex/2026-10-25/n-n/work/d13_delivery');stage.mkdir(exist_ok=True)
 root=stage/'D13_独立上游实验_20261025';root.mkdir(exist_ok=True)
 def copy(src,rel):
  dst=root/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
 for p in O.rglob('*'):
  if p.is_file() and p.suffix.lower() in ('.json','.txt','.csv','.md','.png'):copy(p,Path('01_本轮实验')/p.relative_to(O))
 for pattern in ('d13*.py','d13*.cmd'):
  for p in R.glob(pattern):copy(p,Path('02_运行代码')/p.name)
 for name in ('evo.py','seg.py','covjudge.py'):
  copy(R/name,Path('02_运行代码/共用运行器')/name)
 for w,p in SCORES.items():copy(p,Path('07_独立乐谱输入')/(w+p.suffix))
 copy(R/'PLAN_D13_20261025.md',Path('02_运行代码/PLAN_D13_20261025.md'))
 for pattern in ['d13*.log']:
  for p in (R/'logs').glob(pattern):copy(p,Path('03_运行日志')/p.name)
 for d in evo.RUNS.glob('D13_*'):
  for p in d.iterdir():
   if p.is_file() and (p.suffix in ('.json','.txt','.log')):copy(p,Path('04_实际模型输入输出')/d.name/p.name)
  if (d/'call.log').exists():
   job=Path(load(d/'call.log')['job_directory'])
   for name in ['result.json','prompt.txt','response.txt','attachment-manifest.json']:
    if (job/name).exists():copy(job/name,Path('05_后台任务成功证据')/d.name/name)
  else:
   for fp in d.glob('call_fail*.log'):
    item=load(fp)
    if not item.get('job_directory'):continue
    job=Path(item['job_directory'])
    for name in ('result.json','generation-network.json','topic-network.json','generation-policy.json','submitted.json','started.json'):
     if (job/name).exists():copy(job/name,Path('05b_后台任务失败证据')/d.name/job.name/name)
 # Preserve network/result summaries of jobs interrupted at the earlier stop,
 # including jobs for which the outer caller never got to write call_fail.
 audit=O/'interruption_audit.json'
 if audit.exists():
  for item in load(audit)['jobs']:
   if item['code']=='SUCCESS':continue
   job=Path(item['result_path']).parent
   for name in ('result.json','generation-network.json','topic-network.json','generation-policy.json','submitted.json','started.json'):
    if (job/name).exists():copy(job/name,Path('05b_后台任务失败证据/暂停时后台记录')/item['account']/job.name/name)
 for p in (R/'evaluations/draft10').glob('d1*.json'):copy(p,Path('06_旧稿对照/独立原稿')/p.name)
 for p in (R/'evaluations/pool/C25whole').rglob('*.json'):copy(p,Path('06_旧稿对照/原解释池')/p.relative_to(R/'evaluations/pool/C25whole'))
 for w,t in TAGS.items():
  copy(R/f'evaluations/synth/{t}_{w}/run.json',Path(f'06_旧稿对照/G25逐段综合/{w}.json'))
  copy(R/f'evaluations/continuation_20261025/finalization/{t}_{w}_plain.json',Path(f'06_旧稿对照/冻结最终图/{w}.json'))
 for name in ['historical_local_inventory.json','non_regression_values.json']:
  copy(R/'evaluations/continuation_20261025'/name,Path('06_旧稿对照')/name)
 for name in ['draft10.py','draft11.py','draft12.py','pool.py','pool_v2.py','PLAN_解释池_20261023.md','PLAN_逐段构建线_20261023.md']:
  copy(R/name,Path('06_旧稿对照/旧提示词与计划')/name)
 # Standalone report is authored after reviewing the actual results.
 report=DEST/'D13_实验报告_20261025.txt'
 if report.exists():copy(report,Path('00_先读实验报告.txt'))
 manifest=[{'path':str(p.relative_to(root)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(root.rglob('*')) if p.is_file() and p.name!='文件清单与SHA256.json']
 save(root/'文件清单与SHA256.json',manifest)
 target=DEST/'D13_上游机制与历史路径_实验记录_20261025.zip'
 with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(root.rglob('*')):
   if p.is_file():z.write(p,str(p.relative_to(stage)))
 with zipfile.ZipFile(target) as z:
  assert z.testzip() is None
  for m in manifest:assert hashlib.sha256(z.read(root.name+'/'+m['path'])).hexdigest()==m['sha256']
 digest=sha(target);Path(str(target)+'.sha256').write_text(digest+'  '+target.name+'\n',encoding='utf-8')
 for name in ['D13_重复实验.csv','G25_逐机制来源诊断.csv','experiment_summary.json','provenance_verification.json','section_comparison.json']:
  if (O/name).exists():shutil.copy2(O/name,DEST/name)
 save(O/'delivery_receipt.json',{'path':str(target),'bytes':target.stat().st_size,'files':len(manifest)+1,'sha256':digest})
 print('DELIVERY',target,target.stat().st_size,len(manifest)+1,digest)

if __name__=='__main__':
 if sys.argv[1]=='summary':summarize()
 elif sys.argv[1]=='provenance':provenance()
 else:bundle()
