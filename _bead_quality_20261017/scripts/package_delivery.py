"""Package the readable product and evidence, without browser/auth runtime state."""
from pathlib import Path
import json,hashlib,zipfile,sys
R=Path(__file__).resolve().parents[1]
def main():
 assert (R/'audits/FINAL_VALIDATION.json').exists(),'Run final validation before packaging'
 dest=Path.home()/'Downloads'/'bead_quality_20261017_deliverables.zip'
 assert not dest.exists(),'Destination exists; do not overwrite an earlier delivery'
 selected=[]
 dirs={'sources','prompts','pools','inputs','inputs_v2','production_context','snapshots','editorial','experiments'}
 call_files={'prompt.txt','response.txt','metadata.json','request.json','job.json','command.json','started.json','exit.txt'}
 for p in sorted(R.rglob('*')):
  if not p.is_file():continue
  rel=p.relative_to(R);parts=rel.parts
  if '__pycache__' in parts or 'preview_profile' in parts:continue
  include=False
  if len(parts)==1:include=p.suffix.lower() in {'.md','.json','.txt','.html'} or p.name=='FROZEN'
  elif parts[0] in dirs:include=p.suffix.lower() in {'.md','.json','.txt'}
  elif parts[0]=='audits':include=p.suffix.lower() in {'.md','.json','.txt','.html','.pdf','.png','.py'}
  elif parts[0]=='baseline_package':
   include=p.suffix.lower() in {'.md','.txt'} or (len(parts)>1 and parts[1]=='out' and p.suffix.lower()=='.json')
  elif parts[0]=='calls':include=len(parts)==3 and p.name in call_files
  elif parts[0]=='scripts':
   include=(len(parts)==2 and p.suffix.lower() in {'.py','.md','.json'}) or (len(parts)==4 and parts[1]=='call_results' and p.name in call_files)
  if include:selected.append(p)
 assert any(p.name=='READER.md' for p in selected)
 for p in selected:
  assert not any(x in p.parts for x in ['cwd','preview_profile','attachments','.venv-local'])
  assert p.name not in {'stdout.raw','stderr.raw','raw.json'}
 inventory=[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in selected]
 manifest=R/'DELIVERY_MANIFEST.json';manifest.write_text(json.dumps({'files':inventory,'excluded_runtime_state':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
 with zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in selected+[manifest]:z.write(p,'bead_quality_20261017/'+p.relative_to(R).as_posix())
 with zipfile.ZipFile(dest) as z:
  assert z.testzip() is None
  for f in inventory:assert hashlib.sha256(z.read('bead_quality_20261017/'+f['path'])).hexdigest()==f['sha256']
 digest=hashlib.sha256(dest.read_bytes()).hexdigest()
 receipt={'path':str(dest),'bytes':dest.stat().st_size,'sha256':digest,'files':len(selected)+1,'zip_crc_checked':True,'per_file_hash_checked':True}
 (R/'DELIVERY_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
 (dest.parent/(dest.name+'.sha256')).write_text(digest+'  '+dest.name+'\n',encoding='ascii')
 print(json.dumps(receipt,ensure_ascii=False))
if __name__=='__main__':main()
