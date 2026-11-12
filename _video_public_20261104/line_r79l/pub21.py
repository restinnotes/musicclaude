"""从看视频的体验倒查：原稿的精细体验在屏幕上还剩多少，线的要点落在句子哪里。全走 gpt3。
python pub21.py audit TAG_OP60_OP61 TAG_OP52     审计（op60、op61 两位评委，op52 一位）
python pub21.py sum                              汇总
"""
import json, re, sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import os
os.environ.setdefault('PUB_WORKS', 'op60,op61')
import pub2, pub3
from pub2 import JUDGES, call, parse, rd, wr
R3 = pub3.OUT; R2 = pub2.OUT; Q = R3/'audit21'; Q.mkdir(exist_ok=True)

AUDIT = """一首钢琴曲的“边听边看”视频。观众在听音乐，眼睛扫屏幕，不是专心读。屏幕每段有几条线（一个人经历的事）和散开的短词（听的人当下的感受）。

“原稿”是完整文字：珠子（听的人的感受）和线。“屏幕”是视频里实际显示的。

现在的争议：观众说线太啰嗦、抓不到要点；可也担心压缩时删掉的形容词、副词、句子中间的连接，其实才是最精细的体验所在。请逐段帮我们查清这两头，不要先入为主。

一、精细体验（fine）。每段从原稿挑 2–3 处“这段最精细、换个说法就没了”的体验。不要挑概括性的意思，要挑那种读到才会觉得“对，就是这个感觉”的地方。每处给：
- quote：原稿原文，尽量短，照抄
- carrier：这份精细主要靠什么撑着：形容词、副词、连接转折、比喻画面、身体感觉、具体的事、心里的话、句子节奏，选一个
- screen：屏幕上这份体验还在吗：在 / 变粗 / 没了。“变粗”指大意在，但那份精细没了
- matter：对扫屏幕的观众，丢了它损失大吗：大 / 小。扫读抓不到的细节可以判小
- fix：如果值得救，屏幕上最少加哪几个字能救回来；不值得救写空

二、线的要点（lines）。逐条看屏幕上的线：
- point：这条线真正要让人知道的那一点，从线里照抄最短的连续片段
- where：这个片段在句子哪里：前 / 中 / 后
- waste：这条线里拿掉也不伤意思和感觉的片段，照抄；没有写空
- keep：这条线里看着像废话，其实撑着感觉或因果的片段，照抄；没有写空

三、全局（overall）。三五句话：观众看完整首视频，脑子里能留下一条什么线索？哪些段之间本来有前后呼应，但屏幕上看不出来？最该改的是什么？

只输出 JSON：{"sections":[{"sec":"S01","fine":[{"quote":"…","carrier":"…","screen":"…","matter":"…","fix":"…"}],"lines":[{"text":"线的前几个字","point":"…","where":"…","waste":"…","keep":"…"}]}],"overall":"…"}

【屏幕】
{SCREEN}

【原稿】
{SOURCE}
"""


def source(w):
    rows = []
    for s in rd(R2/f'{w}_src.json')['sections']:
        rows.append(f"\n### {s['sec']}\n线：")
        rows += [f"- {l['text']}" for l in s['lines']]
        rows.append('珠子：')
        rows += [f"- {b['text']}" for b in s['beads']]
    return '\n'.join(rows)


def screen(w, tag):
    rows = []
    for s in rd(R3/f'script_{w}_{tag}.json')['sections']:
        rows.append(f"\n### {s['sec']}")
        for g in s['groups']:
            rows.append('线：'+' '.join(l['text'] for l in g.get('lines', []))+'\n  词：'+' / '.join(b['text'] for b in g.get('beads', [])))
    return '\n'.join(rows)


def audit(a):
    w, j, tag = a; p = Q/f'{w}_{j}_{tag}.json'
    if p.exists(): return
    msg = AUDIT.replace('{SCREEN}', screen(w, tag)).replace('{SOURCE}', source(w))
    for k in range(3):
        ans = call(f'pub21A_{w}_{j}_{tag}'+('' if not k else f'_r{k}'), msg, JUDGES[j], 'gpt3s', 'public21-audit')
        try:
            r = parse(ans); assert r['sections']; wr(p, r); print('完成', w, j, flush=True); return
        except Exception as ex: print('不合格', w, j, repr(ex)[:150], flush=True)


def summarize():
    for p in sorted(Q.glob('*.json')):
        r = rd(p); F = [f for s in r['sections'] for f in s.get('fine', [])]; L = [l for s in r['sections'] for l in s.get('lines', [])]
        lost = [f for f in F if f.get('screen') != '在' and f.get('matter') == '大']
        print(p.stem, '精细', len(F), dict(Counter(f.get('screen') for f in F)), '靠什么', dict(Counter(f.get('carrier') for f in F)))
        print('   丢了且损失大', len(lost), dict(Counter(f.get('carrier') for f in lost)), ' 线', len(L), '要点位置', dict(Counter(l.get('where') for l in L)), '可删占字', round(sum(len(l.get('waste') or '') for l in L)/max(1, sum(len(l.get('point') or '')+len(l.get('waste') or '')+len(l.get('keep') or '') for l in L)), 2), '要点均字', round(sum(len(l.get('point') or '') for l in L)/max(1, len(L)), 1))
        print('   ', r.get('overall', '')[:500])


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    if sys.argv[1] == 'audit':
        t, t52 = sys.argv[2:4]; jobs = [(w, j, t) for w in ('op60', 'op61') for j in JUDGES]+[('op52', 'g6', t52)]
        with ThreadPoolExecutor(5) as ex: list(ex.map(audit, jobs))
        summarize()
    else: summarize()
