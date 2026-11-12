"""11-09 晚 K22：DAG 层改线（迭代准则：原料和 DAG2 一起迭代；DAG 的改动只按端到端证据收下）。
两步，两首同跑、同一份提示词：
  1. 改线：给 Center、现在的线（r2c，带段号、关系、编号）、每段小节和秒数；不给珠子（硬约束 3）。
  2. 对应：给新线和珠子全文，写明每条线对应哪几颗珠子（DAG 标准第 4 条）。
产物是一份只差线的新原料：line_r79o/{NEW}/{作品}_src.json（珠子、分段、Center、要点和时间窗照抄 r2c）。之后用 PUB_SRC={NEW} 走同一条 DAG2。
python r3/reline_k22.py NEW 线提示词文件 对应提示词文件 g6|g56
"""
import json, os, sys, copy, re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(HERE))
os.environ.setdefault('PUB_SRC', 'r2c')
import prompt_lint, pub16
from pub24 import S, R2, rd, call, parse, G6, G56, WORKS
import blend
sys.stdout.reconfigure(encoding='utf-8')
NL = chr(10)


def line_in(src):
    out = []
    for s in src['sections']:
        out.append(f"{s['sec']}（和 Center 的关系：{s.get('relation', '')}）")
        for l in s['lines']: out.append(f"  {l['id']}：{l['text']}" + (f"（提到前面：{'、'.join(l['refs'])}）" if l.get('refs') else ''))
    return NL.join(out)


def segs(w, src):
    win = pub16.windows(w)
    return NL.join(f"{s['sec']}：小节 {s['bars']}，约 {round(win[s['sec']][1]-win[s['sec']][0])} 秒" for s in src['sections'])


def beads_only(src):
    out = []
    for s in src['sections']:
        out.append(f"\n### {s['sec']}（小节 {s['bars']}）")
        for b in s['beads']: out.append(f"[{b['id']}] {b['text']}")
    return NL.join(out)


def ask(rid, msg, m, check):
    for k in range(3):
        try:
            r = parse(call(rid + ('' if not k else f'_r{k}'), msg, m, 'gpt3s', 'k22-reline')); check(r); return r
        except Exception as ex: print('不合格', rid, repr(ex)[:200], flush=True)


def one(a):
    w, new, lp, mp, who = a; m = G56 if who == 'g56' else G6
    out = HERE/new/f'{w}_src.json'
    if out.exists(): print('已有', out); return True
    src = rd(R2/f'{w}_src.json'); secs = [s['sec'] for s in src['sections']]
    ltpl = (S/lp).read_text(encoding='utf-8'); mtpl = (S/mp).read_text(encoding='utf-8')
    for t, nm in ((ltpl, lp), (mtpl, mp)): prompt_lint.lint(re.sub(r'\{(CENTER|LINE|SEGS|BEADS)\}', '', t), nm)
    assert '{BEADS}' not in ltpl, '改线的提示词不能带珠子（硬约束 3）'
    msg = ltpl.replace('{CENTER}', src['center']).replace('{LINE}', line_in(src)).replace('{SEGS}', segs(w, src))

    def chk(r): assert [x['sec'] for x in r['sections']] == secs, '段号不对'; assert all(x.get('lines') for x in r['sections']), '有段没有线'
    r = ask(f'k22L_{w}_{new}', msg, m, chk)
    if not r: return False
    # 编号统一成 段号-序号，避免模型自编编号
    for s in r['sections']:
        for i, l in enumerate(s['lines'], 1): l['id'] = f"{s['sec']}-{i}"
    nsrc = {'sections': [{'sec': s['sec'], 'relation': s.get('relation', ''), 'lines': s['lines']} for s in r['sections']]}
    ids = {b['id'] for s in src['sections'] for b in s['beads']}
    msg2 = mtpl.replace('{LINE}', line_in(nsrc)).replace('{BEADS}', beads_only(src))
    lids = {l['id'] for s in nsrc['sections'] for l in s['lines']}

    def chk2(q): assert q.get('map'), '没有 map'; assert {x['line'] for x in q['map']} <= lids, '对应里有不存在的线'
    q = ask(f'k22M_{w}_{new}', msg2, m, chk2)
    if not q: return False
    mp_ = {x['line']: [b for b in x.get('beads') or [] if b in ids and b.split('-')[0] == x['line'].split('-')[0]] for x in q['map']}   # 11-09 晚：只对应同一段的珠子（K22c 把后段珠子挂到前段，两位顾问都指出）
    res = copy.deepcopy(src)
    for s, ns in zip(res['sections'], nsrc['sections']):
        s['relation'] = ns['relation'] or s.get('relation', '')
        s['lines'] = [{'id': l['id'], 'text': l['text'], 'beads': mp_.get(l['id'], []), 'refs': [x for x in l.get('refs') or [] if x in lids]} for l in ns['lines']]
    used = {b for v in mp_.values() for b in v}
    out.parent.mkdir(exist_ok=True); out.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding='utf-8')
    L = [l['text'] for s in res['sections'] for l in s['lines']]
    print(w, new, '新线', len(L), '条', sum(map(len, L)), '字（r2c', sum(len(l['text']) for s in src['sections'] for l in s['lines']), '字）；没对应上的珠子', sorted(ids - used), flush=True)
    return True


if __name__ == '__main__':
    new, lp, mp, who = sys.argv[1:5]
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, new, lp, mp, who) for w in WORKS])), flush=True)
