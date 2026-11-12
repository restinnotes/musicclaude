"""Read-only local evidence checks for the paired continuation (no model calls)."""
import argparse
import json
import os
from pathlib import Path
os.environ.setdefault('JV', '2')
import continue_r80 as C
import round37_fair as FAIR
import screen_flow as F
import v6fix as V

def candidate(tag, base, stage='F2'):
    data = {'tag': tag, 'base': base, 'stage': stage, 'works': {}, 'issues': []}
    manifests = [json.loads(p.read_text(encoding='utf-8'))
                 for p in C.BATCH.glob('*_manifest.json')]
    manifest = next((m for m in manifests if tag in m.get('tags', [])), {})
    for w in F.WORKS:
        rid = f'sc{tag}_{w}_{stage}'
        source, current = V.graph_of(w, base), V.graph_of(w, tag)
        answer = V.parse(rid)
        assert answer is not None, rid
        old = {i['id']: i['text'] for s in source['segments'] for i in s['items']}
        new = {i['id']: i['text'] for s in current['segments'] for i in s['items']}
        assert source['center'] == current['center']
        assert [(s['sec'], s['bars']) for s in source['segments']] == [(s['sec'], s['bars']) for s in current['segments']]
        assert all(2 <= len(s['items']) <= 4 for s in current['segments'])
        expected = {e['id'].split('+')[0] for e in answer.get('edits', [])}
        changed = {i for i in old.keys() | new.keys() if old.get(i) != new.get(i)}
        assert changed <= expected, (w, 'unexpected changed items', changed - expected)
        if manifest.get('surface_only_nonexpanding_items'):
            if any(e.get('op') != 'replace' for e in answer.get('edits', [])):
                data['issues'].append(f'{w}: surface-only production used a non-replace operation')
            if set(old) != set(new):
                data['issues'].append(f'{w}: surface-only production changed item IDs')
            if any(len(new.get(i, '')) > len(old.get(i, '')) for i in changed):
                data['issues'].append(f'{w}: surface-only production expanded an edited item')
            if len(answer.get('edits', [])) > manifest['max_edits']:
                data['issues'].append(f'{w}: production exceeded frozen edit limit')
        before, after = sum(map(len, old.values())), sum(map(len, new.values()))
        if after > before * 1.03:
            data['issues'].append(f'{w}: length growth exceeds prompt 3% cap')
        seen = set()
        for s in current['segments']:
            for i in s['items']:
                assert set(i.get('cite', [])) <= seen, (w, i['id'], i.get('cite'))
                seen.add(i['id'])
        folder = C.ROOT / 'runs' / rid
        call = json.loads((folder/'call.log').read_text(encoding='utf-8'))
        data['works'][w] = {'rid': rid, 'before_chars': before, 'after_chars': after,
                           'changed_ids': sorted(changed), 'output_sha256': C.digest((folder/'output.txt').read_text(encoding='utf-8')),
                           'input_sha256': C.digest((folder/'input.txt').read_text(encoding='utf-8')),
                           'line_sha256': C.digest(V.view(current)), 'beads_sha256': C.digest(V.beads(w)),
                           'route': call.get('route'), 'model': call.get('model'), 'effort': call.get('thinking_effort')}
    data['mechanical_pass'] = not data['issues']
    C.write(C.BATCH / f'{tag}_mechanical.json', data)
    print(json.dumps(data, ensure_ascii=False, indent=2))

def fair(tag, base, phase):
    rows, missing = [], []
    for w in F.WORKS:
        for j in F.JUDGES:
            for seat in ('newX', 'newY'):
                quick_seat = 'newX' if (w,j) in (('op60','g6'),('op61','g56')) else 'newY'
                if phase == 'quick' and seat != quick_seat:
                    continue
                rid = FAIR.rid_of(w,j,tag,base,seat)
                if not (C.ROOT/'runs'/rid/'output.txt').exists():
                    missing.append(rid)
                    continue
                d = V.parse(rid)
                sections = d.get('sections', [])
                expected = [s['sec'] for s in V.graph_of(w,tag)['segments']]
                assert len(sections) == len(expected) and {s['sec'] for s in sections} == set(expected), rid
                assert all(s.get(k) in ('X','Y','差不多') for s in sections for k in F.DIMENSIONS), rid
                new = 'X' if seat == 'newX' else 'Y'
                assert d.get('better') in ('X','Y','差不多') and d.get(f'{new}_replacing_{"Y" if new=="X" else "X"}_regress') in ('是','否'), rid
                row = FAIR.read(w,j,tag,base,seat)
                row['rid'] = rid
                row['output_sha256'] = C.digest((C.ROOT/'runs'/rid/'output.txt').read_text(encoding='utf-8'))
                rows.append(row)
    def aggregate(rs):
        return {'n':len(rs), 'wins':sum(r['new_win'] for r in rs),
                'no_regress':sum(r['no_regress'] for r in rs),
                'net':{k:sum(r['net'][k] for r in rs) for k in F.DIMENSIONS}}
    total = aggregate(rows)
    needed = 3 if phase == 'quick' else 6
    total['pass'] = not missing and total['wins'] >= needed and all(total['net'][k]>=0 for k in F.DIMENSIONS[:3]) and (phase=='quick' or total['no_regress']>=6)
    data={'tag':tag,'base':base,'phase':phase,'total':total,
          'per_work':{w:aggregate([r for r in rows if r['w']==w]) for w in F.WORKS},
          'missing':missing,'rows':rows}
    if phase == 'full':
        for row in data['per_work'].values():
            row['pass'] = (row['n']==4 and row['wins']>=3 and row['no_regress']>=3
                           and all(row['net'][k]>=0 for k in F.DIMENSIONS[:3]))
        data['paired_pass'] = total['pass'] and all(r['pass'] for r in data['per_work'].values())
    else:
        data['paired_pass'] = None  # Four-ticket screening is not acceptance.
    # Per-work results are reported separately; never replace the pair by a splice.
    C.write(C.BATCH / f'{tag}_vs{base}_{phase}_audit.json',data)
    print(json.dumps(data,ensure_ascii=False,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('action',choices=('candidate','quick','full'))
    p.add_argument('tag')
    p.add_argument('base')
    p.add_argument('--stage',default='F2')
    a=p.parse_args()
    candidate(a.tag,a.base,a.stage) if a.action=='candidate' else fair(a.tag,a.base,a.action)
