from pathlib import Path
from collections import Counter
import json,hashlib,re
R=Path(__file__).resolve().parents[1]; A=R.parent/'_bead_full_audit_20261017'; Q=R.parent/'_bead_quality_20261017'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def put(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def body(p):return p.get('intro','')+'\n\n'+'\n\n'.join(b.get('text','') for b in p['blocks'])
def main():
 pages=[]
 for name in ['early','pilots_editor','middle','late']:
  path=R/'drafts'/(name+'.json')
  if path.exists():pages.extend(read(path)['pages'])
 pages.sort(key=lambda p:p['segment'])
 for p in pages:
  if p['segment']=='S02':
   b=next(b for b in p['blocks'] if b['label']=='同一尾音的三次变化')
   b['visual']={'type':'three_steps','phrase':'第一次是安慰，第二次是犹豫，第三次已经有点疼。','steps':['第一次是安慰，','第二次是犹豫，','第三次已经有点疼。']}
 # Editorial corrections are separately logged, never patched into raw model responses.
 fixes=read(R/'EDITORIAL_FIXES.json') if (R/'EDITORIAL_FIXES.json').exists() else []
 for f in fixes:
  p=next(p for p in pages if p['segment']==f['segment'])
  if f.get('append_block'):p['blocks'].append(f['append_block']);continue
  b=next(b for b in p['blocks'] if b['id']==f['block_id']) if f.get('block_id') else p
  key=f.get('field','text'); assert f['old'] in b[key],f
  b[key]=b[key].replace(f['old'],f['new'])
 additions=read(R/'PILOT_ADDITIONS.json') if (R/'PILOT_ADDITIONS.json').exists() else []
 for a in additions:
  p=next(p for p in pages if p['segment']==a['segment'])
  b=next(b for b in p['blocks'] if b['id']==a['target_block'])
  b['text']+='\n\n'+a['text'];b['evidence']+=a['evidence']
 # Reviewed alternatives replace only their named section; raw drafts stay frozen.
 selection=read(R/'ACTIVE_VERSIONS.json') if (R/'ACTIVE_VERSIONS.json').exists() else {}
 for segment,filename in selection.get('pages',{}).items():
  candidate=next(p for p in read(R/filename)['pages'] if p['segment']==segment)
  pages=[candidate if p['segment']==segment else p for p in pages]
 final_fixes=read(R/'FINAL_EDITS.json') if (R/'FINAL_EDITS.json').exists() else []
 for f in final_fixes:
  p=next(p for p in pages if p['segment']==f['segment'])
  b=next(b for b in p['blocks'] if b['id']==f['block_id'])
  if f.get('remove_block'):
   p['blocks'].remove(b);continue
  assert f['old'] in b['text'],f
  b['text']=b['text'].replace(f['old'],f['new'])
  if f.get('extra_evidence'):b.setdefault('evidence',[]).extend(f['extra_evidence'])
 content={'version':1,'method':'source-first editing with explicit distinctions, separate semantic audit','pages':pages}
 put(R/'CONTENT.json',content)
 ledger=[x for x in read(A/'ALL_MEANINGS.json') if x['segment']!='GLOBAL']; old={x['id']:x for x in ledger}
 actual={}; reviewer_files=[]
 review_sources=selection.get('reviews')
 files=[R/f for f in review_sources] if review_sources else sorted((R/'reviews').glob('*semantic_review.json'))
 for f in files:
  obj=read(f); arr=obj.get('coverage',[])
  if not arr:continue
  reviewer_files.append(f.name)
  for x in arr:
   # Later explicitly selected review supersedes earlier review of the same IDs.
   x['review_file']=f.name;actual[x['id']]=x
 overrides=read(R/'COVERAGE_OVERRIDES.json') if (R/'COVERAGE_OVERRIDES.json').exists() else []
 for x in overrides:
  assert x['id'] in old;x['review_file']='main_editor_adjudication';actual[x['id']]=x
 cov=[]; errors=[]
 pm={p['segment']:p for p in pages}
 for o in ledger:
  x=actual.get(o['id'],dict(id=o['id'],segment=o['segment'],status='unreviewed',span='',reason='独立语义复核尚未完成。',block_ids=[])).copy()
  x['meaning']=o['meaning'];x['dimension']=o['dimension'];x['baseline_status']=o['status']
  for f in fixes+final_fixes:
   if x.get('review_file')=='main_editor_adjudication':continue
   if f.get('old') and f['old'] in (x.get('span') or '') and (not f.get('new') or f['old'] not in f['new'] or f['new'] not in x['span']):
    x['span']=x['span'].replace(f['old'],f['new']);x.setdefault('span_updated_after_editorial_fix',[]).append({'block':f.get('block_id'),'reason':f['reason']})
  if x['status']=='full' and not x.get('span'):errors.append({'type':'full_without_span','id':x['id']})
  if x.get('span') and x['span'] not in body(pm[x['segment']]):
   elsewhere=[p['segment'] for p in pages if x['span'] in body(p)]
   if elsewhere and (x['status']=='not_applicable' or x.get('preserved_in_segment') in elsewhere):x['span_segment']=elsewhere
   elif x['status']=='not_applicable':
    x['previous_cross_section_span']=x.pop('span');x['span']='';x['reason']+=' 当前段不适用；旧对应文字已被别段的后续编辑取代，不把旧句冒充当前正文。'
   else:errors.append({'type':'span_not_in_current','id':x['id'],'span':x['span']})
  cov.append(x)
 put(R/'COVERAGE.json',cov)
 units=read(Q/'sources'/'units.json');quotes=0
 for p in pages:
  for b in p['blocks']:
   for e in b.get('evidence',[]):
    quotes+=1
    if e['uid'] not in units:errors.append({'type':'unknown_uid','block':b['id'],'evidence':e});continue
    if e['quote'] not in units[e['uid']]['text']:
     pool=(Q/'production_context'/'pools'/(p['segment']+'.txt')).read_text(encoding='utf-8')
     # Restored original headings may live outside extracted unit body.
     match=re.search(r'(?ms)^\['+re.escape(e['uid'])+r'\].*?(?=^\[SRC-|\Z)',pool)
     if not match or e['quote'] not in match.group():errors.append({'type':'source_quote_not_exact','block':b['id'],'evidence':e})
 cm={x['id']:x for x in cov};groups=read(A/'CANONICAL_LOCAL_MEANINGS.json')
 relevant=[g for g in groups if g['dimension']!='音乐事实' and g['status'] not in ['pending','not_applicable']]
 counts=Counter();baseline=Counter(); group_rows=[]
 rank={'full':0,'partial':1,'altered':2,'omitted':3,'pending':4,'not_applicable':5,'unreviewed':6}
 for g in relevant:
  candidates=[cm[i] for i in g['canonical_members']]
  best=min(candidates,key=lambda x:rank.get(x['status'],9));counts[best['status']]+=1;baseline[g['status']]+=1
  group_rows.append({'canonical_members':g['canonical_members'],'baseline_status':g['status'],'new_status':best['status'],'best_id':best['id']})
 put(R/'FIXED_DENOMINATOR_COMPARISON.json',group_rows)
 summary={'fixed_baseline_assessed_canonical_experience_denominator':len(relevant),'baseline_counts':dict(baseline),'new_counts':dict(counts),'baseline_full_pct':round(100*baseline['full']/len(relevant),2),'new_full_pct':round(100*counts['full']/len(relevant),2),'note':'只在旧审计已可判断的同一858组比较；未复核/本轮待定位仍留分母，不能以改pending抬高比例。GLOBAL另列，事实98项不计体验。语义判定可被反驳，数字不等于艺术质量。'}
 baseline_hash=hashlib.sha256((Q/'editorial'/'FINAL_BEADS.json').read_bytes()).hexdigest()
 expected_hash=read(R/'reference'/'BASELINE_HASH.json')['sha256']
 if baseline_hash!=expected_hash:errors.append({'type':'baseline_changed'})
 report={'page_count':len(pages),'unique_segments':len(pm),'content_sha256':hashlib.sha256((R/'CONTENT.json').read_bytes()).hexdigest(),'baseline_unchanged':baseline_hash==expected_hash,'source_quote_count':quotes,'local_ledger_rows':len(ledger),'independently_reviewed_rows':len(actual),'review_files':reviewer_files,'errors':errors,'coverage_summary':summary,'by_segment':{p['segment']:{'characters':len(body(p)),'blocks':len(p['blocks']),'statuses':dict(Counter(x['status'] for x in cov if x['segment']==p['segment']))} for p in pages}}
 put(R/'VALIDATION.json',report)
 print(json.dumps({'pages':len(pages),'reviewed':len(actual),'errors':len(errors),'coverage':summary},ensure_ascii=False))
if __name__=='__main__':main()
