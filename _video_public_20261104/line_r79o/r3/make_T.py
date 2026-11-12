"""11-07 上限实验 g68T：感受碎片照 g68C2Y 不动，屏幕上的线换回定稿线原文（按 from 对应，一条定稿线一行）。
用来回答：“为什么”“前后一件事”输，是不是因为屏幕线压缩丢了因果；线回到原文长度后，扫得动、抓要点会不会跟着掉。"""
import sys, copy; sys.path.insert(0, '..'); sys.stdout.reconfigure(encoding='utf-8')
from pub24 import rd, wr, R2, S, WORKS, to_script
for w in WORKS:
    src = {s['sec']: s for s in rd(R2/f'{w}_src.json')['sections']}; scr = copy.deepcopy(rd(S/f'screen_{w}_g68C2Y.json'))
    for sec in scr['sections']:
        ids = [l['id'] for l in src[sec['sec']]['lines']]; txt = {l['id']: l['text'] for l in src[sec['sec']]['lines']}
        used = set(); rows = []; lines_at = []
        for x in sec['rows']:
            if x['kind'] != 'line': rows.append(x); continue
            fr = [i for i in (x.get('from') or []) if i in txt and i not in used]
            if not fr: continue
            for i in fr:
                used.add(i); keys = [k for k in x.get('keys') or [] if k in txt[i] and not any(k in r.get('text', '') for r in rows if r['kind'] == 'line')]
                rows.append({'kind': 'line', 'text': txt[i], 'keys': keys, 'emotion': x.get('emotion'), 'from': [i]}); lines_at.append((i, len(rows)-1))
        for i in ids:   # 没被引用的定稿线：插到前一条已放的定稿线后面
            if i in used: continue
            prev = [p for j, p in lines_at if ids.index(j) < ids.index(i)]; pos = (max(prev)+1) if prev else 0
            rows.insert(pos, {'kind': 'line', 'text': txt[i], 'keys': [], 'emotion': '悬着', 'from': [i]}); used.add(i)
            lines_at = [(j, p+(p >= pos)) for j, p in lines_at]+[(i, pos)]
        sec['rows'] = rows
    wr(S/f'screen_{w}_g68T.json', scr); to_script(w, 'g68T', scr)
    L = [x['text'] for s in scr['sections'] for x in s['rows'] if x['kind'] == 'line']
    print(w, '线', len(L), '行', sum(map(len, L)), '字', '没有放大词的行', sum(not x.get('keys') for s in scr['sections'] for x in s['rows'] if x['kind'] == 'line'))
