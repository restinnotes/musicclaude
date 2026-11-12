"""11-11 画面：给珠子的每条要点定位到小节和声部（用户：“小字里很大部分也是值得去做这种动画效果的……在这种动画里可能也值得继续分大小字”）。
标准画面第 1 条：对着具体声音、具体几小节的细节到那几小节出现，它说的那几个音同色；没有依据的不编位置，不确定是哪个声音的不上色。
做法：每段给出每条要点、所在珠子原文、这一段逐小节的音乐概况（左右手各有几个音、音区、力度），两位评委各自判断：这条要点是不是对着某一刻；
是的话落在哪几小节、哪只手（右手/左手/两手/说不清），依据是原文哪几个字。两位都判“对着某一刻”且小节有重叠才定（取重叠部分）；声部两位一致才上色。
python r3/locate.py         → r3/s24/locate_{作品}_{评委}.json，合并 r3/s24/locate_{作品}.json
"""
import json, os, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
os.environ.setdefault('PUB_SRC', 'r2e'); os.environ.setdefault('FILM_DATA', 'line_r79o')
import numpy as np
import prompt_lint
from pub24 import S, R2, rd, wr, call, parse, G6, G56, WORKS
sys.stdout.reconfigure(encoding='utf-8')
NL = chr(10)

LOC = """下面是一首钢琴曲每一段的听众感受（“珠子”，已拆成一条条要点，每条有编号），以及这一段逐小节的音乐概况（右手、左手各有多少个音、音区从多低到多高）。
我们要做一个和音乐同步的视频：对着音乐某一刻（某个和弦、某处停顿、左手的某种动态、旋律的某次起伏、某几小节的变化）写下的感受，要到那几小节才出现，并把它说的那只手的音染上颜色；对着整段笼统的感受则整段都在。

请逐条判断：
- moment：这条要点是不是对着这一段里的某一刻或某几小节？只有原文里有依据（提到具体的声音、动作、变化、位置，或者“开头”“突然”“这时”“随后”之类，能和音乐概况对上）才算；只是整段的情绪就写 false。
- bars：是的话，落在这一段的哪几小节（起止小节号，必须在这一段范围内，尽量窄）；不是写空。
- hand：它说的是哪只手的声音：右手、左手、两手、说不清。原文没说到具体声音的写“说不清”。
- why：依据，引原文几个字，并说和哪几小节的音乐概况对上。
宁可判 false，也不要猜位置。

只输出 JSON：{"points":[{"id":"S06-B1-p1","moment":true,"bars":[40,41],"hand":"左手","why":"…"}]}，每条都要有。

{BODY}
"""
prompt_lint.lint(LOC, 'locate.LOC')


def loc_prompt():
    if V == 'direct': return LOC.replace('以及这一段逐小节的音乐概况（右手、左手各有多少个音、音区从多低到多高）', '以及这一段每小节的起止时间（这首曲子的一个录音）').replace('能和音乐概况对上', '能和你对这首曲子的了解对上').replace('并说和哪几小节的音乐概况对上', '并说你为什么认为是那几小节')
    if V == 'score': return LOC.replace('以及这一段逐小节的音乐概况（右手、左手各有多少个音、音区从多低到多高）', '以及这一段逐小节左右手的具体音').replace('能和音乐概况对上', '能和谱上的音对上').replace('并说和哪几小节的音乐概况对上', '并说和哪几小节谱上的什么音对上')
    return LOC


def music(w):
    import film_v8
    f = film_v8.Film8(w, 'g68K28b'); ns = f.song.notes
    parts = {}
    for n in ns: parts.setdefault(n.part, []).append(n.pitch)
    lh = min(parts, key=lambda k: np.mean(parts[k])); rh = max(parts, key=lambda k: np.mean(parts[k]))
    return f, lh, rh


def bar_summary(f, lh, rh, b):
    t0, t1 = f.bar_t[b], f.bar_end[b]; out = []
    for nm, p in (('右手', rh), ('左手', lh)):
        x = [n for n in f.song.notes if n.part == p and t0 <= n.time < t1]
        out.append(f"{nm} {len(x)} 个音" + (f"，音区 {min(n.pitch for n in x)}–{max(n.pitch for n in x)}" if x else ''))
    return f"第 {b} 小节（{t0:.1f}–{t1:.1f} 秒）：" + '；'.join(out)


V = os.environ.get('LOCV', '')   # 11-11 用户：“一种是让他自己调用乐谱 一种就是直接问他……我怀疑可能后者都够用”。'' = 逐小节概况；direct = 只给小节号和秒数；score = 逐小节具体的音
NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def bar_notes(f, lh, rh, b):
    t0, t1 = f.bar_t[b], f.bar_end[b]; out = []
    for nm, p in (('右手', rh), ('左手', lh)):
        x = sorted((n for n in f.song.notes if n.part == p and t0 <= n.time < t1), key=lambda n: (n.time, n.pitch))
        out.append(nm + '：' + ' '.join(f"{NAMES[n.pitch % 12]}{n.pitch//12-1}@{(n.time-t0)/(t1-t0):.2f}" for n in x))
    return f"第 {b} 小节（{t0:.1f}–{t1:.1f} 秒）" + NL + NL.join(out)


def bar_line(f, b): return f"第 {b} 小节：{f.bar_t[b]:.1f}–{f.bar_end[b]:.1f} 秒"


def body(w):
    src = rd(R2/f'{w}_src.json'); f, lh, rh = music(w); parts = []
    hd = {'': '【逐小节音乐概况】', 'direct': '【小节和时间】', 'score': '【逐小节的音（音名+八度@在小节里的位置，0 是小节开头、1 是结尾）】'}[V]
    fn = {'': lambda b: bar_summary(f, lh, rh, b), 'direct': lambda b: bar_line(f, b), 'score': lambda b: bar_notes(f, lh, rh, b)}[V]
    for s in src['sections']:
        a, z = [int(x) for x in s['bars'].replace('–', '-').split('-')]
        parts.append(f"### {s['sec']}（第 {a}–{z} 小节）" + NL + hd + NL + NL.join(fn(b) for b in range(a, z+1) if b in f.bar_t)
                     + NL + '【珠子】' + NL + NL.join(f"珠子 {b['id']} 原文：{b['text']}" + NL + NL.join(f"  - {p['id']}：{p['text']}" for p in b['points']) for b in s['beads']))
    pl = json.load(open(HERE.parent/'plans'/f'{w}_points.json', encoding='utf-8'))
    head = f"曲目：{pl.get('title', '')}（演奏：{pl.get('performer', '')}）" + NL
    return head + NL.join(parts), src, f


def one(a):
    w, j = a; p = S/f'locate{V}_{w}_{j}.json'
    if p.exists(): return
    txt, src, f = body(w); ids = {q['id'] for s in src['sections'] for b in s['beads'] for q in b['points']}
    for k in range(3):
        try:
            r = parse(call(f'locate{V}_{w}_{j}' + ('' if not k else f'_r{k}'), loc_prompt().replace('{BODY}', txt), {'g6': G6, 'g56': G56}[j], 'gpt3s', 'film-locate'))
            got = [x for x in r['points'] if x.get('id') in ids]; assert len(got) >= .9*len(ids), len(got); wr(p, {'points': got}); return
        except Exception as ex: print('不合格', w, j, repr(ex)[:150], flush=True)


def merge(w):
    src = rd(R2/f'{w}_src.json'); _, _, f = None, None, None
    import film_v8
    f = film_v8.Film8(w, 'g68K28b')
    h = {j: {x['id']: x for x in rd(S/f'locate{V}_{w}_{j}.json')['points']} for j in ('g6', 'g56')}
    out = {}; n = mom1 = 0
    for s in src['sections']:
        for b in s['beads']:
            for q in b['points']:
                n += 1; x, y = h['g6'].get(q['id']), h['g56'].get(q['id'])
                if not (x and y and x.get('moment') and y.get('moment') and x.get('bars') and y.get('bars')): mom1 += bool((x or {}).get('moment')) != bool((y or {}).get('moment')); continue
                a0, a1 = sorted(x['bars'][:2] if len(x['bars']) > 1 else x['bars']*2); b0, b1 = sorted(y['bars'][:2] if len(y['bars']) > 1 else y['bars']*2)
                lo, hi = max(a0, b0), min(a1, b1)
                if lo > hi or lo not in f.bar_t or hi not in f.bar_end: continue
                hand = x.get('hand') if x.get('hand') == y.get('hand') and x.get('hand') in ('右手', '左手', '两手') else ''
                out[q['id']] = {'bars': [lo, hi], 'win': [f.bar_t[lo], f.bar_end[hi]], 'hand': hand, 'why': [x.get('why'), y.get('why')]}
    wr(S/f'locate{V}_{w}.json', out)
    ref = {q['id']: q['windows'][0] for s in src['sections'] for b in s['beads'] for q in b['points'] if q.get('local') and q.get('windows')}
    hit = sum(1 for i, rw in ref.items() if i in out and out[i]['win'][0] < rw[1] and rw[0] < out[i]['win'][1])
    print(w, f"做法「{V or '概况'}」对照原料里本来就有时间窗的 {len(ref)} 条：定到并且时间重叠 {hit} 条，定到但不重叠 {sum(1 for i in ref if i in out) - hit} 条", flush=True)
    print(w, '要点', n, '两位都定到同一处', len(out), '其中声部也一致', sum(bool(v['hand']) for v in out.values()), '｜是否对着某一刻两位意见不同', mom1, flush=True)


if __name__ == '__main__':
    with ThreadPoolExecutor(4) as ex: list(ex.map(one, [(w, j) for w in WORKS for j in ('g6', 'g56')]))
    for w in WORKS: merge(w)
