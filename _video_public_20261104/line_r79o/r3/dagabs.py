"""11-09 下午 DAG（定稿的线 + 珠子）按 11-08 版 DAG 标准做绝对尺度验收。
起因：用户问“dag 和 dag2 都按照现在的标准收敛了吗”。11-08 起 DAG 一直直接用 r79o 当原料，没按 11-08 版标准测过。
做法照 r3/openabs.py（大众版的绝对尺度验收）：四条内容标准 + 底线逐条给结论，问题按固定的绝对尺度标轻重；只是“还能写得更好”的不列。
轻重按对 DAG2 的影响定义（DAG 只作 DAG2 的原料）：DAG2 照着写会不会写歪、写不出因果、找不到情境。
python r3/dagabs.py [源 src 目录名，默认 r2] [轮次标记 run1 run2 ...]   结果 r3/s24/dagA_{作品}_{评委}_{源}_{轮次}.json
"""
import re, sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import prompt_lint
from pub24 import S, rd, wr, call, parse, G6, G56, WORKS
sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[1]

DAGA = """你是验收评审。下面是一首钢琴曲的“定稿”：一条线（一个人经历的一件事，分段要点，每段标了他此刻和全曲核心的关系）和每段的珠子（听的人此刻心里和身上的感受）。它不直接给观众看，而是作为原料，交给下一步改写成大众版“边听边看”视频的屏幕稿；压缩、人话、不啰嗦、排主次都由下一步做，这里不要求。

请按下面的标准做验收：逐条标准判断过没过，再列出确实存在的问题。

【轻重的绝对尺度——只按问题对下一步（照着它写屏幕稿）的实际影响判断，不按它是不是这一份里最突出的问题】
- 严重：照着它写，屏幕稿很可能会讲错或讲不通这个人的关键经历、原因、转折，或者偏离全曲核心；或者某段核心的感受在线里完全找不到对应的处境，下一步只能自己编。
- 中等：能用，但下一步要自己补因果、自己判断哪句对应哪颗珠子、自己理顺前后，或者某处意思含糊、可能被读歪。
- 轻微：不影响下一步照着写；只是措辞、局部可以更准。
- 不构成问题：只是能想到别的写法、个人偏好；以及人话、啰嗦、压缩、排主次（这些由下一步负责）——这类不要列出来。
规则：
1. 同一把尺子用在任何版本上。一份定稿即使只剩一个问题，它也可能只是轻微。
2. 出现次数多不自动升级：只有在确实造成累积影响时才算中等，并说明影响在哪里。
3. 情感留白、需要体会一下的细腻表达，不算问题；戏剧化、主观、只讲一个故事、没有外部动作，不算缺点。
4. 没有达到“轻微”门槛的地方不用找；某条标准没有问题就写“过”。

【标准】
{STD}

只输出 JSON：{"standards":[{"std":"1","verdict":"过|有问题","note":"一句"}],"issues":[{"sec":"S05 或 跨段","std":"1|2|3|4|底线","quote":"原文（跨段的写两三处）","why":"对下一步的实际影响是什么","severity":"严重|中等|轻微"}]}

【全曲核心（Center）】
{CENTER}

【定稿：每段的线和珠子】
{SRC}
"""
prompt_lint.lint(DAGA, 'dagabs.py')


def std():
    s = (Path('D:/musicclaude/_thread_evo_20261019/标准.md')).read_text(encoding='utf-8')
    s = s[s.index('## 内容维度'):s.index('修订记录')].rstrip('-\n ')
    return re.sub(r'（(用户|10-|11-)[^）]*）', '', s)


def src_text(w, src):
    d = rd(ROOT/src/f'{w}_src.json'); out = []
    for s in d['sections']:
        out.append(f"\n### {s['sec']}（他此刻和核心的关系：{s.get('relation', '')}）")
        out += [f"线 {l['id']}：{l['text']}" + (f"（提到前面：{'、'.join(l['refs'])}）" if l.get('refs') else '') + (f"（对应珠子：{'、'.join(l['beads'])}）" if l.get('beads') else '') for l in s['lines']]   # 11-09：r2b 起写明对应和出处
        out += [f"珠子 {b['id']}：{b['text']}" for b in s['beads']]
    return chr(10).join(out), d.get('center', '')


def one(a):
    w, j, m, src, run = a; p = S/f'dagA_{w}_{j}_{src}_{run}.json'
    if p.exists(): return rd(p)
    t, c = src_text(w, src)
    c = c if isinstance(c, str) else '；'.join(f'{k}：{v}' for k, v in c.items()) if isinstance(c, dict) else str(c)
    msg = DAGA.replace('{STD}', std()).replace('{CENTER}', c).replace('{SRC}', t)
    for k in range(3):
        ans = call(f'dagA_{w}_{j}_{src}_{run}' + ('' if not k else f'_r{k}'), msg, m, 'gpt3s', 'dag-abs')
        try: r = parse(ans); assert 'issues' in r; wr(p, r); return r
        except Exception as ex: print('不合格', w, j, src, run, repr(ex)[:120], flush=True)


def summary(src, runs):
    for w in WORKS:
        for j in ('g6', 'g56'):
            row = []
            for run in runs:
                p = S/f'dagA_{w}_{j}_{src}_{run}.json'
                if not p.exists(): row.append('缺'); continue
                r = rd(p); c = Counter(x.get('severity') for x in r.get('issues') or [])
                bad = [s.get('std') for s in r.get('standards') or [] if s.get('verdict') == '有问题']
                row.append(f"严重 {c['严重']}、中等 {c['中等']}、轻微 {c['轻微']}；有问题的标准 {','.join(bad) or '无'}")
            print(f"DAG 绝对验收 {src} {w} {j}： " + ' ｜ '.join(row), flush=True)


if __name__ == '__main__':
    args = sys.argv[1:]; src = next((x for x in args if not x.startswith('run')), 'r2'); runs = [x for x in args if x.startswith('run')] or ['run1']
    jobs = [(w, j, m, src, run) for run in runs for w in WORKS for j, m in (('g6', G6), ('g56', G56))]
    with ThreadPoolExecutor(min(8, len(jobs))) as ex: list(ex.map(one, jobs))
    summary(src, runs)
