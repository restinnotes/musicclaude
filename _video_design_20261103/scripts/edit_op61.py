# 《幻想波兰舞曲》开头约两分半：检验同一套画面语言能否换一首曲子。摘句同样逐字核对。
import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')
EVO = r'D:\musicclaude\_thread_evo_20261019'
parsed = json.load(open('r54weave_parsed.json', encoding='utf-8'))['op61']
music = json.load(open('work/op61_music_v3.json', encoding='utf-8'))
BARS = {int(k): float(v) for k, v in music['bars']}
DUR = float(music['dur'])
graph = json.load(open(EVO + r'\evaluations\v6fix\op61_r54weave.json', encoding='utf-8'))['graph']
ALL = [x['text'] for s in parsed for x in s['beads']]
def tb(b):
    k = int(b); t0 = BARS.get(k, DUR); t1 = BARS.get(k + 1, DUR)
    return t0 + (b - k) * (t1 - t0)
def P(bar, text, hue, kind='top', span=1.0, d=None):
    if not any(text in b for b in ALL):
        raise SystemExit('不是珠子原文：' + text)
    return dict(t=tb(bar), d=d or max(3.4, len(text) / 3.6), text=text, hue=hue, sel=[tb(bar), tb(bar + span), kind])
# 颜色的含义按这首的 Center 换：蓝=尊严（挺直、不认输），金=怀念（旧日、亲近），玫=失落
PH = [
    P(1, '沉重、郑重的和弦', 'blue', 'all', 0.05),
    P(1.25, '像烟雾往高处散', 'blue', 'lh', 0.75),
    P(3, '短句像叹息，刚冒出来就被长停顿截断', 'rose', 'all', 1.0, d=5),
    P(5, '余音在冰冷的空气里慢慢散尽', 'rose', 'all', 1.0),
    P(7.3, '强迫自己挺直背脊', 'blue', 'lh', 0.7),
    P(8.2, '摸到的却只有虚空', 'rose', 'lh', 0.7),
    P(9, '像一幕旧场景忽然回来', 'gold', 'top', 2.0),
    P(12.5, '过去也不会因此重新变成现在', 'gold', 'top', 2.0),
    P(18, '波兰舞曲的步态逐渐浮现', 'blue', 'top', 2.0),
    P(21, '隐约记起了该如何迈步', 'blue', 'lh', 1.5),
    P(24, '一首从远处传来的旧歌', 'gold', 'top', 2.0),
    P(27, '腿脚虚浮的人，在记忆中挪动舞步', 'rose', 'top', 2.0),
    P(30, '细碎、不安的半音在蠕动', 'rose', 'lh', 2.0),
    P(38, '音乐猛地往上推，却又退下来', 'blue', 'top', 3.0),
]
LINE_T = {
    'S01-1': (2.3, [('总算不用再一再委屈自己了', 'blue')]),
    'S01-2': (5.1, [('心里就空落落的', 'rose')]),
    'S01-3': (9.5, [('从前熟悉的日子', 'gold'), ('靠什么让自己安下心', 'rose')]),
    'S02-1': (24.4, [('舍不得从前那些自在的时候', 'gold')]),
    'S02-2': (32, [('当初受过的难堪', 'blue')]),
    'S02-3': (41, [('好日子', 'gold'), ('不甘心', 'blue')]),
}
exec(open('scripts/_wrap.py', encoding='utf-8').read())
items = {i['id']: i for s in graph['segments'] for i in s['items']}
lines = []
for sid, (bar, frags) in LINE_T.items():
    txt = items[sid]['text']
    for f, _ in frags:
        if f not in txt:
            raise SystemExit(f'不是线的原文：{sid} {f}')
    rows = wrap(txt)
    seg_rows = []
    for r in rows:
        fr = []
        for f, h in frags:
            if f in r:
                fr.append((f, h))
            else:
                for k in range(len(f) - 1, 1, -1):
                    if r.endswith(f[:k]):
                        fr.append((f[:k], h)); break
                    if r.startswith(f[-k:]):
                        fr.append((f[-k:], h)); break
        seg_rows.append(segment_row(r, fr))
    lines.append(dict(id=sid, t=round(tb(bar), 2), d=round(max(4.2, len(txt) / 4.8), 2), rows=seg_rows, text=txt, hue=frags[0][1]))
lines.sort(key=lambda x: x['t'])
for a, b in zip(lines, lines[1:]):
    if a['t'] + a['d'] + 0.7 > b['t']:
        b['t'] = round(a['t'] + a['d'] + 0.7, 2)
KIND = {'top': lambda n: n['h'] == 1 and n['sky'], 'rh': lambda n: n['h'] == 1, 'inner': lambda n: n['h'] == 1 and not n['sky'],
        'lh': lambda n: n['h'] == 0, 'all': lambda n: True}
Y_LOW, Y_HIGH, P_LOW, P_HIGH = 778.0, 122.0, 24, 103
yof = lambda q: Y_LOW + (q - P_LOW) * (Y_HIGH - Y_LOW) / (P_HIGH - P_LOW)
phrases = sorted(PH, key=lambda x: x['t'])
placed = []
for p in phrases:
    a, b, kind = p['sel']
    sel = [n for n in music['notes'] if a <= n['s'] < b and KIND[kind](n)]
    if not sel:
        raise SystemExit('这句摘句没有对应的音：' + p['text'])
    p['t'] = round(max(p['t'], sel[0]['s']) + 0.05, 2)
    hi = max(n['p'] for n in sel)
    y = max(118.0, min(816.0, yof(hi) - 52))
    for _ in range(14):
        hit = False
        for q in placed:
            if q['t'] + q['d'] + 0.9 < p['t']:
                continue
            qx1 = 1540 - (p['t'] - q['t']) * 66 - 30
            qx0 = qx1 - len(q['text']) * 34
            if qx0 - 24 < 1510 and 1510 - len(p['text']) * 34 - 24 < qx1 and abs(q['y'] - y) < 54:
                hit = True
                y -= 56
                if y < 112:
                    y = 700.0
                break
        if not hit:
            break
    p['y'] = round(y, 1); p['d'] = round(p['d'], 2); placed.append(p)
def M(bar, top, bot, rh, lh, fade=3.0):
    return dict(t=round(tb(bar), 2), top=top, bot=bot, rh=rh, lh=lh, fade=fade)
mood = [
    M(1, [8, 11, 18], [10, 15, 24], [214, 226, 240], [120, 145, 180]),      # 冰冷、空
    M(9, [18, 13, 12], [34, 22, 16], [255, 226, 176], [160, 130, 110], 5),  # 旧场景回来，有了暖意
    M(15, [12, 12, 18], [18, 16, 24], [226, 218, 214], [120, 120, 150], 5), # 又退回去
    M(24, [20, 9, 14], [38, 14, 22], [255, 214, 186], [190, 96, 100], 3),   # 舞步，暗红
    M(38, [26, 10, 12], [52, 16, 18], [255, 214, 170], [220, 96, 80], 3),
]
necklace = [dict(t=p['t'], hue=p['hue']) for p in phrases]
tline = {l['id']: l['t'] for l in lines}
arcs = []
for l in lines:
    for c in items[l['id']].get('cite') or []:
        if c in tline and c[:3] != l['id'][:3]:
            arcs.append({'from': tline[c], 'to': l['t'], 'hue': l['hue']})
spec = dict(lines=lines, phrases=phrases, mood=mood, ghosts=[], necklace=necklace, arcs=arcs, center='', credit='', end_t=99999, wave=False, gain=2.6,
            title='肖邦《幻想波兰舞曲》', subtitle='一个人在这首曲子里经历的一件事', intro_len=5.0)
json.dump(spec, open('work/op61_spec.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('摘句', len(phrases), '线', len(lines))
