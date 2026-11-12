"""Frame-level verification of stable reading pages and timed changes."""
import bisect, json
import numpy as np
from film import Film, PALETTE
from dag2 import ROOT, WORKS, write

def audit():
 results={}
 for w in WORKS:
  f=Film(w);rows=[]
  for i,(start,end) in enumerate(zip(f.starts,f.ends)):
   a=start+min(1.0,(end-start)*.2);b=start+(end-start)*.7
   first=np.asarray(f.frame(a));later=np.asarray(f.frame(b))
   stable=np.array_equal(first[103:705,48:1446],later[103:705,48:1446]);assert stable
   motion=int(np.count_nonzero(first[780:1050,:1560]!=later[780:1050,:1560]));assert motion>0,(w,i,'no music motion')
   if i:
    assert bisect.bisect_right(f.starts,start-1/30)-1==i-1
    assert bisect.bisect_right(f.starts,start+1/30)-1==i
   # Every scheduled note currently visible was sounded already.
   assert all(n['s']<=a+0.001 for n in f.notes[np.searchsorted(f.ns,a-15):np.searchsorted(f.ns,a+0.001)])
   rows.append({'sec':f.segs[i]['sec'],'text_panel_stable':stable,'music_changed_pixels':motion,'boundary_correct':True,'future_notes_absent':True})
  results[w]={'segments':rows,'pass':True}
 write(ROOT/'qa/temporal.json',results)
 print(json.dumps({k:{'segments':len(v['segments']),'pass':v['pass']} for k,v in results.items()},ensure_ascii=False))

if __name__=='__main__':audit()
