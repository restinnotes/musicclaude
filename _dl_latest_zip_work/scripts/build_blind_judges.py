#!/usr/bin/env python3
"""Build blind reviewer prompts from completed C JSON and the private legacy target. No model calls."""
import json,hashlib,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RULE=(ROOT/'prompts/D_BLIND_COMPARISON_v1.txt').read_text(encoding='utf-8')
def parse_json(s):
 try:return json.loads(s)
 except json.JSONDecodeError:
  s=re.sub(r'^```(?:json)?\s*|\s*```$','',s.strip())
  return json.loads(s)
index=[]
for k in [2,11,18,20,23]:
 inp=json.loads((ROOT/f'inputs/op60/C_k{k:02d}.json').read_text(encoding='utf-8'))
 old=(ROOT/f'private/legacy_target_k{k:02d}.txt').read_text(encoding='utf-8').split('\n\n',1)[1]
 for model,judge in [('gpt6w','gpt56w'),('gpt56w','gpt6w')]:
  p=ROOT/'results'/model/f'C{k:02d}.txt'
  if not p.exists():
   print(f'SKIP C{k:02d} {model}: no real result')
   continue
  try:
   obj=parse_json(p.read_text(encoding='utf8'))
   assert obj['station_k']==k and obj['task']=='C'
   screen=[item['text'] for item in obj['new_screen_items']]; assert isinstance(screen,list) and all(isinstance(s,str) for s in screen)
  except Exception as e:
   print('SKIP invalid',model,k,e);continue
  generated='\n'.join(f'- {s}' for s in screen) if screen else '(本段无新增内容)'
  # fixed keyed shuffle, no randomization leakage in prompt text
  generated_is_A=hashlib.sha256(f'{k}/{model}/fixed-20261009'.encode()).digest()[0]%2==0
  anonA,anonB=(generated,old) if generated_is_A else (old,generated)
  content=(RULE+f'\n【站点】k{k:02d} / {inp["meta"]["section_title"]}\n'
     +'【上一屏（固定状态）】\n'+json.dumps(inp['screen_before'],ensure_ascii=False,indent=2)
     +'\n【当前候选（仅作为证据，未核谱）】\n'+json.dumps(inp['current_candidates'],ensure_ascii=False,indent=2)
     +'\n【匿名版本 A】\n'+anonA+'\n【匿名版本 B】\n'+anonB+'\n')
  rel=f'jobs/d_blind/{judge}/D_k{k:02d}_vs_{model}.txt'
  dest=ROOT/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(content,encoding='utf8')
  index.append({'k':k,'generating_model':model,'judging_model':judge,'prompt_file':rel,
                'sha256':hashlib.sha256(content.encode()).hexdigest(),
                'generated_side':'A' if generated_is_A else 'B'})
if index:
 priv=ROOT/'private/judge_mapping_NOT_FOR_JUDGES.json'
 priv.write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(f'Generated {len(index)} blind D prompts; judge_mapping is private. Do not pass mapping into models.')
