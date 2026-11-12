"""11-06 试验：盲比提示词加入 Center 一项，看评委选择会不会变。不改正式验收（round37_fair.py 不动）。
python round79_fairc.py TAG BASE   → 正反 8 票，evaluations/r79/fairc_{TAG}_vs{BASE}.json
"""
import json, os, sys, zlib
from concurrent.futures import ThreadPoolExecutor
os.environ.setdefault('JV', '2')
import evo, screen_flow as F, v6fix as V

ADD = """5. center（贴 Center）：这条线本该讲的是这件事——{CENTER}。哪一版这一段讲的更是这件事本身（Center 里那几样东西是不是都在、是不是缠在一起），而不是一件和它相近的另一件事？
"""


def prompt(w, x, y):
    p = V.BLIND2.replace('5. lost：', ADD.replace('{CENTER}', V.graph_of(w, 'r78a').get('center'))+'6. lost：')
    p = p.replace('最后整体判断：', '最后整体判断（贴不贴 Center 和前四项同样重要）：')
    p = p.replace('"cover": "X", "cover_why": "……",', '"cover": "X", "cover_why": "……", "center": "X", "center_why": "……",')
    return p.format(NAME=V.covjudge.NAME[w], WHAT=V.WHAT2, X=V.view(x), Y=V.view(y), BEADS=V.beads(w))


def one(a):
    w, j, tag, base, s = a; rid = f'r79FC_{w}_{j}_{tag}_vs{base}_{s}'
    old, new = V.graph_of(w, base), V.graph_of(w, tag); x, y = (new, old) if s == 'newX' else (old, new)
    evo.TL.route = 'gpt4s' if zlib.crc32(rid.encode()) % 2 else 'gpt3s'
    for k in range(3):
        r = evo.call(rid+('' if not k else f'_r{k}'), prompt(w, x, y), model=V.JUDGES[j], meta={'stage': 'r79-fairc', 'web': True})
        try: d = json.JSONDecoder().raw_decode(r[r.find('{'):])[0]; break
        except Exception: d = None
    if not d: return None
    nw = 'X' if s == 'newX' else 'Y'; od = 'Y' if nw == 'X' else 'X'
    net = {k: sum((c.get(k) == nw)-(c.get(k) == od) for c in d['sections']) for k in ('alone', 'lean', 'plain', 'cover', 'center')}
    return {'w': w, 'j': j, 'seat': s, 'new_win': d.get('better') == nw, 'net': net}


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8'); F.configure()
    tag, base = sys.argv[1:3]
    with ThreadPoolExecutor(8) as ex: rows = [r for r in ex.map(one, [(w, j, tag, base, s) for w in F.WORKS for j in F.JUDGES for s in ('newX', 'newY')]) if r]
    tot = {k: sum(r['net'][k] for r in rows) for k in rows[0]['net']} if rows else {}
    print(tag, 'vs', base, '加 Center 的盲比：选新', sum(r['new_win'] for r in rows), '/', len(rows), tot, flush=True)
    for r in rows: print('  ', r['w'], r['j'], r['seat'], '新胜' if r['new_win'] else '旧胜', r['net'], flush=True)
    json.dump(rows, open(f'evaluations/r79/fairc_{tag}_vs{base}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
