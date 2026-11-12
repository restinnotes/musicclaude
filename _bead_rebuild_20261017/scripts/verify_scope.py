from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]; Q=R.parent/'_bead_quality_20261017'; A=R.parent/'_bead_full_audit_20261017'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=read(Q/'sources/SOURCE_MANIFEST.json')['sources']
bad=[]
for s in manifest:
 p=Q/'sources'/(s['src_id']+'.md')
 if sha(p)!=s['sha256']:bad.append(s['src_id'])
u=read(Q/'sources/units.json'); rev=read(A/'ALL_UNIT_REVIEWS.json')
ledger=read(A/'ALL_MEANINGS.json'); units={x['uid'] for x in rev}
counts={}
for s in ['S'+str(i).zfill(2) for i in range(1,15)]:
 rows=[x for x in rev if x['segment']==s];counts[s]={'source_units_reviewed':len(rows),'meaning_rows':sum(x['segment']==s for x in ledger)}
out={'source_files':len(manifest),'source_hash_mismatches':bad,'raw_unique_units':len(u),'audit_unique_source_units':len(units),'unreviewed_raw_units':sorted(set(u)-units),'source_segment_dispositions':len(rev),'unique_source_segment_dispositions':len({(x['segment'],x['uid']) for x in rev}),'all_meaning_rows':len(ledger),'local_meaning_rows':sum(x['segment']!='GLOBAL' for x in ledger),'global_meaning_rows':sum(x['segment']=='GLOBAL' for x in ledger),'baseline_sha256':sha(Q/'editorial/FINAL_BEADS.json'),'baseline_hash_matches':sha(Q/'editorial/FINAL_BEADS.json')==read(R/'reference/BASELINE_HASH.json')['sha256'],'by_segment':counts,'limits':'全量指30份冻结原稿的来源、标题与原意账本覆盖；不表示原意提取不存在漏项。当前正文每个原意是否保留由COVERAGE及独立复核决定。'}
(R/'SCOPE_VERIFICATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
assert not bad and not out['unreviewed_raw_units'] and out['baseline_hash_matches']
print(json.dumps({k:v for k,v in out.items() if k!='by_segment'},ensure_ascii=False))
