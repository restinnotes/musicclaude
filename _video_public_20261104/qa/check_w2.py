import sys, traceback
sys.path.insert(0,'.'); sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
import pub2, pub3
R=Path('../_thread_evo_20261019/runs')
for w in ['op60','op61']:
    for name in [f'pub3_write_{w}_w2', f'pub3_write_{w}_w2_fix2']:
        t=(R/name/'output.txt').read_text(encoding='utf-8')
        print(name,len(t),repr(t[:60]),repr(t[-60:]))
        try:
            d=pub2.parse(t); print(' parse ok', len(d.get('sections',[])))
            d=pub2.tidy_keys(d); print(' tidy',type(d))
            e=pub3.check(w,d); print(' check',len(e),e[:6])
        except Exception:
            print(traceback.format_exc()[-600:])
