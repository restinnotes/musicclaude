"""新作品从珠子到大众版输入：不改主线脚本，只在内存里加这首作品。
python op52_up.py struct      整理珠子（N03 最终结果 + N03h 去编辑句）
python op52_up.py lines TAG "Center 句"   N05a–d 写线（沿用 Q15）
python op52_up.py src TAG     覆盖评委定匹配（N12 的放法）后生成 r2/{w}_src.json
"""
import json, os, re, sys
from pathlib import Path
os.environ.setdefault('JV', '2'); os.environ.setdefault('WORK', 'op52'); os.environ['THREAD_ROUTE'] = 'gpt3s'
W = os.environ.get('PUB_WORK', 'op52')
ROOT = Path(__file__).resolve().parent; EVO = Path('D:/musicclaude/_thread_evo_20261019'); sys.path.insert(0, str(EVO)); sys.stdout.reconfigure(encoding='utf-8')
import evo, covjudge, work_meta
META = work_meta.load(W); STRUCT = META['_dir']/'struct'; RUNS = META['_dir']/'bead'/'runs'; SEG = json.loads((META['_dir']/'segmentation.json').read_text(encoding='utf-8'))
covjudge.NAME[W] = f"{META['title_zh']}{META['opus']}"; covjudge.STRUCT[W] = STRUCT
import v6fix as V, v6cov


def rd(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def wr(p, x): Path(p).parent.mkdir(parents=True, exist_ok=True); Path(p).write_text(json.dumps(x, ensure_ascii=False, indent=1), encoding='utf-8')


def struct():
    import bead_clean as BC
    STRUCT.mkdir(parents=True, exist_ok=True); missing = []
    for s in SEG['segments']:
        sec = s['id']; f = next((RUNS/st/f'{sec}.parsed.json' for st in ('final2_b', 'final_b') if (RUNS/st/f'{sec}.parsed.json').exists()), None)
        if not f: missing.append(sec); continue
        d = rd(f); wr(STRUCT/f'{sec}.json', {'segment': sec, 'mm_start': s['start'], 'mm_end': s['end'], 'title': d.get('title'), 'reader': d.get('reader'), 'beads': [{k: b.get(k) for k in ('id', 'role', 'text', 'measures', 'placement', 'performance_condition')} for b in d.get('beads', [])], 'relations': d.get('relations', []), 'timeline': d.get('timeline', [])})
    if missing: sys.exit(f'缺 {missing}')
    bs = covjudge.beads(W); rid = f'bc2_{W}'
    evo.call(rid, BC.P.format(BEADS='\n'.join(f"[{b['id']}] {b['text']}" for b in bs)), model=evo.G6, meta={'stage': 'bead_clean'})
    old = {b['id']: b['text'] for b in bs}; new = dict(old); n = 0
    for x in (evo.parse_json(evo.output(rid) or '{}') or {}).get('beads') or []:
        i, t = x.get('id'), x.get('text') or ''
        if i in old and t and t != old[i] and BC.added_chars(old[i], t) <= 6 and len(t) < len(old[i]): new[i] = t; n += 1
    for s in SEG['segments']:
        p = STRUCT/f"{s['id']}.json"; d = rd(p)
        for b in d['beads']: b['text'] = new.get(f"{s['id']}-{b['id']}", b['text'])
        wr(p, d)
    print(W, '段', len(SEG['segments']), '珠子', len(bs), '去编辑句', n)


def skeleton():
    return {'center': CENTER, 'segments': [{'sec': s['id'], 'bars': f"{s['start']}–{s['end']}"} for s in SEG['segments']]}


def lines(tag, center):
    global CENTER; CENTER = center
    import pipe
    spec = pipe.load_spec(str(EVO/'schemes'/'Q15.json')); g = skeleton(); comp = META['composer']+(f"（{META['composer_en']}）" if META.get('composer_en') else '')
    builtins = {'WORK_INFO': f"作曲家：{comp}\n作品：{META['title_zh']}{META['opus']}", 'SEGMENTS': '\n'.join(f"{s['sec']}：第 {s['bars']} 小节" for s in g['segments']), 'CENTER': center, 'BEADS_TEXT': covjudge.bead_text(W)}
    wr(V.OUT/f'{W}_skel.json', {'graph': g, 'rows': []})
    pipe.run_work(spec, W, tag, None, 'skel', (builtins, g))


def src(tag):
    from concurrent.futures import ThreadPoolExecutor
    import pub2, v6weave
    g = V.graph_of(W, tag); texts = {s['sec']: [i['text'] for i in s['items']] for s in g['segments']}; votes = {}
    def one(j):
        rid = f'cov2_{W}_{j}_{tag}'
        if not evo.done(rid): evo.call(rid, v6cov.COV2.format(NAME=covjudge.NAME[W], WHAT=V.WHAT2, LINE=V.view(g), BEADS=V.beads(W)), model=V.JUDGES[j], meta={'stage': 'cov2'})
        return V.parse(rid) or {}
    with ThreadPoolExecutor(2) as ex: res = list(ex.map(one, V.JUDGES))
    from collections import Counter
    for r in res:
        for x in r.get('beads') or []:
            if x.get('status') in ('说清', '偏弱'):
                for n in v6weave.item_nums(x.get('items'), x['sec'], texts.get(x['sec'])): votes.setdefault((x['sec'], str(x['bead']).split('-')[-1]), Counter())[n] += 1
    music = rd(ROOT/f'input/{W}_music.json'); bars = dict((int(a), b) for a, b in music['bars']); out = {'work': W, 'center': g.get('center'), 'sections': []}
    def start(n): return bars.get(n, music['dur'])
    for s in SEG['segments']:
        sec = s['id']; lo, hi = start(s['start']), start(s['end']+1); dur = hi-lo; beads = []
        for i, b in enumerate(b for b in covjudge.beads(W) if b['sec'] == sec and b['role'] != '演奏条件'):
            short = b['id'].split('-')[-1]; v = votes.get((sec, short)); after = max(0, (max(v.items(), key=lambda kv: (kv[1], -kv[0]))[0] if v else len(texts[sec]))-1)
            m = re.search(r'(\d+)\s*[–—-]\s*(\d+)', str(b['measures'])) or re.search(r'(\d+)', str(b['measures']))
            a, z = (int(m.group(1)), int(m.group(m.lastindex))) if m else (s['start'], s['end']); a = max(a, s['start']); z = min(max(a, z), s['end'])
            wins = [[start(a), start(z+1)]]; local = wins[0][1]-wins[0][0] < .5*dur; pts = []
            for k, x in enumerate(pub2.SENT.finditer(b['text'])):
                t = x.group(0).strip()
                if t: pts.append({'id': f"{sec}-B{i+1}-p{k+1}", 'text': t, 'local': local, 'windows': wins})
            beads.append({'id': f'{sec}-B{i+1}', 'orig': b['id'], 'text': b['text'], 'where': str(b['measures']), 'after': min(after, len(texts[sec])-1), 'role': b['role'], 'points': pts})
        gs = next(x for x in g['segments'] if x['sec'] == sec)
        out['sections'].append({'sec': sec, 'bars': gs['bars'], 'window': [lo, hi], 'relation': gs.get('relation'), 'lines': [{'id': x['id'], 'text': x['text']} for x in gs['items']], 'beads': beads})
    wr(ROOT/f'r2/{W}_src.json', out); print(W, '段', len(out['sections']), '线', sum(len(x['lines']) for x in out['sections']), '珠', sum(len(x['beads']) for x in out['sections']), '要点', sum(len(b['points']) for x in out['sections'] for b in x['beads']))


if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'struct': struct()
    elif c == 'lines': lines(sys.argv[2], sys.argv[3])
    elif c == 'src': src(sys.argv[2])
