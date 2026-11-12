"""对已写好的 w6 补跑去重，再标音符、上色、判交界。"""
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent)); sys.stdout.reconfigure(encoding='utf-8')
import pub3, pub7, pub9, pub11
from pub2 import WORKS, rd, wr

TAG = sys.argv[1]
for w in WORKS:
    p = pub3.OUT/f'script_{w}_{TAG}.json'; d = rd(p); n = pub11.dedupe(d); wr(p, d); print(w, '去重', n, flush=True)
with ThreadPoolExecutor(6) as ex:
    fm = ex.submit(pub3.marks, TAG)
    fm.result()
    list(ex.map(pub7.one, [(w, TAG) for w in WORKS])); list(ex.map(pub9.one, [(w, TAG) for w in WORKS]))
print('完成', flush=True)
