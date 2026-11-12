"""11-10 傍晚 DAG 层：生产珠子后加一步去重（用户 11-10：“这种两段一样的取前一段不就行了 这应该要改 dag 靠前的东西就行了吧 生产珠子的”；“泛泛的道理感觉确实可以删”；“抽象词感觉应该要堆叠吧”）。
起因（端到端证据）：一条跨两段的听感在分段时被整条放进了相邻两段（出处栏写明“覆盖前后两段”），写手照搬就成跨屏重复；珠子里泛泛的道理照搬被判不是此刻的体验。
做法：两位各自独立挑 ①后一段里几乎原样重说前面某一段要点、没有新增内容的要点（取前一段，后一段删）；②泛泛的道理。两位都挑中的才删。
并列的几样感受不动；后一段里新增的部分不动；别的一律不改字。删空的珠子去掉。产物 line_r79o/{NEW}/（线、对应、分段照抄来源）。
python r3/beaddedup.py NEW        （来源用 PUB_SRC，默认 r2c）
"""
import json, os, sys, copy
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(HERE))
os.environ.setdefault('PUB_SRC', 'r2c')
import prompt_lint
from pub24 import R2, rd, call, parse, G6, G56, WORKS
sys.stdout.reconfigure(encoding='utf-8')
NL = chr(10)

DEDUP = """下面是一首钢琴曲每一段的“珠子”要点：几位听众在这一段写下的感受，已按句拆开，每条有编号（编号开头是段号）。这些要点以后会被写到视频屏幕上，一段一屏。

请只挑两类要点，别的都不要动：

一、跨段重复：后面一段的某条要点，和前面某一段（通常是相邻的前一段）的某条要点说的是同一个具体体验，用词也几乎一样，没有多出新的画面、身体感觉、情绪层次或变化。这种情况保留前一段的，挑出后一段的那条。
- 只是主题相近（都在害怕、都在想念）不算；后一条比前一条多了新东西（更强了、变了、多了一层）不算，哪怕前半句相同；同一段里的几条不在这一类里。
- 一条要点前半重复、后半是新的：不挑。

二、泛泛的道理：这条要点说的不是这一刻听到、感到、想到的具体东西，而是一句放在哪里都成立的人生判断或道理。
- 把几样感受并列在一起说的要点不是道理，不要挑。带着具体画面、身体感觉、处境的不要挑。

宁可少挑。只输出 JSON：{"drop":[{"id":"S02-B1-p3","kind":"重复|道理","dup_of":"重复的话写前面那条的编号，否则空","why":"一句话"}]}。没有就输出 {"drop":[]}。

【珠子要点】
{BEADS}
"""
prompt_lint.lint(DEDUP, 'beaddedup.DEDUP')


def ask(a):
    w, j, model = a; src = rd(R2/f'{w}_src.json')
    txt = NL.join(NL + '### ' + s['sec'] + NL + NL.join(f"- {q['id']}：{q['text']}" for b in s['beads'] for q in b['points']) for s in src['sections'])
    for k in range(3):
        try: return w, j, parse(call(f'beaddedup_{w}_{j}' + ('' if not k else f'_r{k}'), DEDUP.replace('{BEADS}', txt), model, 'gpt3s', 'dag-beaddedup'))['drop']
        except Exception as ex: print('不合格', w, j, repr(ex)[:150], flush=True)
    return w, j, []


if __name__ == '__main__':
    new = sys.argv[1]; out = R2.parent/new; out.mkdir(exist_ok=True)
    with ThreadPoolExecutor(4) as ex: res = list(ex.map(ask, [(w, j, m) for w in WORKS for j, m in (('g6', G6), ('g56', G56))]))
    for w in WORKS:
        f = {j: {x['id']: x for x in fx if x.get('id')} for ww, j, fx in res if ww == w}
        src = copy.deepcopy(rd(R2/f'{w}_src.json')); tx = {q['id']: q['text'] for s in src['sections'] for b in s['beads'] for q in b['points']}
        both = {i for i in set(f['g6']) & set(f['g56']) if i in tx and f['g6'][i].get('kind') == f['g56'][i].get('kind')}
        print('==', w, 'GPT-6 挑', len(f['g6']), 'GPT-5.6 挑', len(f['g56']), '都挑中', len(both))
        for i in sorted(both):
            x = f['g6'][i]; print(f"   删 {i}（{x.get('kind')}）{tx[i]}");
            if x.get('dup_of') in tx: print(f"        前面那条 {x['dup_of']}：{tx[x['dup_of']]}")
        for j in ('g6', 'g56'):
            for i in sorted(set(f[j]) - both):
                if i in tx: print(f"   只有 {j} 挑（不删）{i}（{f[j][i].get('kind')}）{tx[i][:60]}")
        for s in src['sections']:
            for b in s['beads']:
                b['points'] = [q for q in b['points'] if q['id'] not in both]
                if any(i.startswith(b['id'] + '-') for i in both): b['text'] = ''.join(q['text'] for q in b['points'])
            s['beads'] = [b for b in s['beads'] if b['points']]
        (out/f'{w}_src.json').write_text(json.dumps(src, ensure_ascii=False, indent=1), encoding='utf-8')
        (out/f'beaddedup_{w}.json').write_text(json.dumps({'picks': f, 'dropped': sorted(both)}, ensure_ascii=False, indent=1), encoding='utf-8')
