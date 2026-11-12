"""R31 分关盲比入口：只读 argv 里已生成的 tag，对 qurefs 走现有 screen_flow，不新增判定。"""
import json, sys
from concurrent.futures import ThreadPoolExecutor
import screen_flow as F
F.configure()
tags = sys.argv[1:]
with ThreadPoolExecutor(max_workers=len(tags)) as pool:
    results = dict(zip(tags, pool.map(lambda t: F.screen(t, 'qurefs'), tags)))
for t, d in results.items():
    b = d['blind']
    print(t, d['status'], f"{b['wins']}/{b['complete']}", b['net_sums'], d.get('next'), flush=True)
