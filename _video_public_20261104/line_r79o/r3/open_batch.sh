#!/bin/bash
cd /d/musicclaude/_video_public_20261104/line_r79o
for t in "$@"; do python r3/open_review.py $t & done; wait
python - "$@" <<'PY'
import sys
from pub24 import S, rd
for t in ['g68K3M2'] + sys.argv[1:]:
    for w in ['op60', 'op61']:
        sev = {'严重': 0, '中等': 0, '轻微': 0}; n = 0
        for j in ['g6', 'g56']:
            p = S/f'open_{w}_{j}_{t}.json'
            if not p.exists(): continue
            r = rd(p); n += len(r.get('issues') or [])
            for c in r.get('cumulative') or []: sev[c.get('severity')] = sev.get(c.get('severity'), 0) + 1
        print(f'开放评审 {t} {w}：局部问题 {n}；跨段问题 严重 {sev["严重"]}、中等 {sev["中等"]}、轻微 {sev["轻微"]}', flush=True)
PY
echo "== 开放评审完"
