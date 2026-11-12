"""Preserve unread judge attempts and register explicit, identical-evidence recovery."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from prepare_reviews import ROLES
HERE=Path(__file__).resolve().parent
for job in ROLES:
    parent=HERE/'jobs'/(job+'-recovery01')
    old=json.loads((parent/'result.json').read_text(encoding='utf-8'))
    assert old['transport_success'] and 'INPUT_INCOMPLETE' in (parent/'response.md').read_text(encoding='utf-8')
    child=HERE/'jobs'/(parent.name+'-recovery02')
    child.mkdir(exist_ok=True)
    prompt=(parent/'prompt.txt').read_text(encoding='utf-8').replace(parent.name,child.name)
    (child/'prompt.txt').write_text(prompt,encoding='utf-8')
    (child/'attachments.json').write_bytes((parent/'attachments.json').read_bytes())
    row={'original_job_id':parent.name,'replacement_job_id':child.name,
         'replacement_prompt_sha256':hashlib.sha256((child/'prompt.txt').read_bytes()).hexdigest(),
         'reason':'Previous model explicitly reported INPUT_INCOMPLETE. Duplicate DOM file inputs selected inactive composer; small file-only sentinel proven readable after selecting active final general file input and requiring visible attachment chip.',
         'original_result_preserved':True,'evidence_pack_unchanged':True,
         'utc':datetime.now(timezone.utc).isoformat()}
    with (parent/'completion-resolution.json').open('x',encoding='utf-8') as f:json.dump(row,f,ensure_ascii=False,indent=2)
print('Four independent recoveries registered; exact immutable evidence retained')
