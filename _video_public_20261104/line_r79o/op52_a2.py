"""Op.52 A 稿补位：Gemini 代理连不上（ECONNREFUSED），Luna 部分失败。缺多少就用 gpt3 多抽几份，凑够 24 份后收进 A 目录。
python op52_a2.py fill N      再抽 N 份 GPT
python op52_a2.py collect     收集成 SRC-*.md（够 24 份才写）
"""
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
B = Path('D:/musicclaude/_bead_op61_20261020/gen_A'); sys.path.insert(0, str(B)); sys.stdout.reconfigure(encoding='utf-8')
import gen
gen.WORK = 'op52'
import work_meta
d = work_meta.load('op52'); dest = work_meta.source_dir(d); out = gen.output_dir(); other = out.parent/'other_models'/'outputs'


def good():
    ok = {}
    for f in list(out.glob('*.md'))+list(other.glob('*.md')):
        t = f.read_text(encoding='utf-8')
        if len(t) >= 2500: ok[f.stem] = t
    return ok


c = sys.argv[1]
if c == 'fill':
    n = int(sys.argv[2]); pv = {'int': 'A_int_v1', 'web': 'A_web_v2'}; models = [('gpt6w', 'gpt-6-thinking'), ('gpt56w', 'gpt-5-6-thinking')]; jobs = []; i = 4
    while len(jobs) < n:
        for fam, m in models:
            for br in ('int', 'web'):
                if len(jobs) < n: jobs.append((f'{fam}-{br}-{i}', pv[br], m))
        i += 1
    with ThreadPoolExecutor(3) as ex: list(ex.map(lambda j: gen.run(j[0], j[1], j[2]), jobs))
    print('现有合格', len(good()), flush=True)
else:
    ok = good(); print('合格', len(ok), sorted(ok)); print({k: len(v) for k, v in ok.items() if len(v) < 5000})
    if len(ok) >= 24:
        names = sorted(ok); keep = [k for k in names if not k.startswith('gpt')]+[k for k in names if k.startswith('gpt')]; keep = keep[:24]
        dest.mkdir(parents=True, exist_ok=True)
        for k in keep: (dest/f'SRC-{k}.md').write_text(ok[k], encoding='utf-8')
        print('已收集', len(keep), dest)
