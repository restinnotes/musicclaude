"""Lossless repair of trailing JSON commas only; never changes any string, field or verdict.
Raw model text is preserved byte for byte and the exact removed character offsets are recorded.
"""
import hashlib
import json
import sys
import evo
import judge_synth_v4

def trailing_commas(text):
 inside=False;escaped=False;remove=[]
 for i,c in enumerate(text):
  if inside:
   if escaped:escaped=False
   elif c=='\\':escaped=True
   elif c=='"':inside=False
  elif c=='"':inside=True
  elif c==',':
   j=i+1
   while j<len(text) and text[j].isspace():j+=1
   if j<len(text) and text[j] in '}]':remove.append(i)
 offsets=set(remove)
 return ''.join(c for i,c in enumerate(text) if i not in offsets),remove

def repair(rid):
 p=evo.RUNS/rid/'output.txt';raw=p.read_text(encoding='utf-8')
 try:judge_synth_v4.parse(raw);return False
 except json.JSONDecodeError:pass
 fixed,offsets=trailing_commas(raw)
 if not offsets:raise ValueError('not a trailing-comma-only problem')
 judge_synth_v4.parse(fixed)
 original=p.with_name('output_before_trailing_comma_repair.txt')
 if original.exists():raise ValueError('original repair snapshot already exists; inspect manually')
 original.write_bytes(p.read_bytes())
 receipt={'run_id':rid,'repair':'remove JSON trailing commas outside quoted strings only','removed_character_offsets':offsets,'raw_file':str(original),'raw_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),'repaired_text_sha256':hashlib.sha256(fixed.encode()).hexdigest(),'semantic_values_changed':False}
 p.write_text(fixed,encoding='utf-8');p.with_name('syntax_repair.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
 print(rid,'format-only commas removed',offsets,flush=True);return True

if __name__=='__main__':
 probe='{"note":"comma, } and escaped \\" quote", "pass":true,}'
 clean,positions=trailing_commas(probe)
 assert clean=='{"note":"comma, } and escaped \\" quote", "pass":true}' and len(positions)==1
 for rid in sys.argv[1:]:repair(rid)
