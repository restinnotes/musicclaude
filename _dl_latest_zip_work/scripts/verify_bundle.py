#!/usr/bin/env python3
import json, hashlib, sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
M=json.loads((R/'jobs/manifest.json').read_text(encoding='utf-8'))
assert len(M['jobs'])==16
seen=set()
for j in M['jobs']:
 assert j['job_id'] not in seen
 seen.add(j['job_id'])
 a=(R/j['model_prompt_paths']['gpt6w']).read_bytes()
 b=(R/j['model_prompt_paths']['gpt56w']).read_bytes()
 assert a==b,(j['job_id'],'not byte identical')
 assert hashlib.sha256(a).hexdigest()==j['input_sha256']
 assert b and len(b)>250
print('OK: 16 paired jobs, 32 UTF-8 prompt files, identical-bytes, SHA256 matched.')
