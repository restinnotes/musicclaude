#!/usr/bin/env python3
"""Verify that package preserves 14 segments, 51 beads, and baseline text."""
import json, re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
d=json.loads((root/'03_Bead机器可读'/'14段_STRUCT轻量版.json').read_text(encoding='utf-8'))
s=d['segments']
assert len(s)==14, len(s)
assert sum(len(x['beads']) for x in s)==51
assert [(x['mm_start'],x['mm_end']) for x in s]==[(1,3),(4,16),(17,23),(24,34),(35,39),(40,50),(51,61),(62,71),(72,77),(78,83),(84,92),(93,102),(103,110),(111,116)]
for x in s:
    item=json.loads((root/'03_Bead机器可读'/f"{x['segment']}.json").read_text(encoding='utf-8'))
    assert item == x
    for b in x['beads']:
        assert b['text']
        assert b['id']
        assert b['text'] in (root/'02_Bead精简输入'/'D4_五十一条完整Bead.md').read_text(encoding='utf-8')
    assert x['reader'] in (root/'02_Bead精简输入'/'D3_十四段reader.md').read_text(encoding='utf-8')
p0=(root/'01_提示词与基准'/'P0_纯提示词_直接调用.txt').read_text(encoding='utf-8')
assert p0.startswith('Thread 是沿着既定段落')
assert p0.strip().endswith('为什么在当前段落会感受到这个')
b=(root/'01_提示词与基准'/'B0_成功范例_水面从来不答应静止.md').read_text(encoding='utf-8')
assert len(re.findall(r'^## 第',b, re.M)) == 15
print('PASS: 14 segment boundaries, 51 bead texts, 14 reader texts, P0 and full B0 archive')
