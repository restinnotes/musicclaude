from pathlib import Path
import json, hashlib, zipfile

root=Path(__file__).resolve().parents[1]
target=Path(r'C:\Users\zuoyi\Downloads\bead_video_review_20261017.zip')
assert not target.exists(), 'refuse to overwrite delivery'
check=json.loads((root/'audits/COMBINED_VALIDATION.json').read_text(encoding='utf-8'))
assert not check['quote_failures']
assert check['families']==213
assert json.loads((root/'audits/PREVIEW_CHECK.json').read_text(encoding='utf-8'))['passed']
baseline=Path(r'D:\musicclaude\_bead_quality_20261017\editorial\FINAL_BEADS.json')
assert hashlib.sha256(baseline.read_bytes()).hexdigest()=='3f140a066e7ff2b9e4e9abf9ced1cd07f29b8ae535645c6ad84700b6c9484a8d'
assert baseline.read_bytes()==(root/'reference/FINAL_BEADS_UNCHANGED.json').read_bytes()
files=sorted(p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in ('DELIVERY_MANIFEST.json','DELIVERY_RECEIPT.json'))
manifest={'files':[{'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files], 'base_mother_unchanged':True,'purpose':'semantic audit and display study; no audio synchronization'}
mp=root/'DELIVERY_MANIFEST.json'
mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
    for p in files+[mp]:z.write(p,p.relative_to(root).as_posix())
with zipfile.ZipFile(target) as z:
    assert z.testzip() is None
    for row in manifest['files']:
        assert hashlib.sha256(z.read(row['path'])).hexdigest()==row['sha256'], row['path']
sha=hashlib.sha256(target.read_bytes()).hexdigest()
target.with_suffix('.zip.sha256').write_text(sha+'  '+target.name+'\n',encoding='utf-8')
receipt={'path':str(target),'bytes':target.stat().st_size,'files':len(files)+1,'sha256':sha,'crc_verified':True,'all_member_hashes_verified':True}
(root/'DELIVERY_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False,indent=2))
