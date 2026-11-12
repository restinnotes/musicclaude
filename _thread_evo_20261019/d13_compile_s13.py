"""Lossless family-audit union while the redundant model merge is unreturned."""
from d13_experiment import *
import copy

parts=[]
for family in ('d10','d11','d12'):
 paths=[p for p in evo.RUNS.glob('D13_forensic_op61_S13_'+family+'_*') if (p/'output.txt').exists()]
 assert len(paths)==1,(family,paths)
 p=paths[0];parts.append({'family':family,'run_id':p.name,'review':evo.parse_json(rd(p/'output.txt'))})
targets=[]
for index in (1,2):
 ts=[next(t for t in p['review']['targets'] if t['index']==index) for p in parts]
 priority={'A':0,'B':1,'C':2}
 best=min(ts,key=lambda t:priority[t['class']])
 t=copy.deepcopy(best)
 t['families']={family.upper():copy.deepcopy(next(x for x in ts if x['families'][family.upper()]['class']!='not_supplied')['families'][family.upper()]) for family in ('d10','d11','d12')}
 t['merge_note']='Deterministic best-existing-class union only; no new semantic adjudication. Context review separately corrects scope and causality.'
 targets.append(t)
dst=O/'forensics/reviews/op61_S13.json'
if not dst.exists():
 save(dst,{'run_id':None,'scope':'all_families_lossless_union','sec':'S13','assembled_by':'Codex deterministic extraction of completed family audits, not a new model result','parts':parts,'targets':targets,'merges':parts[-1]['review']['merges'],'section_conclusion':'Both D10 matches are A; D11/D12 near matches retained verbatim. D10 was excluded from the original d12-only pool. No model merge result is claimed.'})
print(dst)
