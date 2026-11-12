"""Evidence and packaging checks, deliberately no proxy quality scoring."""
from pathlib import Path
import hashlib,json,re
from html.parser import HTMLParser
R=Path(__file__).resolve().parents[1]
def j(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s):return re.sub(r'[*`_]','',s).replace('\r\n','\n')
class HTML(HTMLParser):
 def __init__(self):super().__init__();self.chapters=[];self.ids=[];self.network=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='section' and a.get('class')=='bead':self.ids.append(a.get('id'))
  if tag=='button' and a.get('class')=='chapter':self.chapters.append(a.get('data-index'))
  if tag in ['script','img','link'] and any(a.get(k,'').startswith(('http:','https:','//')) for k in ['src','href']):self.network.append(a)
def main():
 beads=j(R/'editorial/FINAL_BEADS.json');trace=j(R/'editorial/FINAL_TRACE.json');units=j(R/'sources/units.json')
 manifest=j(R/'sources/SOURCE_MANIFEST.json')['sources'];allowed={s['src_id'] for s in manifest}
 assert len(allowed)==30
 segs=j(R/'sources/structure.json')['frozen_segments']; assert len(beads)==14
 checks=[]
 for i,(b,t,(rng,label)) in enumerate(zip(beads,trace,segs),1):
  assert b['segment']==t['segment']==f'S{i:02}'
  assert t['range']==rng and b['status']=='edited_release'
  assert t['reader_sha256']==hashlib.sha256(b['body'].encode()).hexdigest()
  assert b['sources']==t['adopted_sources']
  assert len(b['body'])>20
  assert not re.search(r'SRC-|WritingBlock|<box|校核|模型|UID',b['body'])
  pool=(R/f'production_context/pools/{b["segment"]}.txt').read_text(encoding='utf-8')
  for uid in b['sources']:
   assert uid in units and uid.rsplit('-U',1)[0] in allowed
   assert units[uid]['text'].strip() in pool
  for uid,q in t['quotes_verified_after_markdown_delimiter_normalization']:
   assert norm(q) in norm(units[uid]['text'])
  checks.append({'segment':b['segment'],'adopted_uid_occurrences':len(b['sources']),'reader_hash_verified':True})
 calls=j(R/'experiments/ACTUAL_CALLS.json')
 assert len(calls)==12, f'Expected 12 actual completed experiment calls, got {len(calls)}'
 callmap={x['job_id']:x for x in calls}
 assert all(x['status']=='ok' for x in calls),[(x['job_id'],x['status']) for x in calls]
 for x in calls:
  d=R/x['dir'];m=j(d/'metadata.json')
  assert sha(d/'prompt.txt')==x['prompt_sha256']
  # response is UTF8 text serialized by two different tools; require exact file bytes.
  assert sha(d/'response.txt')==m['response_sha256'],x['job_id']
 pairs=[('S02_G6_A_initial','S02_FLASH_A_28'),('S02_G6_A2_28','S02_FLASH_A2_28'),('S07_G6_A2_30','S07_FLASH_A2_30'),('S13_G6_A2_30','S13_FLASH_A2_30')]
 for a,b in pairs:assert callmap[a]['prompt_sha256']==callmap[b]['prompt_sha256'],(a,b)
 for s in manifest:assert sha(R/s['archive'])==s['actual_sha256']
 report_files=['READ_ME_FIRST.md','READER.md','BEAD_CONTENT_REVIEW.md','BEADS_INTERNAL.md','DIAGNOSIS.md','MODEL_METHOD_COMPARISON.md','SOURCES_AND_LIMITS.md','REPRODUCE.md','OLD_READER_CLEAN.md']
 missing=[]
 for name in report_files:
  data=(R/name).read_text(encoding='utf-8')
  assert 'TODO' not in data and '待填' not in data
  for target in re.findall(r'\]\(([^)]+)\)',data):
   target=target.strip('<>').split('#',1)[0]
   if not target or re.match(r'[a-z]+://',target,re.I) or re.match(r'[A-Za-z]:',target):continue
   if not (R/target).exists():missing.append((name,target))
 assert not missing,missing
 h=HTML();h.feed((R/'阅读与对照.html').read_text(encoding='utf-8'))
 assert h.ids==[f'S{i:02}' for i in range(1,15)] and len(h.chapters)==14 and not h.network
 forbidden={'SRC-gpt56w-int-1','SRC-gpt56w-web-1'}
 assert not any(u.rsplit('-U',1)[0] in forbidden or 'gpro' in u for b in beads for u in b['sources'])
 report={'source_files':30,'beads':14,'adopted_uid_occurrences':sum(len(x['sources']) for x in beads),'unique_adopted_uids':len({u for b in beads for u in b['sources']}),'original_quotes':sum(len(t['quotes_verified_after_markdown_delimiter_normalization']) for t in trace),'actual_successful_calls':len(calls),'identical_prompt_pairs':pairs,'checks':checks,'reader_html_external_assets':0,'top_level_markdown_links_verified':True,'quality_score':None,'note':'These are integrity checks, not claims that counts imply artistic quality.'}
 (R/'audits/FINAL_VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
 print(json.dumps({k:v for k,v in report.items() if k!='checks'},ensure_ascii=False))
if __name__=='__main__':main()
