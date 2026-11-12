"""线对定稿 8 票验收（新版前后座位平衡），两首分开看。python thread_fair.py TAG"""
import sys
from concurrent.futures import ThreadPoolExecutor
import pub2
from pub2 import FAIR, THREAD_DIMS, WORKS, thread_vote, wr
sys.stdout.reconfigure(encoding='utf-8')
tag = sys.argv[1]
with ThreadPoolExecutor(8) as ex: rows = [r for r in ex.map(lambda a: thread_vote(a[0], a[1], tag, a[2]), FAIR) if r]
res = {'tag': tag, 'votes': len(rows), 'rows': rows, 'by_work': {}}
for w in WORKS:
    rr = [r for r in rows if r['w'] == w]
    res['by_work'][w] = {'n': len(rr), 'new': sum(r['new_win'] for r in rr), 'nets': {k: sum(r['net'][k] for r in rr) for k in THREAD_DIMS}}
    print(w, res['by_work'][w], flush=True)
res['nets'] = {k: sum(r['net'][k] for r in rows) for k in THREAD_DIMS}; print('合计', res['nets'], '选新', sum(r['new_win'] for r in rows), '/', len(rows))
wr(pub2.OUT/f'thread_fair_{tag}.json', res)
