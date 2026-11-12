"""11-11 画面：核对定位（用户：“判断不准确 比如什么‘高处长颤音’根本不适合‘涌到嘴边’一起的”“当然这个正确率我们只会还要再看”）。
对 locate_final 里定到的每条要点，给出珠子原文、这条要点、被定到的小节和那几小节左右手的具体音，两位评委各自判断：这条要点说的就是这几小节、这只手吗。
都说“对得上”才保留；结果 r3/s24/locate_ok_{作品}.json（film_v9 读它）。
python r3/locate_check.py
"""
import json, os, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(Path(__file__).resolve().parent)); sys.path.insert(0, str(HERE))
os.environ.setdefault('PUB_SRC', 'r2e'); os.environ.setdefault('FILM_DATA', 'line_r79o')
import prompt_lint
from pub24 import S, R2, rd, wr, call, parse, G6, G56, WORKS
import locate
sys.stdout.reconfigure(encoding='utf-8')
NL = chr(10)

CHK = """下面是一首钢琴曲的听众感受，每条被定到了乐曲的某几小节和某只手，后面附上那几小节左右手的具体音（音名+八度@在小节里的位置，0 是小节开头、1 是结尾）。
视频里，音乐走到那几小节时，这条感受会亮起来，它说的那只手的音也会染成同一颜色。所以定错了，观众会看到一句话配着不相干的声音。

请逐条判断：
- ok：这条感受说的确实是这几小节（不是这一段里别的地方）吗？原文里没有指向具体声音或时刻、只是整段的心情，也算对不上。对得上写 true。
- hand_ok：它说的确实是这只手的声音吗？原文没说到具体声音的写 false。
- better：对不上的话，你认为应该是哪几小节（在给出的段落范围内），没有就写空。
- why：一句话理由，引原文几个字。
宁可判对不上。

只输出 JSON：{"items":[{"id":"S06-B1-p1","ok":true,"hand_ok":true,"better":[],"why":"…"}]}，每条都要有。

{BODY}
"""
prompt_lint.lint(CHK, 'locate_check.CHK')


def body(w):
    src = rd(R2/f'{w}_src.json'); loc = rd(S/f'locate_final_{w}.json'); f, lh, rh = locate.music(w)
    pt = {p['id']: (s, b, p) for s in src['sections'] for b in s['beads'] for p in b['points']}
    pl = json.load(open(HERE.parent/'plans'/f'{w}_points.json', encoding='utf-8'))
    out = [f"曲目：{pl.get('title', '')}（演奏：{pl.get('performer', '')}）"]
    for i, L in sorted(loc.items()):
        s, b, p = pt[i]; a, z = L['bars']
        out.append(f"### {i}（所在段 {s['sec']}，第 {s['bars']} 小节）" + NL + f"珠子原文：{b['text']}" + NL + f"这条：{p['text']}" + NL
                   + f"定到：第 {a}–{z} 小节，{L['hand'] or '没定声部'}" + NL + NL.join(locate.bar_notes(f, lh, rh, x) for x in range(a, z+1) if x in f.bar_t))
    return NL.join(out), set(loc)


def one(a):
    w, j = a; p = S/f'locchk_{w}_{j}.json'
    if p.exists(): return
    txt, ids = body(w)
    for k in range(3):
        try:
            r = parse(call(f'locchk_{w}_{j}' + ('' if not k else f'_r{k}'), CHK.replace('{BODY}', txt), {'g6': G6, 'g56': G56}[j], 'gpt3s', 'film-locchk'))
            got = [x for x in r['items'] if x.get('id') in ids]; assert len(got) >= .9*len(ids), len(got); wr(p, {'items': got}); return
        except Exception as ex: print('不合格', w, j, repr(ex)[:150], flush=True)


def merge(w):
    loc = rd(S/f'locate_final_{w}.json'); h = {j: {x['id']: x for x in rd(S/f'locchk_{w}_{j}.json')['items']} for j in ('g6', 'g56')}
    ok = {}
    for i, L in loc.items():
        x, y = h['g6'].get(i, {}), h['g56'].get(i, {})
        if x.get('ok') and y.get('ok'): ok[i] = dict(L, hand=L['hand'] if (x.get('hand_ok') and y.get('hand_ok')) else '', why=[x.get('why'), y.get('why')])
    wr(S/f'locate_ok_{w}.json', ok)
    print(w, '定位', len(loc), '两位都说对得上', len(ok), '其中声部也对', sum(bool(v['hand']) for v in ok.values()), '｜一位说对不上', sum(1 for i in loc if bool(h['g6'].get(i, {}).get('ok')) != bool(h['g56'].get(i, {}).get('ok'))), flush=True)
    for i in sorted(set(loc) - set(ok))[:12]: print('   去掉', i, h['g6'].get(i, {}).get('why'), '｜', h['g56'].get(i, {}).get('why'))


if __name__ == '__main__':
    with ThreadPoolExecutor(4) as ex: list(ex.map(one, [(w, j) for w in WORKS for j in ('g6', 'g56')]))
    for w in WORKS: merge(w)
