"""One real G3 blind review; reuse its normal ID and all completion protections."""
import os
import sys
from pathlib import Path

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
os.environ.update(THREAD_ROUTE='mimic',MG_GLOBAL='1',MG_SLOTS='1',MG_ATTEMPTS='1',JV='2',ONLY_W='op60')
import mg_schedule
import v6fix as V

mg_schedule.check()
V.JUDGES={'g6':V.evo.G6}
V.blind('r26g3','qu')
rid='v6b2_op60_g6_r26g3_vsqu'
if not V.evo.done(rid):
    raise SystemExit('Actual review has no verified complete result; inspect remote failure, do not duplicate')
print('ACTUAL_VERIFIED_COMPLETE',rid,flush=True)
