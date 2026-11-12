#!/usr/bin/env python3
"""Offline immutable-prompt + repeated-plan consistency check. Never calls a model."""
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
m=json.loads((ROOT/'jobs/manifest.json').read_text(encoding='utf-8'))
p=json.loads((ROOT/'jobs/repetition_plan.json').read_text(encoding='utf-8'))
assert m['models']==['gpt6w','gpt56w']
assert p['models']=={'gpt6w':'gpt-6-thinking','gpt56w':'gpt-5-6-thinking'}
assert len(p['jobs'])==len(m['jobs'])==16
assert p['base_model_calls']==16*2*p['base_repeats']==160
assert p['judge_preselected_repeats']==[1,5]
for j,a in zip(m['jobs'],p['jobs']):
 assert j['job_id']==a['job_id'] and j['input_sha256']==a['input_sha256']
 for model in m['models']:
  f=ROOT/j['model_prompt_paths'][model]
  assert f.is_file()
  assert hashlib.sha256(f.read_bytes()).hexdigest()==j['input_sha256']
print('OK: 16 jobs; identical unchanged GPT prompts; r01–r05 = 160 potential calls; no live calls performed.')
