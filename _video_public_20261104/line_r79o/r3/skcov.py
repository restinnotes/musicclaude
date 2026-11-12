"""11-12 夜 骨架层的覆盖（用户：“如果你现在不测覆盖……那可能某一大堆到最后永远没办法解释？”）。
每份骨架：两位评委逐颗珠子判，这一段骨架写的处境里，找不找得到和这颗珠子情境相近的处境（DAG 标准第 4 条：相关就行，不逐颗解释）。
python r3/skcov.py 名字=来源 …（来源写法同 skcheck.py）→ r3/s24/skcov_{名字}.json；最后跨所有已测骨架统计：哪些珠子在任何一份骨架里都没被接上。"""
import json, os, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); sys.path.insert(0, str(Path(__file__).resolve().parent)); os.environ['PUB_SRC'] = 'r2e'
from pub24 import R2, S, rd, call, parse, G6, G56, WORKS
import skcheck
sys.stdout.reconfigure(encoding='utf-8')
ASK = """下面是一份“骨架”：同一个人在一首钢琴曲里经历的一件心事，按音乐分段，每段写他此刻的处境和缘由（不是最终文案，不评措辞）。每段后面附了这一段的听感记录（珠子）：听的人在这一段的感受、画面、比喻。

请逐颗珠子判断：这一段骨架写的处境，能不能让人感到这颗珠子里的那种滋味——也就是，处在骨架写的这种处境里的人，会有和这颗珠子性质相近的感受吗？
- 接得上：骨架这一段的处境本身就带出这种滋味（不要求提到珠子的画面，相关就行）。
- 偏弱：大方向沾边，但这颗珠子最主要的那种滋味，处境里没有来由。
- 接不上：处境和这颗珠子的滋味没有关系，或者方向相反。
只看本段的骨架内容加上“全篇不变的处境”；不要因为骨架把珠子的感受词照抄了一遍就判接得上——要有处境。

只输出 JSON：{"beads":[{"id":"S01-B1","fit":"接得上|偏弱|接不上","why":"不超过二十字"}]}

【全篇不变的处境】
{GIVENS}

【这件事】{SIT}

{SEGS}
"""
JS = (('g6', G6), ('g56', G56))


def one(a):
    name, src, w, jn, J = a; sk = skcheck.load(src, w); secs = rd(R2/f'{w}_src.json')['sections']; bs = {s['sec']: s['beads'] for s in secs}
    segs = '\n\n'.join(f"### {s['sec']}\n骨架：{s['text']}\n珠子：\n" + '\n'.join(f"- {b['id']}：{b['text']}" for b in bs.get(s['sec'], [])) for s in sk['segs'])
    msg = ASK.replace('{GIVENS}', '\n'.join('- ' + g for g in sk['givens']) or '（没有单列）').replace('{SIT}', str(sk['situation'])).replace('{SEGS}', segs)
    for t in range(3):
        try:
            r = parse(call(f'skcov_{name}_{w}_{jn}' + ('' if not t else f'_r{t}'), msg, J, 'gpt3s', 'skcov')); assert len(r['beads']) > 10
            return {'w': w, 'judge': jn, 'beads': {b['id']: b['fit'].strip()[:3] for b in r['beads']}}
        except Exception as ex: print('重试', name, w, jn, repr(ex)[:100], flush=True)


def run(name, src):
    p = S/f'skcov_{name}.json'
    if not p.exists():
        with ThreadPoolExecutor(4) as ex: res = [x for x in ex.map(one, [(name, src, w, jn, J) for w in WORKS for jn, J in JS]) if x]
        p.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding='utf-8')
    return rd(p)


def score(res, w):
    """每颗珠子取两位评委里较低的一档。返回 {珠子: 2|1|0}"""
    V = {'接得上': 2, '偏弱': 1, '接不上': 0}; out = {}
    for r in res:
        if r['w'] != w: continue
        for b, f in r['beads'].items(): out[b] = min(out.get(b, 2), V.get(f, 1))
    return out


if __name__ == '__main__':
    jobs = [a.split('=', 1) for a in sys.argv[1:]]
    with ThreadPoolExecutor(len(jobs) or 1) as ex: list(ex.map(lambda j: run(*j), jobs))
    allr = {p.stem[6:]: rd(p) for p in sorted(S.glob('skcov_*.json'))}
    print('\n===== 骨架层覆盖（每颗珠子取两位评委里较低的一档）')
    for w in WORKS:
        main = {b['id'] for s in rd(R2/f'{w}_src.json')['sections'] for b in s['beads'] if b.get('role') == '主体验'}; best = {}
        for name, res in allr.items():
            sc = score(res, w)
            if not sc: continue
            for b, v in sc.items(): best[b] = max(best.get(b, 0), v)
            m = [v for b, v in sc.items() if b in main]
            print(f"{name} {w}｜接得上 {sum(v == 2 for v in sc.values())}/{len(sc)}、接不上 {sum(v == 0 for v in sc.values())}｜主体验 接得上 {sum(v == 2 for v in m)}/{len(m)}、接不上 {sum(v == 0 for v in m)}")
        print(f"  {w} 在所有已测骨架里都没被接上的珠子（{len(allr)} 份）：", [b for b, v in sorted(best.items()) if v < 2] or '无')
