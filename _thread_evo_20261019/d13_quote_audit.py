"""Read-only source quote check; outer quote marks are formatting, not source text."""
from d13_experiment import *
from collections import Counter

def unwrap(text):
 text=text.strip()
 pairs={'“':'”','「':'」','『':'』','‘':'’','"':'"',"'":"'"}
 while len(text)>1 and pairs.get(text[0])==text[-1]:text=text[1:-1].strip()
 return text

def run():
 result=[]
 for w in TAGS:
  for p in sorted((O/'forensics/reviews').glob(w+'_S*.json')):
   source=load(O/'forensics/inputs'/p.name)
   raw={x['source']:x for x in source['original_drafts']}
   for t in load(p)['targets']:
    for family,match in t['families'].items():
     name=match.get('source');quote=match.get('quote','');found=raw.get(name)
     # Search actual field values, rather than JSON escaping or metadata keys.
     def strings(value):
      if isinstance(value,str):return [value]
      if isinstance(value,list):return [s for item in value for s in strings(item)]
      if isinstance(value,dict):return [s for item in value.values() for s in strings(item)]
      return []
     texts=strings(found['current'])if found else []
     normalized=unwrap(quote)
     strict=bool(quote and any(quote in s for s in texts))
     formatted=bool(normalized and any(normalized in s for s in texts))
     result.append({'work':w,'sec':source['sec'],'index':t['index'],'family':family,'source':name,
      'original_quote':quote,'formatting_only_normalized_quote':normalized,
      'strict_match':strict,'match_after_outer_quote_removal':formatted,
      'status':'exact'if strict else 'outer_quote_formatting_only'if formatted else 'needs_review'})
 ex_counts=Counter(x['status']for x in result)
 save(O/'forensics/source_quote_verification_v2.json',{'operation':'offline string verification; no semantic rewrites, no new model calls','counts':dict(ex_counts),'checks':result})
 print('SOURCE QUOTES',dict(ex_counts),'total',len(result))

if __name__=='__main__':run()
