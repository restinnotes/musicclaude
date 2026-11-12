"""11-06 晚：精细体验评委校准。
旧测法（pub21 AUDIT）每次评审现挑 2–3 处精细体验再判，两次评审挑中同一句的几乎没有（船歌 42 处里重合 0–1 处），
所以分数主要量的是“这次挑了哪些句子、评委松紧”，不是屏幕变了没有。用户：“是不是你评委提示词问题 你在做的过程中如果觉得评委有问题的话需要校准”。
新测法：每首先固定一份精细体验清单（GPT-6、GPT-5.6 各挑一次，合并去重后冻结在 r3/fine_list_{作品}.json），之后每一版屏幕都对同一份清单逐条判 在 / 变粗 / 没了。
python pub25.py list                 建清单（已有就不动）
python pub25.py judge TAG [TAG...]   逐条判，结果 r3/fine2_{作品}_{评委}_{TAG}.json
python pub25.py score TAG [TAG...]   打印每版“在”的比例和逐评委数
"""
import json, re, sys
from concurrent.futures import ThreadPoolExecutor
from pub2 import G6, G56, JUDGES, WORKS, call, parse, rd, wr
import pub21

R3 = pub21.R3

EXTRACT = """下面是一首钢琴曲每一段的原稿：线（一个人经历的事）和珠子（听的人写下的当下感受）。

请逐段挑出这段最精细、换个说法就没了的体验，每段 3–4 处。不要挑概括性的意思，要挑那种读到才会觉得“对，就是这个感觉”的地方：一个具体的比喻画面、一种身体感觉、一个连接转折里的心理分寸、一句心里的话。

每处给：
- sec：段号
- quote：原稿原文，照抄，尽量短（一个短语到一句）
- what：一句话说这份精细是什么（例如“旋律不只是少了，而是孤零零、没有方向”）

只输出 JSON：{"fine":[{"sec":"S01","quote":"…","what":"…"}]}

【原稿】
{SOURCE}
"""

JUDGE = """一首钢琴曲的“边听边看”视频。观众在听音乐，眼睛扫屏幕。屏幕每段有几条线（一个人经历的事）和散开的短词（听的人当下的感受）。

下面是一份固定的“精细体验清单”：原稿里最精细、换个说法就没了的体验，每条附了这份精细是什么。请逐条看屏幕上这份精细还在不在：
- 在：屏幕上有字面或几乎同样细的说法，读到能得到同样的感觉（可以换词，可以拆成几个短词，只要那份分寸还在）
- 变粗：大意还在，但那份精细没了（比如“孤零零、漫无目的”只剩“声音变少”）
- 没了：屏幕上找不到

只看清单里的条目，逐条判，不要漏，也不要自己加条目。

只输出 JSON：{"items":[{"id":"F001","screen":"在|变粗|没了","where":"屏幕上对应的字，照抄；没有写空"}]}

【精细体验清单】
{LIST}

【屏幕】
{SCREEN}
"""


def _norm(t):
    return re.sub(r'[\s，。、；：！？“”‘’（）—…,.!?;:]', '', t or '')


def _overlap(a, b):
    a, b = _norm(a), _norm(b)
    if not a or not b: return 0
    if a in b or b in a: return 1
    common = sum(1 for i in range(len(a) - 1) if a[i:i+2] in b)
    return common / max(1, min(len(a), len(b)) - 1)


def build_list(w):
    p = R3/f'fine_list_{w}.json'
    if p.exists(): return rd(p)
    msg = EXTRACT.replace('{SOURCE}', pub21.source(w)); got = {}
    def one(name_model):
        name, model = name_model
        for k in range(3):
            ans = call(f'pub25X_{w}_{name}' + ('' if not k else f'_r{k}'), msg, model, 'gpt3s', 'public25-extract')
            try: r = parse(ans); assert r['fine']; return name, r['fine']
            except Exception as ex: print('不合格', w, name, repr(ex)[:150], flush=True)
        return name, []
    with ThreadPoolExecutor(2) as ex: got = dict(ex.map(one, [('g6', G6), ('g56', G56)]))
    items = []
    for name in ('g6', 'g56'):
        for f in got.get(name) or []:
            if not f.get('quote'): continue
            if any(x['sec'] == f.get('sec') and _overlap(x['quote'], f['quote']) >= 0.6 for x in items): continue
            items.append({'sec': f.get('sec'), 'quote': f['quote'], 'what': f.get('what', ''), 'from': name})
    items.sort(key=lambda x: (x['sec'] or '', ))
    for i, x in enumerate(items): x['id'] = f'F{i+1:03d}'
    r = {'items': items, 'note': '固定清单：GPT-6、GPT-5.6 各挑一次，同段重合六成以上的去重'}
    wr(p, r); print(w, '精细清单', len(items), '条（GPT-6', len(got.get('g6') or []), '，GPT-5.6', len(got.get('g56') or []), '）', flush=True)
    return r


def judge(a):
    w, j, tag = a; p = R3/f'fine2_{w}_{j}_{tag}.json'
    if p.exists(): return rd(p)
    L = build_list(w)['items']
    lst = '\n'.join(f"{x['id']}｜{x['sec']}｜「{x['quote']}」——{x['what']}" for x in L)
    msg = JUDGE.replace('{LIST}', lst).replace('{SCREEN}', pub21.screen(w, tag))
    for k in range(3):
        ans = call(f'pub25J_{w}_{j}_{tag}' + ('' if not k else f'_r{k}'), msg, JUDGES[j], 'gpt3s', 'public25-judge')
        try:
            r = parse(ans); ids = {x['id'] for x in L}; it = [x for x in r['items'] if x.get('id') in ids]
            assert len(it) >= 0.9 * len(L), f'只判了 {len(it)}/{len(L)}'
            wr(p, {'items': it}); return r
        except Exception as ex: print('不合格', w, j, tag, repr(ex)[:150], flush=True)


def score(w, tag, judges=None):
    out = {}
    for j in judges or JUDGES:
        p = R3/f'fine2_{w}_{j}_{tag}.json'
        if p.exists():
            it = rd(p)['items']; out[j] = round(sum(x.get('screen') == '在' for x in it) / max(1, len(it)), 3)
    return (round(sum(out.values()) / len(out), 3) if out else None), out


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8'); c = sys.argv[1]
    if c == 'list':
        for w in WORKS: build_list(w)
    elif c == 'judge':
        for w in WORKS: build_list(w)
        with ThreadPoolExecutor(12) as ex: list(ex.map(judge, [(w, j, t) for t in sys.argv[2:] for w in WORKS for j in JUDGES]))
        for t in sys.argv[2:]:
            for w in WORKS: print(t, w, score(w, t), flush=True)
    elif c == 'score':
        for t in sys.argv[2:]:
            for w in WORKS: print(t, w, score(w, t), flush=True)
