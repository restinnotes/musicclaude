"""Argon 能不能替代 Gemini 3.8 Flash 写原稿（A 稿）：同一提示词（A_int_v1，不联网）。不进任何主线，产物放 argon_A/。
python pub22.py gen            三首各 3 份 Argon
python pub22.py judge          Op.60、61 上和已有 gflash 稿盲比（4 票）
python pub22.py stats          字面统计
"""
import json, sys, re, os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
ROOT = Path(__file__).resolve().parent; EVO = Path('D:/musicclaude/_thread_evo_20261019'); sys.path.insert(0, str(EVO)); sys.path.insert(0, 'D:/musicclaude/_bead_op61_20261020/gen_A')
os.environ.setdefault('JV', '2'); sys.stdout.reconfigure(encoding='utf-8')
import evo, gen, work_meta
OUT = ROOT/'argon_A'; OUT.mkdir(exist_ok=True)
WORKS = ('op60', 'op61', 'op52')
SRC = {'op60': Path('D:/musicclaude/_bead_saturation_20261018/inputs/A'), 'op61': Path('D:/musicclaude/_bead_op61_20261020/inputs/A'), 'op52': EVO/'works/op52/A'}

BLIND = """下面是两份为同一首钢琴曲写的听感文字，由不同作者写。这些文字之后要被提炼成给普通听众的“珠子”：听的人当下心里和身上是什么感觉。

请比较：哪份给出了更精细、更具体、更能让普通人对上自己感受的体验？空泛的抒情、堆砌的比喻和纯音乐术语不算好。

只输出 JSON：{"better":"X|Y","x_only":["只有 X 有、确实有价值的体验，3 条以内"],"y_only":["只有 Y 有、确实有价值的体验，3 条以内"],"why":"两三句话"}

【X】
{X}

【Y】
{Y}
"""


def one(a):
    w, i = a; rid = f'pub22_{w}_argon_{i}'; msg = gen.render('A_int_v1', w)
    ans = evo.call_argon_direct(rid, msg, meta={'stage': 'pub22-argon-A'})
    (OUT/f'{w}_argon_{i}.md').write_text(ans or '', encoding='utf-8'); print(w, i, len(ans or ''), flush=True)


def judge(a):
    w, i, j, seat = a; arg = (OUT/f'{w}_argon_{i}.md').read_text(encoding='utf-8'); fl = (SRC[w]/f'SRC-gflash-int-{i}.md').read_text(encoding='utf-8')
    x, y = (arg, fl) if seat == 'X' else (fl, arg); rid = f'pub22J_{w}_{i}_{j}_{seat}'
    import pub2
    ans = pub2.call(rid, BLIND.replace('{X}', x).replace('{Y}', y), pub2.JUDGES[j], 'gpt3s', 'public22-judge'); r = pub2.parse(ans) or {}
    (OUT/f'judge_{w}_{i}_{j}.json').write_text(json.dumps({'argon_seat': seat, **r}, ensure_ascii=False, indent=1), encoding='utf-8')
    print(w, i, j, 'Argon 在', seat, '选', r.get('better'), 'Argon胜' if r.get('better') == seat else 'Flash胜', (r.get('why') or '')[:200], flush=True)


def stats():
    def bg(t):
        t = ''.join(c for c in t if '\u4e00' <= c <= '\u9fff'); return {t[k:k+2] for k in range(len(t)-1)}
    for w in WORKS:
        cor = {}
        for f in SRC[w].glob('*.md'):
            fam = f.name.split('-')[1]; cor.setdefault('gpt' if fam.startswith('gpt') else fam, []).append(f.read_text(encoding='utf-8', errors='ignore'))
        gpt = set().union(*[bg(t) for t in cor['gpt']]); rows = []
        for fam, ts in list(cor.items())+[('argon', [p.read_text(encoding='utf-8') for p in OUT.glob(f'{w}_argon_*.md')])]:
            if fam == 'gpt' or not ts: continue
            rows.append((fam, '均长', sum(map(len, ts))//len(ts), 'GPT 没有的词占比', round(sum(len(bg(t)-gpt)/max(1, len(bg(t))) for t in ts)/len(ts), 3)))
        print(w, 'GPT稿', len(cor['gpt']), '均长', sum(map(len, cor['gpt']))//len(cor['gpt']), rows, flush=True)


if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'gen':
        with ThreadPoolExecutor(3) as ex: list(ex.map(one, [(w, i) for w in WORKS for i in (1, 2, 3)]))
        stats()
    elif c == 'judge':
        sys.path.insert(0, str(ROOT))
        with ThreadPoolExecutor(4) as ex: list(ex.map(judge, [('op60', 1, 'g6', 'X'), ('op61', 1, 'g6', 'Y'), ('op60', 2, 'g56', 'Y'), ('op61', 2, 'g56', 'X')]))
    else: stats()
