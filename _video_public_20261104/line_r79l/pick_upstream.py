"""上游两处选择改成规则，不靠人挑。作品无关。
python pick_upstream.py seg 作品     从 N01 调研到的全部公开分段表里，选每段时长最接近目标的一张（相邻段共享的小节归后一段）。
python pick_upstream.py center 作品  从 N04 的评审里，选解释力和展开空间都高的 Center 候选；并列看专属性。
规则：视频一屏要停留够读、又不能一屏太久；船歌和幻想的段落平均 36–54 秒，取其中间作为目标。
"""
import json, re, sys
from pathlib import Path
EVO = Path('D:/musicclaude/_thread_evo_20261019'); sys.path.insert(0, str(EVO)); sys.stdout.reconfigure(encoding='utf-8')
import seg as SEG, work_meta
TARGET = 45.


def tables(j, total):
    for s in j['sources']:
        for l in s.get('levels', []):
            try: rows = [(int(x['start']), int(x['end']), x.get('label', '')) for x in l['segments']]
            except (TypeError, ValueError, KeyError): continue
            out = []
            for i, (a, b, lab) in enumerate(rows):
                if i+1 < len(rows) and rows[i+1][0] == b: b -= 1
                out.append({'start': a, 'end': b, 'label': lab})
            if out and not SEG.validate(out, total): yield s, l, out


def pick_seg(w):
    j = json.loads((EVO/f'runs/seg_{w}_v1/parsed.json').read_text(encoding='utf-8')); total = int(j['total_measures']); spm = work_meta.load(w)['seconds_per_measure']; rows = []
    for s, l, segs in tables(j, total):
        avg = total*spm/len(segs); longest = max(x['end']-x['start']+1 for x in segs)*spm
        rows.append((abs(avg-TARGET)+max(0, longest-3*TARGET)/10, s, l, segs, avg, longest))
    rows.sort(key=lambda r: r[0])
    for r in rows: print(round(r[0], 1), (r[1].get('author_or_institution') or '')[:24], r[2]['level'][:22], '段', len(r[3]), '平均秒', round(r[4]), '最长秒', round(r[5]))
    _, s, l, segs, *_ = rows[0]; source = {k: s.get(k) for k in ('id', 'author_or_institution', 'title', 'url', 'locator', 'accessed_original')}
    source.update({'level': l['level'], 'run': f'seg_{w}_v1', 'note': f'按规则选：每段平均时长最接近 {TARGET} 秒；相邻段共享小节归后一段。', 'numbering_note': j.get('numbering_note'), 'disagreements': j.get('disagreements')})
    d = SEG.build(j.get('work') or SEG.CFG[w]['work'], j.get('short_name') or w, total, segs, source, 'published_structure_rule_pick', [])
    print('选中', source['author_or_institution'], l['level'], [x['start'] for x in segs])
    if not (EVO/f'works/{w}/segmentation.json').exists(): SEG.save(w, d)
    return d


def pick_center(w):
    cand = []; log = Path(__file__).parent/f'qa/log/{w}_N04.log'
    for ln in log.read_text(encoding='utf-8', errors='ignore').splitlines():
        m = re.match(r'\|\s*(N\d+)\s*\|[^|]*\|\s*(\d+)%\s*\|\s*(\d+)%\s*\|[^|]*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([^|]+?)\s*\|', ln)
        if m: cand.append({'id': m[1], 'spec': int(m[2]), 'fit': int(m[3]), 'room': float(m[4]), 'convince': float(m[5]), 'center': m[6]})
    cand.sort(key=lambda c: (c['fit']+10*c['room'], c['spec']), reverse=True)
    for c in cand: print(c)
    print('选中', cand[0]['center']); return cand[0]['center']


if __name__ == '__main__':
    c, w = sys.argv[1:3]
    if c == 'seg': pick_seg(w)
    else: pick_center(w)
