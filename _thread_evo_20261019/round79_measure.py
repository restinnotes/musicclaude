"""11-06 线的两个新测法，先校准评委再用：
- prog：推进还是来回摆（标准第 1 条“像一步步往前探索，不像在迷宫里来回”）。逐段标：新的一步 / 往深处走 / 回到前面的状态 / 原地重复。
- center：和 Center 的关联。第一步盲读：不给 Center，只读线，说这条线讲的核心是什么、反复出现哪几条主题；
  第二步对照：给两句候选（本作品的 Center 和旧 Center，位置轮换），判哪句更贴，再逐段标这段体现 Center 的哪一部分，列出跑到 Center 以外的主题。
python round79_measure.py calib          在 r78a、r49b、h23、人为回摆版（r78aloop）上校准
python round79_measure.py run TAG [...]  测给定版本
python round79_measure.py sum TAG [...]
两首 × 两位评委（GPT-6、GPT-5.6），gpt3、gpt4 分流。
"""
import json, os, sys, zlib, copy
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
os.environ.setdefault('JV', '2')
ROOT = Path(__file__).resolve().parent; sys.path.insert(0, str(ROOT))
import evo
OUT = ROOT/'evaluations'/'r79'; OUT.mkdir(parents=True, exist_ok=True)
WORKS = ('op60', 'op61'); JUDGES = {'g6': evo.G6, 'g56': evo.G56}
OLD = {'op60': '对亲密的投入与自我克制始终相互牵制。', 'op61': '向外行动与旧梦都要求投入，却彼此牵制。'}

PROG = """下面是一条“线”：一个人在一首曲子里经历的一件事，按音乐段落分段，每段几条。

我们要求它“像一步步往前探索，不像在迷宫里来回”：每一段都应该让这件事往前走一步或往深处走一步；可以有犹豫和反复，但反复之后要有新的东西，而不是回到前面某段已经到过的状态、再把同样的心思说一遍。

请逐段判断：
- step：新的一步（处境或认识有了新的东西）/ 往深处走（同一件事想得更深、更具体）/ 回到前面（回到前面某段已经有过的状态或想法，没有新的东西）/ 原地重复（和上一段说的几乎一样）
- back_to：如果是“回到前面”，写回到了哪一段（如 S04）；否则空
- new：这段新多出来的东西，十五字以内；没有就写“无”
最后：
- loops：列出来回摆的几处，每处写涉及的段和摆的是什么（如“S07–S13 在‘想要保证’和‘怕不被需要’之间来回”）
- verdict：整体像“往前探索”还是“迷宫里来回”，或“前半探索、后半来回”这类，一句话
- score：推进的分，1–10，10 是每段都在往前或往深处走

只输出 JSON：{"sections":[{"sec":"S01","step":"新的一步","back_to":"","new":"…"}],"loops":["…"],"verdict":"…","score":7}

【线】
{LINE}
"""

BLIND = """下面是一条“线”：一个人在一首曲子里经历的一件事，按音乐段落分段。请只根据线本身回答：
1. core：这条线讲的核心是什么？用一句话说，像给这件事起一个概括（不超过三十字）。
2. themes：线里反复出现的主题有哪几条？每条写主题（十字以内）和出现在哪些段。
只输出 JSON：{"core":"…","themes":[{"theme":"…","secs":["S01"]}]}

【线】
{LINE}
"""

PICK = """下面是一条“线”（一个人在一首曲子里经历的一件事），以及两句候选的“核心”。哪一句更贴这条线实际写出来的东西？
只输出 JSON：{"pick":"X|Y","fit":"很贴|部分贴|不太贴","why":"一两句"}

【X】{X}
【Y】{Y}

【线】
{LINE}
"""

PAIRP = """下面是同一首曲子的两条“线”（一个人在曲子里经历的一件事，按段写）。我们要求线“像一步步往前探索，不像在迷宫里来回”：每段都让这件事往前或往深处走；可以犹豫反复，但反复之后要有新的东西，而不是回到前面某段已经到过的状态、把同样的心思再说一遍。

哪一条更像在迷宫里来回？分别列出两条里来回摆的地方（涉及哪几段、摆的是什么）。
只输出 JSON：{"more_loop":"X|Y|一样","x_loops":["…"],"y_loops":["…"],"why":"一两句"}

【X】
{X}

【Y】
{Y}
"""

PAIRC = """下面是同一首曲子的两条“线”（一个人在曲子里经历的一件事，按段写），以及它们本该围绕的核心（Center）。

哪一条讲的更是 Center 那件事本身？看三点：Center 里的几样东西是不是都在；它们是不是缠在一起地变化，而不是各说各的；线有没有换成一件和 Center 相近的另一件事来当主线（比如只写了 Center 的一半，或者把某个具体顾虑当成了整件事）。字多字少、写得好不好都不算。

只输出 JSON：{"closer":"X|Y|一样","x_off":["X 偏离 Center 的地方"],"y_off":["Y 偏离 Center 的地方"],"why":"一两句"}

【Center】{C}

【X】
{X}

【Y】
{Y}
"""

MAP = """下面是一条“线”（一个人在一首曲子里经历的一件事）和它本该围绕的核心（Center）。
1. 逐段判断这段体现了 Center 的哪一部分：
   - part：前一半 / 后一半 / 两者不可分（这段同时体现了 Center 说的两样东西怎样缠在一起）/ 无关（这段在讲 Center 以外的事）
   - drift：如果无关或只沾边，这段实际在讲什么，十字以内；否则空
2. offcenter：线里占了较多段、但 Center 没有包含的主题，列出来并写出现在哪些段。
3. score：和 Center 的关联，1–10。
只输出 JSON：{"sections":[{"sec":"S01","part":"两者不可分","drift":""}],"offcenter":[{"theme":"…","secs":["S05"]}],"score":7}

【Center】{C}

【线】
{LINE}
"""


def graph(w, tag):
    if tag == 'r78aloop': return loop(w)
    g = json.loads((ROOT/'evaluations'/'v6fix'/f'{w}_{tag}.json').read_text(encoding='utf-8-sig')); return g.get('graph', g)


def loop(w):
    """校准用：在 r78a 的后半段，每段末尾补上四段之前那段的第一条（意思原样回去），人为制造回摆。"""
    g = copy.deepcopy(graph(w, 'r78a')); segs = g['segments']; n = len(segs)
    for i in range(n//2, n-1):
        src = segs[i-4]['items'][0]['text']; segs[i]['items'].append({'id': f"{segs[i]['sec']}-x", 'text': src})
    return g


def view(g): return '\n\n'.join(f"{s['sec']}\n"+'\n'.join(f"- {i['text']}" for i in s['items']) for s in g['segments'])


def center(w): return graph(w, 'r78a').get('center')


def call(rid, msg, model):
    evo.TL.route = 'gpt4s' if zlib.crc32(rid.encode()) % 2 else 'gpt3s'
    for k in range(3):
        r = evo.call(rid+('' if not k else f'_r{k}'), msg, model=model, meta={'stage': 'r79', 'web': True})
        try:
            return json.JSONDecoder().raw_decode(r[r.find('{'):])[0]
        except Exception: print('不合格', rid, flush=True)
    return None


def one(a):
    kind, w, j, tag = a; p = OUT/f'{kind}_{w}_{j}_{tag}.json'
    if p.exists(): return
    g = graph(w, tag); line = view(g)
    if kind[:2] in ('pp', 'pc'): p = OUT/f"{kind}_{w}_{j}_{tag}_vs{os.environ.get('R79_BASE', 'r78a')}.json"
    if p.exists(): return
    if kind == 'prog': r = call(f'r79P_{w}_{j}_{tag}', PROG.replace('{LINE}', line), JUDGES[j])
    elif kind == 'blind': r = call(f'r79B_{w}_{j}_{tag}', BLIND.replace('{LINE}', line), JUDGES[j])
    elif kind == 'pick':
        true_x = zlib.crc32(f'{w}{j}{tag}'.encode()) % 2 == 0   # 真 Center 在 X 还是 Y 轮换
        x, y = (center(w), OLD[w]) if true_x else (OLD[w], center(w))
        r = call(f'r79K_{w}_{j}_{tag}', PICK.replace('{X}', x).replace('{Y}', y).replace('{LINE}', line), JUDGES[j])
        if r: r['true'] = 'X' if true_x else 'Y'
    elif kind.startswith('pk'):   # pkX / pkY：真 Center 放在 X 或 Y
        tx = kind[-1] == 'X'; x, y = (center(w), OLD[w]) if tx else (OLD[w], center(w))
        r = call(f'r79{kind}_{w}_{j}_{tag}', PICK.replace('{X}', x).replace('{Y}', y).replace('{LINE}', line), JUDGES[j])
        if r: r['true'] = 'X' if tx else 'Y'
    elif kind.startswith('pp'):   # ppX / ppY：本版在 X 或 Y，和 BASE 比谁更来回
        base = os.environ.get('R79_BASE', 'r78a'); bl = view(graph(w, base)); tx = kind[-1] == 'X'
        r = call(f'r79{kind}_{w}_{j}_{tag}_vs{base}', PAIRP.replace('{X}', line if tx else bl).replace('{Y}', bl if tx else line), JUDGES[j])
        if r: r['self'] = 'X' if tx else 'Y'; r['base'] = base
    elif kind.startswith('pc'):   # pcX / pcY：本版在 X 或 Y，和 BASE 比谁更贴 Center
        base = os.environ.get('R79_BASE', 'r78a'); bl = view(graph(w, base)); tx = kind[-1] == 'X'
        r = call(f'r79{kind}_{w}_{j}_{tag}_vs{base}', PAIRC.replace('{C}', center(w)).replace('{X}', line if tx else bl).replace('{Y}', bl if tx else line), JUDGES[j])
        if r: r['self'] = 'X' if tx else 'Y'; r['base'] = base
    else: r = call(f'r79M_{w}_{j}_{tag}', MAP.replace('{C}', center(w)).replace('{LINE}', line), JUDGES[j])
    if r: p.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')


def run2(tags):
    """对比式：Center 两选一（正反位置）和与 BASE 比谁更来回（正反位置）。"""
    jobs = [(k, w, j, t) for t in tags for w in WORKS for j in JUDGES for k in (() if t == os.environ.get('R79_BASE', 'r78a') else ('ppX', 'ppY', 'pcX', 'pcY'))]
    with ThreadPoolExecutor(10) as ex: list(ex.map(one, jobs))
    summary2(tags)


def summary2(tags):
    base = os.environ.get('R79_BASE', 'r78a')
    for t in tags:
        for w in WORKS:
            pk = [json.loads(p.read_text(encoding='utf-8')) for p in OUT.glob(f'pk?_{w}_*_{t}.json')]
            pp = [json.loads(p.read_text(encoding='utf-8')) for p in OUT.glob(f'pp?_{w}_*_{t}_vs{base}.json')]
            more = sum(r.get('more_loop') == r.get('self') for r in pp); less = sum(r.get('more_loop') not in (r.get('self'), '一样') for r in pp)
            pc = [json.loads(p.read_text(encoding='utf-8')) for p in OUT.glob(f'pc?_{w}_*_{t}_vs{base}.json')]
            cl = sum(r.get('closer') == r.get('self') for r in pc); cb = sum(r.get('closer') not in (r.get('self'), '一样') for r in pc)
            print(f"{t} {w}：和 {base} 比更贴 Center 本版 {cl}、{base} {cb}、一样 {len(pc)-cl-cb}", flush=True)
            print(f"{t} {w}：认对 Center {sum(r.get('pick') == r.get('true') for r in pk)}/{len(pk)}；和 {base} 比，判本版更来回 {more}、判 {base} 更来回 {less}、一样 {len(pp)-more-less}", flush=True)


def run(tags):
    jobs = [(k, w, j, t) for t in tags for w in WORKS for j in JUDGES for k in ('prog', 'blind', 'pick', 'map')]
    with ThreadPoolExecutor(10) as ex: list(ex.map(one, jobs))
    summary(tags)


def summary(tags):
    for t in tags:
        for w in WORKS:
            row = []
            for j in JUDGES:
                p = OUT/f'prog_{w}_{j}_{t}.json'
                if p.exists():
                    r = json.loads(p.read_text(encoding='utf-8')); c = Counter(s.get('step') for s in r['sections'])
                    row.append(f"{j} 推进分 {r.get('score')} 回到前面 {c['回到前面']} 原地 {c['原地重复']}")
                p = OUT/f'pick_{w}_{j}_{t}.json'
                if p.exists():
                    r = json.loads(p.read_text(encoding='utf-8')); row.append(f"{j} 两选一{'选中真Center' if r.get('pick') == r.get('true') else '选了旧Center'}（{r.get('fit')}）")
                p = OUT/f'map_{w}_{j}_{t}.json'
                if p.exists():
                    r = json.loads(p.read_text(encoding='utf-8')); c = Counter(s.get('part') for s in r['sections'])
                    row.append(f"{j} Center关联分 {r.get('score')} 段：前半 {c['前一半']} 后半 {c['后一半']} 不可分 {c['两者不可分']} 无关 {c['无关']} 偏出主题 {[o.get('theme') for o in r.get('offcenter') or []]}")
                p = OUT/f'blind_{w}_{j}_{t}.json'
                if p.exists(): row.append(f"{j} 盲读核心：{json.loads(p.read_text(encoding='utf-8')).get('core')}")
            print(f"== {t} {w}\n   " + '\n   '.join(row), flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    c = sys.argv[1]
    if c == 'calib': run(['r78a', 'r49b', 'h23', 'r78aloop'])
    elif c == 'calib2': run2(['r78a', 'r49b', 'h23', 'r78aloop'])
    elif c == 'run2': run2(sys.argv[2:])
    elif c == 'sum2': summary2(sys.argv[2:])
    elif c == 'run': run(sys.argv[2:])
    else: summary(sys.argv[2:])
