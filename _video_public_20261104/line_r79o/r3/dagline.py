"""11-11 DAG 层改线（I12 交回，两位顾问的改线方案）。用一份改线提示词，在现有原料（PUB_SRC，默认 r2e）的线上改，产物 line_r79o/{NEW}/（珠子、分段照抄，线换新）。
线改了以后要走同一份 DAG2 提示词端到端比，好了才收（准则第一节）。
python r3/dagline.py NEW 提示词文件名（在 r3/s24/） 写手(g6|g56)
"""
import json, os, sys, copy
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(HERE))
os.environ.setdefault('PUB_SRC', 'r2e')
import prompt_lint, re
from pub24 import R2, S, rd, call, parse, G6, G56, WORKS
sys.stdout.reconfigure(encoding='utf-8')
NL = chr(10)


def line_text(src):
    return NL.join(NL + '### ' + s['sec'] + NL + NL.join(f"- {l['id']}：{l['text']}（对应珠子：{'、'.join(l.get('beads') or []) or '无'}）" for l in s['lines']) for s in src['sections'])


def bead_text(src):
    return NL.join(NL + '### ' + s['sec'] + NL + NL.join(f"- {b['id']}：{b['text']}" for b in s['beads']) for s in src['sections'])


def one(a):
    w, new, pf, j = a; src = rd(R2/f'{w}_src.json'); out = R2.parent/new
    tpl = (S/pf).read_text(encoding='utf-8')
    prompt_lint.lint(re.sub(r'\{(LINE|CENTER|BEADS)\}', '', tpl), pf)
    msg = tpl.replace('{LINE}', line_text(src)).replace('{CENTER}', src['center']).replace('{BEADS}', bead_text(src))
    model = {'g6': G6, 'g56': G56}[j]; secs = [s['sec'] for s in src['sections']]
    for k in range(3):
        try:
            r = parse(call(f'dagline_{new}_{w}' + ('' if not k else f'_r{k}'), msg, model, 'gpt3s', 'dag-line'))
            got = {s['sec']: s for s in r['sections']}; assert all(x in got and got[x].get('lines') for x in secs), '缺段'
            break
        except Exception as ex: print('不合格', w, repr(ex)[:150], flush=True); r = None
    if not r: return w, None
    bids = {b['id'] for s in src['sections'] for b in s['beads']}
    d = copy.deepcopy(src); old = {l['id']: l for s in src['sections'] for l in s['lines']}; ch = 0; n0 = n1 = 0
    for s in d['sections']:
        n0 += sum(len(l['text']) for l in s['lines'])
        nl = []
        for l in got[s['sec']]['lines']:
            o = old.get(l['id'], {})
            nl.append({'id': l['id'], 'text': l['text'].strip(), 'beads': [b for b in (l.get('beads') or o.get('beads') or []) if b in bids], 'refs': o.get('refs', [])})
            ch += o.get('text') != l['text'].strip()
        s['lines'] = nl; n1 += sum(len(l['text']) for l in nl)
    (out/f'{w}_src.json').write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8')
    (out/f'dagline_{w}.json').write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
    print(w, new, '改动或新增', ch, '条；线字数', n0, '→', n1, flush=True)
    return w, d


if __name__ == '__main__':
    new, pf, j = sys.argv[1], sys.argv[2], sys.argv[3]; (R2.parent/new).mkdir(exist_ok=True)
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, [(w, new, pf, j) for w in WORKS]))
