from pathlib import Path
import hashlib,json,shutil,zipfile
R=Path(__file__).resolve().parents[1];A=R.parent/'_bead_full_audit_20261017';Q=R.parent/'_bead_quality_20261017'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
shutil.copyfile(A/'完整内容审计.html',R/'原稿与旧版全量审计.html')
for name in ['ALL_MEANINGS.json','ALL_MERGES.json','ALL_UNIT_REVIEWS.json','CANONICAL_LOCAL_MEANINGS.json','CANONICAL_GROUPS.json','HEADING_SEMANTIC_REVIEW.json','统计口径.txt']:
 shutil.copyfile(A/name,R/'reference'/('baseline_'+name))
# Bundle the exact source and input material needed to inspect all claims.
(R/'reference/original_A').mkdir(parents=True,exist_ok=True)
for f in (Q/'sources').glob('SRC-*.md'):shutil.copyfile(f,R/'reference/original_A'/f.name)
for f in ['SOURCE_MANIFEST.json','units.json']:shutil.copyfile(Q/'sources'/f,R/'reference'/f)
v=json.loads((R/'VALIDATION.json').read_text(encoding='utf-8'))
assert v['page_count']==14 and v['unique_segments']==14 and not v['errors'] and v['baseline_unchanged']
assert v['independently_reviewed_rows']==v['local_ledger_rows'], 'Do not package incomplete semantic review as complete.'
files=[]
for p in R.rglob('*'):
 if not p.is_file() or '__pycache__' in p.parts:continue
 rel=p.relative_to(R)
 if p.suffix in ['.png','.zip','.raw'] or 'cwd' in rel.parts:continue
 # The reusable runner stays local; package exact job inputs, responses and safe metadata.
 if p.name=='run_calls.py':continue
 files.append(p)
receipt={'content_sha256':sha(R/'CONTENT.json'),'coverage_sha256':sha(R/'COVERAGE.json'),'validation':v,'files':[{'path':str(p.relative_to(R)),'sha256':sha(p)} for p in files]}
(R/'DELIVERY_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
destination=Path.home()/'Downloads'/'船歌_内容恢复与全量复核_20261018.zip'
with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED) as z:
 for p in files+[R/'DELIVERY_RECEIPT.json']:z.write(p,Path(R.name)/p.relative_to(R))
print(json.dumps({'path':str(destination),'bytes':destination.stat().st_size,'files':len(files)+1,'sha256':sha(destination)},ensure_ascii=False))
