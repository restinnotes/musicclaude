# 《船歌》样片的编辑表：线逐字用 r54weave；珠子摘句逐字来自对应珠子（程序核对，不是逐字就报错）。
# 这张表是我手工挑的，用来验证画面想法；正式生产时这一步应由模型做，并单独过评审。
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
EVO = r'D:\musicclaude\_thread_evo_20261019'
parsed = json.load(open('r54weave_parsed.json', encoding='utf-8'))['op60']
music = json.load(open('work/op60_music_v3.json', encoding='utf-8'))
BARS = {int(k): float(v) for k, v in music['bars']}
DUR = float(music['dur'])
graph = json.load(open(EVO + r'\evaluations\v6fix\op60_r54weave.json', encoding='utf-8'))['graph']


def tb(b):
    k = int(b)
    t0 = BARS.get(k, DUR)
    t1 = BARS.get(k + 1, DUR)
    return t0 + (b - k) * (t1 - t0)


ALL_BEADS = [x['text'] for s in parsed for x in s['beads']]


def P(bar, text, hue, kind='top', span=1.0, d=None, y=None, dx=-30):
    """bar: 出现的小节（可带小数）；text: 必须是某颗珠子里的连续原文；kind: 点亮哪些音；span: 点亮几小节"""
    if not any(text in b for b in ALL_BEADS):
        raise SystemExit('不是珠子原文：' + text)
    t = tb(bar)
    if d is None:
        d = max(3.2, len(text) / 3.6)
    return dict(t=t, d=d, text=text, hue=hue, sel=[tb(bar), tb(bar + span), kind], bar=bar, y=y, dx=dx)


# ---- 珠子摘句（时间按音乐，不按合写稿的次序） ----
PH = [
    P(1, '有一点突然', 'gold', 'lh', 0.3, d=3.2),
    P(2, '细碎的光点再缓缓飘落', 'gold', 'rh', 1.0, y=300),
    P(4, '左手已经像心跳', 'blue', 'lh', 2.0, y=540),
    P(6, '两条旋律线贴得很近', 'gold', 'rh', 2.0, y=250),
    P(8.5, '像一根温柔的刺', 'rose', 'top', 1.5, y=200),
    P(10.6, '水却一直在流，时间也一直在走', 'rose', 'lh', 1.5, y=560),
    P(12, '忽然往上涌了一次', 'gold', 'top', 2.0, y=210),
    P(14.2, '像轻轻呼出一口气', 'blue', 'top', 1.5, y=200),
    P(17.2, '有一点陶醉，有一点走神', 'gold', 'rh', 2.0, y=240),
    P(20, '心里闪过一个急于表达的念头', 'gold', 'top', 1.5, y=170),
    P(21.6, '被水下暗流拖住', 'blue', 'lh', 1.5, y=560),
    P(24, '熟悉的歌声又回来了', 'gold', 'top', 2.0, y=250),
    P(27, '水面折射的光斑', 'gold', 'rh', 1.0, y=200),
    P(29, '不自觉地握得更紧', 'rose', 'top', 1.0, y=190),
    P(30.3, '仿佛每一秒都在倒数', 'rose', 'lh', 1.7, y=560),
    P(32.3, '像夕阳在水面切出的最后一道金光', 'gold', 'top', 0.7, d=5.4, y=170),
    P(33.0, '在喉咙口颤抖、哽咽', 'rose', 'top', 1.0, y=210),
    P(35.3, '仿佛自己松开了手', 'blue', 'top', 0.7, y=240),
    P(36.1, '只剩下一条单薄、孤零零的旋律', 'blue', 'top', 2.0, d=5.6, y=380),
    P(40, '空气一下凉了', 'blue', 'top', 1.0, y=300),
    P(42.2, '清凉、空灵的月光', 'blue', 'top', 2.0, y=280),
    P(44.5, '“算了”“但还是放不下”', 'rose', 'inner', 2.0, y=240),
    P(48, '恍惚间却像已经成了回忆', 'rose', 'top', 2.0, y=300),
    P(51, '内声部像水底的暗涌不断攀爬', 'rose', 'inner', 2.0, y=210),
    P(54.5, '低音的八度与切分像沉重的脉搏', 'gold', 'lh', 2.0, y=570),
    P(58, '你已经听见时间正在经过', 'rose', 'top', 2.0, y=170),
    P(62, '旋律忽然变得直接、舒展', 'gold', 'top', 2.0, y=220),
    P(65.5, '像重新接触到阳光和风', 'gold', 'top', 2.0, y=200),
    P(69, '向上散掉、蒸发了', 'blue', 'top', 2.0, y=150),
    P(71, '戛然而止', 'blue', 'top', 1.0, y=300),
    P(72, '像话说到要紧处一下顿住', 'blue', 'top', 1.0, y=300),
    P(74.5, '光还在，只是隔了一层朦胧的雾气', 'blue', 'top', 2.0, y=280, d=5.0),
    P(76, '两个人对视到呼吸都停了', 'rose', 'top', 2.0, y=250),
    P(78, '终于长长呼出一口气', 'gold', 'top', 1.0, y=200),
    P(80, '像晨曦里的银色蛛丝', 'gold', 'top', 1.2, y=150),
    P(81.2, '从极高处倾泻而下', 'gold', 'rh', 1.5, y=240),
    P(82.7, '连自己的身体也仿佛失去了重量', 'gold', 'top', 1.3, y=300),
    P(84, '同一艘船、同一首歌', 'gold', 'top', 2.0, y=240),
    P(85.3, '横跨几个八度的惊涛骇浪', 'gold', 'lh', 2.0, y=600),
    P(88, '这是我的感情，我不再为它道歉', 'gold', 'top', 2.0, y=170, d=5.0),
    P(90.5, '光芒刺眼到让人想流泪', 'rose', 'top', 1.5, y=170),
    P(93, '放到了最大尺度', 'gold', 'top', 2.0, y=165),
    P(96, '仿佛还想要更多，却始终不能完全满足', 'rose', 'top', 3.0, y=165, d=5.2),
    P(100.5, '这份狂喜像高烧', 'gold', 'all', 1.5, y=165),
    P(103, '终于把长久悬着的心愿说出口', 'gold', 'top', 2.0, y=250),
    P(105, '下方的脚步仿佛牢牢踩住地面', 'blue', 'lh', 2.0, y=600),
    P(107.2, '悲伤却进入了幸福内部', 'rose', 'top', 2.0, y=220, d=4.6),
    P(109, '「可是呢？」', 'rose', 'top', 1.0, y=250),
    P(111, '真正松下来、轻下来', 'blue', 'top', 1.5, y=260),
    P(113, '像男中音独自沉思', 'gold', 'inner', 1.5, y=540),
    P(115, '水花溅落夜空', 'gold', 'rh', 1.0, y=170),
    P(116, '低音像铁锚落入水底', 'rose', 'lh', 1.0, y=610, d=4.4),
]

# ---- 线：逐字；只标时间和同色片段 ----
# t 的单位是小节，线不必卡小节，这里只让它落在合适的情绪上；颜色片段必须是这句线的原文
LINE_T = {
    'S01-1': (1.15, [('那么想靠近这个人', 'gold')]),
    'S01-2': (2.6, [('只敢露出一点点', 'blue')]),
    'S01-3': (4.1, [('觉得甜', 'gold')]),
    'S02-1': (6.2, [('渐渐放松下来', 'gold')]),
    'S02-2': (9.6, [('最后还是怕太急弄坏眼下的自在而收住了', 'blue')]),
    'S02-3': (13.2, [('还没分开就先有一点舍不得', 'rose')]),
    'S03-1': (17.4, [('舒舒服服地待在这份亲近里', 'gold')]),
    'S03-2': (20.2, [('念头就慢慢淡了', 'blue')]),
    'S04-1': (24.6, [('满心欢喜', 'gold')]),
    'S04-2': (27.4, [('全说出来', 'gold'), ('怕对方觉得太多', 'blue')]),
    'S04-3': (29.9, [('留久一点', 'rose')]),
    'S05-1': (33.6, [('自然露了出来', 'gold')]),
    'S05-2': (36.0, [('心里空落落的', 'blue')]),
    'S05-3': (38.3, [('忽然隔了一层', 'blue')]),
    'S06-1': (40.8, [('照旧亲近他', 'gold')]),
    'S06-2': (44.0, [('忽然觉得有点孤单', 'blue')]),
    'S06-3': (47.6, [('舍不得结束这份亲近', 'rose')]),
    'S07-1': (51.5, [('不是自己一个人在需要', 'gold')]),
    'S07-2': (55.0, [('舍不得抽身', 'rose')]),
    'S07-3': (59.0, [('自己都能在身边', 'gold')]),
    'S08-1': (62.8, [('大大方方地回应', 'gold')]),
    'S08-2': (65.9, [('还能这么好很久', 'gold')]),
    'S08-3': (68.8, [('心里又有了一点没底', 'blue')]),
    'S09-1': (72.3, [('连和他待在一起也不愿意了呢', 'blue')]),
    'S09-2': (74.2, [('连下一个念头都不敢接着想', 'blue')]),
    'S09-3': (76.3, [('眼前这份亲近并没有', 'gold')]),
    'S10-1': (78.5, [('好好享受', 'gold')]),
    'S10-2': (81.2, [('几乎想笑，也有点想哭', 'gold')]),
    'S11-1': (84.1, [('真的愿意长久陪着对方', 'gold')]),
    'S11-2': (86.7, [('胸口发疼', 'rose')]),
    'S11-3': (89.2, [('心里疼得厉害', 'rose')]),
    'S12-1': (93.2, [('把能给的好都给对方', 'gold')]),
    'S12-2': (96.0, [('留不住每一个以后', 'rose')]),
    'S12-3': (99.2, [('痛痛快快地喜欢对方', 'gold')]),
    'S13-1': (103.3, [('谁也没法答应永远', 'rose')]),
    'S13-2': (105.5, [('把已经露出的喜欢往回收一点', 'blue')]),
    'S13-3': (108.2, [('想收回便更难受', 'rose')]),
    'S14-1': (111.0, [('心里软下来，又有些发酸', 'rose')]),
    'S14-2': (113.2, [('不想再催着要一个永远不变的保证', 'gold')]),
    'S14-3': (114.9, [('就不往回藏了', 'gold')]),
}


def wrap(text, n=28):
    """最多两行：一行放得下就一行；否则在最靠近中间的逗号处断，两行都不超过 30 字。"""
    if len(text) <= n:
        return [text]
    mid = len(text) / 2
    cuts = [i + 1 for i, ch in enumerate(text) if ch in '，、；：？' and i + 1 < len(text) - 1]
    good = [c for c in cuts if c <= 30 and len(text) - c <= 30]
    c = min(good, key=lambda c: abs(c - mid)) if good else int(round(mid))
    return [text[:c], text[c:]]


def segment_row(row, frags):
    # 把一行切成（文字，颜色）小段
    out = [(row, None)]
    for frag, hue in frags:
        nxt = []
        for s, h in out:
            if h is None and frag in s:
                i = s.index(frag)
                if s[:i]:
                    nxt.append((s[:i], None))
                nxt.append((frag, hue))
                if s[i + len(frag):]:
                    nxt.append((s[i + len(frag):], None))
            else:
                nxt.append((s, h))
        out = nxt
    return out


items = {i['id']: i for s in graph['segments'] for i in s['items']}
import os
PERSON = os.environ.get('PERSON') == '1'
if PERSON:
    for it in items.values():
        t = it['text'].replace('对方', '你').replace('他', '我')
        # 同一小句里“你”后面的“自己”指的是“我”，否则会读成“你自己”
        t = ''.join(re.sub('(你.*?)自己', lambda m: m.group(1) + '我', part) for part in re.split('([，。；：？])', t))
        it['text'] = t
    LINE_T = {k: (b, [(f.replace('对方', '你').replace('他', '我'), h) for f, h in fr]) for k, (b, fr) in LINE_T.items()}
CPS = 4.8
lines = []
for sid, (bar, frags) in LINE_T.items():
    txt = items[sid]['text']
    for f, _ in frags:
        if f not in txt:
            raise SystemExit(f'不是线的原文：{sid} {f}')
    t = tb(bar)
    d = max(4.2, len(txt) / CPS)
    rows = wrap(txt)
    # 跨行的同色片段：把片段按行切开
    seg_rows = []
    for r in rows:
        fr = []
        for f, h in frags:
            if f in r:
                fr.append((f, h))
            else:
                # 片段被断行切开时，分别找两边
                for k in range(len(f) - 1, 1, -1):
                    if r.endswith(f[:k]):
                        fr.append((f[:k], h))
                        break
                    if r.startswith(f[-k:]):
                        fr.append((f[-k:], h))
                        break
        seg_rows.append(segment_row(r, fr))
    lines.append(dict(id=sid, t=round(t, 2), d=round(d, 2), rows=seg_rows, text=txt, hue=(frags[0][1] if frags else 'gold')))
lines.sort(key=lambda x: x['t'])
# 不让两句线重叠：前一句读完才出下一句
for a, b in zip(lines, lines[1:]):
    if a['t'] + a['d'] + 0.7 > b['t']:
        b['t'] = round(a['t'] + a['d'] + 0.7, 2)

# 摘句的 y 没给时给默认；时间排序
phrases = sorted(PH, key=lambda x: x['t'])
KIND = {'top': lambda n: n['h'] == 1 and n['sky'], 'rh': lambda n: n['h'] == 1, 'inner': lambda n: n['h'] == 1 and not n['sky'],
        'lh': lambda n: n['h'] == 0, 'all': lambda n: True}
Y_LOW, Y_HIGH, P_LOW, P_HIGH = 778.0, 122.0, 24, 103
yof = lambda q: Y_LOW + (q - P_LOW) * (Y_HIGH - Y_LOW) / (P_HIGH - P_LOW)
V = 66.0
NOW_X = 1540.0
placed = []
for p in phrases:
    a, b, kind = p['sel']
    sel = [n for n in music['notes'] if a <= n['s'] < b and KIND[kind](n)]
    if not sel:
        raise SystemExit('这句摘句没有对应的音：' + p['text'])
    p['t'] = round(max(p['t'], sel[0]['s']) + 0.05, 2)
    hi = min(n['p'] for n in sel) if kind == 'lh' else max(n['p'] for n in sel)
    y = yof(hi) + 74 if kind == 'lh' else yof(hi) - 52
    y = max(118.0, min(816.0, y))
    w = len(p['text']) * 33
    for _ in range(14):
        hit = False
        for q in placed:
            if q['t'] + q['d'] + 0.9 < p['t']:
                continue
            qx1 = NOW_X - (p['t'] - q['t']) * V - 30
            qx0 = qx1 - len(q['text']) * 33
            if qx0 - 24 < NOW_X - 30 and NOW_X - 30 - w - 24 < qx1 and abs(q['y'] - y) < 54:
                hit = True
                y += 56 if kind == 'lh' else -56
                if y < 112:
                    y = 816.0
                if y > 820:
                    y = 130.0
                break
        if not hit:
            break
    p['y'] = round(y, 1)
    placed.append(p)
    p['d'] = round(p['d'], 2)
    p['sel'] = [round(p['sel'][0], 2), round(p['sel'][1], 2), p['sel'][2]]

# 先听到、再读到：同色摘句如果比线晚一点点，就把线挪到摘句之后（你 8 月的要求：why-now 放在感受后面）
for l in lines:
    later = [p for p in phrases if p['hue'] == l['hue'] and 0 < p['t'] - l['t'] <= 5.0]
    if later and l['id'] != 'S04-3':   # S04-3 不挪：第 32 小节的顶点要留白
        l['t'] = round(min(p['t'] for p in later) + 0.5, 2)
lines.sort(key=lambda x: x['t'])
for a, b in zip(lines, lines[1:]):
    if a['t'] + a['d'] + 0.7 > b['t']:
        b['t'] = round(a['t'] + a['d'] + 0.7, 2)
_b = _s = _a = _n = 0
for l in lines:
    near = [p for p in phrases if p['hue'] == l['hue'] and abs(p['t'] - l['t']) <= 8]
    if not near:
        _n += 1
        continue
    x = min(near, key=lambda p: abs(p['t'] - l['t']))['t'] - l['t']
    if x < -0.2:
        _b += 1
    elif x > 0.2:
        _a += 1
    else:
        _s += 1
print('同色摘句更早', _b, '几乎同时', _s, '更晚', _a, '8秒内没有', _n)
print('高潮第32小节顶点时的线', [l['id'] for l in lines if l['t'] <= tb(32.75) <= l['t'] + l['d'] + 0.7])

# 情绪色：每一处都来自珠子写过的冷暖、明暗
def M(bar, top, bot, rh, lh, fade=3.0):
    return dict(t=round(tb(bar), 2), top=top, bot=bot, rh=rh, lh=lh, fade=fade, bar=bar)


mood = [
    M(1, [8, 9, 20], [12, 13, 26], [255, 232, 190], [150, 170, 210]),
    M(4, [7, 15, 26], [10, 28, 38], [255, 222, 165], [86, 158, 178], 5),
    M(17, [15, 12, 28], [28, 19, 40], [236, 205, 198], [122, 112, 176], 5),
    M(24, [12, 13, 25], [32, 22, 30], [255, 216, 145], [104, 142, 168], 4),
    M(32, [24, 14, 14], [46, 26, 18], [255, 222, 135], [170, 132, 112], 4),
    M(35, [8, 9, 11], [11, 12, 15], [214, 220, 226], [106, 112, 124], 3),
    M(39, [5, 6, 9], [7, 8, 12], [190, 205, 225], [90, 110, 140], 1.5),
    M(40, [5, 12, 28], [9, 24, 46], [192, 226, 255], [72, 122, 178], 1.2),
    M(51, [12, 12, 32], [34, 17, 40], [226, 206, 236], [150, 92, 132], 6),
    M(62, [8, 23, 30], [16, 40, 42], [222, 255, 236], [112, 176, 166], 3),
    M(72, [18, 17, 24], [28, 24, 30], [210, 196, 206], [120, 106, 126], 2.5),
    M(78, [15, 22, 40], [28, 42, 64], [240, 248, 255], [142, 172, 206], 3),
    M(84, [22, 12, 9], [52, 25, 12], [255, 226, 152], [222, 122, 72], 1.6),
    M(93, [34, 13, 7], [70, 30, 10], [255, 236, 172], [255, 132, 62], 3),
    M(103, [22, 7, 12], [46, 10, 18], [255, 192, 172], [192, 62, 72], 3),
    M(111, [14, 9, 16], [22, 13, 20], [236, 196, 176], [142, 92, 102], 5),
    M(116.6, [3, 3, 5], [4, 4, 6], [200, 180, 170], [90, 70, 80], 3),
]

# 同一首歌的上一次：程序已验证相似度（24←6 为 0.81，84←6 为 0.93，51←40 为 0.87）
notes = music['notes']


def ghost(dst, src, n, transpose=0):
    pts = []
    for i in range(n):
        s0, s1 = BARS[src + i], BARS[src + i + 1]
        d0, d1 = BARS[dst + i], BARS[dst + i + 1]
        for x in notes:
            if x['h'] == 1 and x['sky'] and s0 <= x['s'] < s1:
                k = (x['s'] - s0) / (s1 - s0)
                pts.append([round(d0 + k * (d1 - d0), 3), x['p'] + transpose])
    return dict(t0=BARS[dst], t1=BARS[dst + n], pts=pts, dst=dst, src=src, n=n)


ghosts = [ghost(24, 6, 4), ghost(84, 6, 4), ghost(51, 40, 4)]

# 项链：每颗珠子一个点，颜色跟它的摘句走
necklace = [dict(t=p['t'], hue=p['hue']) for p in phrases]

# 弧：线的每句引用的前文（来自 r54weave 的 cite，程序直接读）
tline = {l['id']: l['t'] for l in lines}
arcs = []
for l in lines:
    for c in items[l['id']].get('cite') or []:
        if c in tline and c[:3] != l['id'][:3]:   # 只画跨段的引用
            arcs.append({'from': tline[c], 'to': l['t'], 'hue': l['hue']})

spec = dict(lines=lines, phrases=phrases, mood=mood, ghosts=ghosts, necklace=necklace, arcs=arcs,
            center=graph['center'], credit='肖邦《船歌》Op.60　钢琴：迪努·利帕蒂　线与珠子：r54weave',
            end_t=DUR + 0.5, tail=12.0, title='肖邦《船歌》', subtitle='一个人在这首曲子里经历的一件事', intro_len=5.0)
json.dump(spec, open(os.environ.get('SPEC_OUT', 'work/op60_spec.json'), 'w', encoding='utf-8'), ensure_ascii=False)

# 读量核算
L = sum(len(re.sub(r'\s', '', l['text'])) for l in lines)
Ph = sum(len(p['text']) for p in phrases)
print(f'线 {L} 字，摘句 {Ph} 字（{len(phrases)} 条），合计 {(L + Ph) / DUR:.2f} 字/秒')
bead_total = sum(len(b) for b in ALL_BEADS)
print(f'珠子原文 {bead_total} 字，摘句占 {Ph / bead_total * 100:.0f}%')
worst = 0
win = 15
for t0 in np.arange(0, DUR - win, 1.0) if False else [x * 1.0 for x in range(0, int(DUR - win))]:
    n = 0
    for l in lines:
        ov = max(0, min(l['t'] + l['d'], t0 + win) - max(l['t'], t0))
        n += len(l['text']) * ov / l['d']
    for p in phrases:
        ov = max(0, min(p['t'] + p['d'], t0 + win) - max(p['t'], t0))
        n += len(p['text']) * ov / p['d']
    worst = max(worst, n / win)
print(f'任意 15 秒窗口最大读量：{worst:.1f} 字/秒')
lag = []
for sid, (bar, _) in LINE_T.items():
    l = next(x for x in lines if x['id'] == sid)
    lag.append((round(l['t'] - tb(bar), 1), sid))
print('线因为不重叠被推迟（秒）：', sorted(lag, reverse=True)[:6])
# 线的结束是否超过音乐
print('线在屏幕上的时间占比 %.0f%%' % (sum(l['d'] for l in lines) / DUR * 100))
print('两行以上的句子', sum(1 for l in lines if len(l['rows']) > 2), '最长一行', max(len(''.join(x[0] for x in r)) for l in lines for r in l['rows']))
print('最后一句结束', lines[-1]['t'] + lines[-1]['d'], '音乐结束', DUR)
