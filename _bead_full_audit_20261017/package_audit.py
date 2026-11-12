import json,hashlib,zipfile,shutil
from pathlib import Path
R=Path(__file__).parent; B=Path(r'D:\musicclaude\_bead_quality_20261017')
v=json.loads((R/'VALIDATION.json').read_text(encoding='utf-8'))
assert not v['errors'], 'Do not package an incomplete audit'
ref=R/'reference';ref.mkdir(exist_ok=True)
for name,src in [('CURRENT_BEADS.json',B/'editorial/FINAL_BEADS.json'),('A_UNITS.json',B/'sources/units.json'),('SOURCE_MANIFEST.json',B/'sources/SOURCE_MANIFEST.json')]:shutil.copy2(src,ref/name)
sources=ref/'original_A';sources.mkdir(exist_ok=True)
manifest=json.loads((B/'sources/SOURCE_MANIFEST.json').read_text(encoding='utf-8'))
for s in manifest['sources']:shutil.copy2(B/s['archive'],sources/(s['src_id']+'.md'))
for name in ['CONNECTION_AUDIT.json','CONNECTION_AUDIT.md']:
 p=Path(r'D:\musicclaude\_bead_facets_20261017')/name
 if p.exists():shutil.copy2(p,R/name)
files=[p for p in R.rglob('*') if p.is_file() and not p.name.startswith('audit_') and not p.name.endswith('.py') and p.name not in ['DELIVERY_RECEIPT.json']]
archive=Path(r'C:\Users\zuoyi\Downloads\bead_full_content_audit_20261017.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,str(p.relative_to(R)))
receipt=dict(path=str(archive),bytes=archive.stat().st_size,sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),files=len(files),mother_sha256=v['mother_sha256'])
(R/'DELIVERY_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(receipt,ensure_ascii=False))
