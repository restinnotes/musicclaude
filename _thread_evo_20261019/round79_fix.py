"""11-06 B 路：用推进和 Center 关联两个新测法挑出的问题，局部修线（不重写）。复用 round65_fix 的 REPAIR 提示词和套用逻辑，只换问题来源。
python round79_fix.py TAG SOURCE [--max 8] [--guard r68a:r67a,...] [--route gpt3s]
问题来源：evaluations/r79/ 里 SOURCE 的 prog（来回摆）、map（偏离 Center 的段和主题）、pp（和 r78a 比的来回摆）；再加机械统计的高频抽象词。
"""
import argparse, json, os, re, sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import round65_fix as R
import v6fix as V
OUT = Path(__file__).resolve().parent/'evaluations'/'r79'

EXTRA = """
【这一轮专门修两件事，其他别动】
1. 来回摆：标准要求线“像一步步往前探索，不像在迷宫里来回”。读者指出的来回摆处，让后来的那段带出前面没有的新东西（新的处境、更深一层的认识、一个落到自己身上的后果），或者把重复的那条删掉、并到前面；不要只换个说法再说一遍。
2. 偏离 Center：这条线本该讲的是 Center 那件事本身——{CENTER}。读者指出的偏离段落，把这段写回 Center 里的东西在此刻的样子；不要新编情节，不要把珠子的比喻写成真事。
另外，同一个抽象词（比如下面统计里出现很多次的词）不要在相邻段反复充当万能词，换成这段具体的所求和顾虑。
"""


TIGHT = """
【这一轮只修两类，其余逐字不动】
1. 上一轮正反比较里，评委说“别版这段更简洁 / 更像人话”的地方：照着收紧措辞，意思一样不少。
2. 读者指出的、本版自己的来回摆：让后来那段带出前面没有的新东西；不要只换个说法再说一遍。
硬性要求：不许删除任何条目（不要输出 None），不许把两条并成一条；改后的条目不比原来长。不要改动没被点到的段。
这条线本该讲的是：{CENTER}。改的时候不要把它拉离这件事。
"""


CTIGHT = """
【这一轮只修一件事：让这条线更是 Center 那件事本身】
这条线本该讲的是：{CENTER}。
读者指出了下面这些偏离 Center 的地方。把被点到的条目改写成 Center 里那几样东西在此刻缠在一起的样子：比如此刻的幸福里已经带着留不住的痛，或者此刻的痛里还连着幸福。用这个人此刻具体在意的事来写，不要写成抽象的道理。
硬性要求：不许删除任何条目（不要输出 None），不许并条；改后不比原来长；不新编情节、不把珠子的比喻写成真事；没被点到的段逐字不动。改完通读，前后要接得上，不要让同一个意思在相邻段重说。
"""


def issues(w, src):
    rows = []
    for p in sorted(OUT.glob(f'prog_{w}_*_{src}.json')):
        r = json.loads(p.read_text(encoding='utf-8')); j = p.stem.split('_')[2]
        for x in r.get('loops') or []: rows.append({'读者': j, 'where': '来回摆', 'why': x})
        for s in r.get('sections') or []:
            if s.get('step') in ('回到前面', '原地重复'): rows.append({'读者': j, 'where': s['sec'], 'why': f"{s['step']}{'（回到 '+s['back_to']+'）' if s.get('back_to') else ''}：这段没有新东西"})
    for p in sorted(OUT.glob(f'pc?_{w}_*_{src}_vs*.json')):
        r = json.loads(p.read_text(encoding='utf-8')); key = 'x_off' if r.get('self') == 'X' else 'y_off'
        for x in r.get(key) or []: rows.append({'读者': p.stem.split('_')[2], 'where': '偏离 Center', 'why': x})
    for p in sorted(OUT.glob(f'map_{w}_*_{src}.json')):
        r = json.loads(p.read_text(encoding='utf-8')); j = p.stem.split('_')[2]
        for o in r.get('offcenter') or []: rows.append({'读者': j, 'where': '、'.join(o.get('secs') or []), 'why': f"偏离 Center 的主题：{o.get('theme')}"})
        for s in r.get('sections') or []:
            if s.get('part') == '无关' or s.get('drift'): rows.append({'读者': j, 'where': s['sec'], 'why': f"这段在讲 Center 以外的事：{s.get('drift')}"})
    for p in sorted(OUT.glob(f'pp?_{w}_*_{src}_vs*.json')):
        r = json.loads(p.read_text(encoding='utf-8')); key = 'x_loops' if r.get('self') == 'X' else 'y_loops'   # 本版自己的来回摆
        for x in r.get(key) or []: rows.append({'读者': p.stem.split('_')[2], 'where': '来回摆', 'why': x})
    g = V.graph_of(w, src); text = ' '.join(i['text'] for s in g['segments'] for i in s['items'])
    words = Counter(re.findall('[一-鿿]{2}', text)); top = [(k, n) for k, n in words.most_common(40) if k in ('亲近', '喜欢', '需要', '在乎', '回去', '从前', '委屈', '自在', '舍不得', '陪着', '保证', '不安', '心里')][:6]
    rows.append({'读者': '统计', 'where': '全篇', 'why': '高频词：' + '、'.join(f'{k}×{n}' for k, n in top)})
    return rows


def main():
    p = argparse.ArgumentParser(); p.add_argument('tag'); p.add_argument('source'); p.add_argument('--max', type=int, default=8)
    p.add_argument('--guard', default='r68a:r67a,r70a:r69b,r70b:r69b,r66a:r54weave'); p.add_argument('--route', default='gpt3s'); p.add_argument('--model', default='g6'); p.add_argument('--vs', default='', help='带回盲比里评委说丢掉的东西，如 r78a'); p.add_argument('--tight', action='store_true', help='只收紧措辞和修本版来回摆，不许删条目'); p.add_argument('--center', action='store_true', help='只修偏离 Center，不许删条目')
    a = p.parse_args(); os.environ['THREAD_ROUTE'] = a.route; R.F.configure()
    def one(w):
        iss = issues(w, a.source)
        if a.tight: iss = [x for x in iss if x['where'] == '来回摆']
        if a.center: iss = [x for x in iss if x['where'] == '偏离 Center' or '偏离 Center' in str(x.get('why'))]
        print(w, '问题', len(iss), flush=True)
        extra = (CTIGHT if a.center else TIGHT if a.tight else EXTRA).replace('{CENTER}', V.graph_of(w, a.source).get('center') or '')
        if a.vs:
            NL = chr(10)
            extra += NL + '【上一轮和 ' + a.vs + ' 正反比较时，评委说这一版丢掉或变差的东西：能补回就补回，别再删；评委说更啰嗦的地方要收】' + NL + NL.join(json.dumps(x, ensure_ascii=False) for x in R.feedback(w, a.source, a.vs)) + NL
        if a.guard:
            extra += ('\n【守护清单：前几轮评委明确说“删了就算退步”的内容。这些意思必须留在线里，可以换更短的说法，但不许删掉】\n' + '\n'.join(f'- {x}' for x in R.guard_list(w, a.guard)) + '\n')
        msg = R.REPAIR.format(MAX=a.max, LINE=V.view(V.graph_of(w, a.source), ids=True), BEADS=V.beads(w), ISSUES=json.dumps(iss, ensure_ascii=False, indent=0), EXTRA=extra)
        ans = R.pipe.call(f'sc{a.tag}_{w}_F2', msg, a.model, a.tag)
        R.apply_answer(w, a.tag, a.source, ans, a.max)
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, R.F.WORKS))
    R.show(a.tag, a.source)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8'); main()
