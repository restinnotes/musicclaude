"""11-09 下午 DAG 补“对应”和“出处”（DAG 标准第 4 条“写明哪条线对应哪几颗珠子”、形态“提到前面的内容直接提并标出处”）。
r3/dagabs.py 对 r79o（r2）两首两位评委各两遍，8 次里中等问题几乎都是这一条：只把线和珠子并列，没写对应。
做法：GPT-6、GPT-5.6 各自独立标；两位一致的直接用，不一致的取两位都给的线并集（最多 2 条）。线和珠子的文字一个字不动。
另：船歌 S13-1“越喜欢跟他待着”指代不清（GPT-5.6 报中等），按全段以“他”为感受主体的读法改成“他越喜欢跟对方待着”。
python r3/dagmap.py 新目录名(r2b)       写到 line_r79o/{新目录}/{作品}_src.json，每条线加 beads（对应的珠子）和 refs（提到的前面段落）
"""
import copy, json, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import prompt_lint
from pub24 import rd, call, parse, G6, G56, WORKS
sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[1]

MAP = """下面是一首钢琴曲定稿的线（一个人经历的一件事，按段、按条编号）和每段的珠子（听的人此刻的感受）。请做两件标注，不改任何文字：
1. 对应：同一段里，每颗珠子的感受落在哪条线的处境上（情境相近、感受呼应就算，不要求因果）。每颗珠子给 1 条线，确实同时贴近两条才给 2 条。
2. 出处：每条线如果提到了前面段落里已经出现过的事或感受，标出它指的是前面哪一条线的编号；没有提到前面就不标。

只输出 JSON：{"beads":[{"id":"珠子编号","lines":["线编号"]}],"refs":[{"id":"线编号","to":["前面的线编号"]}]}

{SRC}
"""
prompt_lint.lint(MAP, 'dagmap.py')


def text(d):
    out = []
    for s in d['sections']:
        out.append(f"\n### {s['sec']}")
        out += [f"线 {l['id']}：{l['text']}" for l in s['lines']]
        out += [f"珠子 {b['id']}：{b['text']}" for b in s['beads']]
    return chr(10).join(out)


def ask(w, j, m, d):
    for k in range(3):
        try:
            r = parse(call(f'dagmap_{w}_{j}' + ('' if not k else f'_r{k}'), MAP.replace('{SRC}', text(d)), m, 'gpt3s', 'dag-map'))
            return {x['id']: [y for y in x.get('lines') or []] for x in r['beads']}, {x['id']: [y for y in x.get('to') or []] for x in r.get('refs') or []}
        except Exception as ex: print('不合格', w, j, repr(ex)[:120], flush=True)
    return {}, {}


def one(a):
    w, new = a; d = copy.deepcopy(rd(ROOT/'r2'/f'{w}_src.json'))
    if w == 'op60':
        for s in d['sections']:
            for l in s['lines']:
                if l['id'] == 'S13-1':
                    assert '越喜欢跟他待着' in l['text']; l['text'] = l['text'].replace('越喜欢跟他待着', '他越喜欢跟对方待着')
    with ThreadPoolExecutor(2) as ex: (b1, r1), (b2, r2) = ex.map(lambda jm: ask(w, jm[0], jm[1], d), [('g6', G6), ('g56', G56)])
    agree = diff = 0
    lid = {l['id']: s['sec'] for s in d['sections'] for l in s['lines']}
    order = [l['id'] for s in d['sections'] for l in s['lines']]
    for s in d['sections']:
        ok = {l['id'] for l in s['lines']}
        for l in s['lines']: l['beads'] = []
        for b in s['beads']:
            x, y = [i for i in b1.get(b['id'], []) if i in ok], [i for i in b2.get(b['id'], []) if i in ok]
            if set(x) == set(y) and x: use = x; agree += 1
            else: use = list(dict.fromkeys([i for i in x if i in y] or (x[:1] + y[:1]))); diff += 1
            use = use[:2] or [s['lines'][0]['id']]
            b['lines'] = use
            for l in s['lines']:
                if l['id'] in use: l['beads'].append(b['id'])
        for l in s['lines']:
            both = [i for i in r1.get(l['id'], []) if i in r2.get(l['id'], [])]
            l['refs'] = [i for i in both if i in lid and lid[i] != s['sec'] and order.index(i) < order.index(l['id'])]
    p = ROOT/new/f'{w}_src.json'; p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8')
    print(w, new, '珠子对应：两位一致', agree, '、不一致取交集或各取第一', diff, '；标了出处的线', sum(1 for s in d['sections'] for l in s['lines'] if l['refs']), flush=True)


if __name__ == '__main__':
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, [(w, sys.argv[1]) for w in WORKS]))
