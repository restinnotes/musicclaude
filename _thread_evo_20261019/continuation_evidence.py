"""Read-only evidence bindings; inspection receipts must already exist."""
import argparse
import json
import continue_r80 as C
import round50_measure as M
import screen_flow as F
import v6fix as V
import v6alone
import v6cov
import verdict


def bind(rid, expected):
    p = C.ROOT / 'runs' / rid
    actual = (p / 'input.txt').read_text(encoding='utf-8')
    assert actual == expected, (rid, 'input mismatch')
    ih = C.digest(actual)
    oh = C.digest((p / 'output.txt').read_text(encoding='utf-8'))
    receipt = json.loads((p / 'inspection_r80.json').read_text(encoding='utf-8'))
    assert receipt['read_complete'] and receipt['input_sha256'] == ih and receipt['output_sha256'] == oh, rid
    call=json.loads((p/'call.log').read_text(encoding='utf-8'))
    assert call.get('completed'),rid
    return {'rid': rid, 'input_sha256': ih, 'output_sha256': oh,'read_complete':True,
            'model':call.get('model'),'effort':call.get('thinking_effort'),'route':call.get('route')}


def floor(tag, base, kind):
    rows = []
    for w in F.WORKS:
        g = V.graph_of(w, tag)
        msg = (v6cov.COV2.format(NAME=V.covjudge.NAME[w], WHAT=V.WHAT2, LINE=V.view(g), BEADS=V.beads(w))
               if kind == 'coverage' else v6alone.ALONE2.format(NAME=V.covjudge.NAME[w], LINE=v6alone.line_ids(g)))
        for j in F.JUDGES:
            rid = f'{"cov2" if kind == "coverage" else "al2"}_{w}_{j}_{tag}'
            assert (verdict.cov_secs(w,j,tag) if kind == 'coverage' else verdict.alone_count(w,j,tag)) is not None, rid
            rows.append(bind(rid, msg))
    data = {'reviews': rows, 'state': F.floor_state(tag, base, kind)}
    C.write(C.BATCH / f'{tag}_{kind}_binding.json', data)
    print(tag, kind, data['state'])


def fair(tag, base):
    dest = C.BATCH / 'completed_review_binding.json'
    old = json.loads(dest.read_text(encoding='utf-8')) if dest.exists() else []
    # Preserve the original structure used by earlier continuation receipts.
    key = 'bound_reviews' if isinstance(old,dict) and 'bound_reviews' in old else 'reviews'
    rows = old if isinstance(old, list) else old.get(key, []) + (old.get('reviews', []) if key != 'reviews' else [])
    indexed = {r['rid']: r for r in rows}
    for rid, msg, _ in M.jobs('fair',tag,base):
        if (C.ROOT/'runs'/rid/'output.txt').exists():
            indexed[rid] = {**bind(rid, msg),'tag':tag,'comparison_base':base}
    data = list(indexed.values()) if isinstance(old,list) else {**{k:v for k,v in old.items() if k != 'reviews'},key:list(indexed.values())}
    if isinstance(data,dict):
        if 'base' in data:
            data['initial_base']=data.pop('base')
        data['base_scope']='Per review run id; later comparisons may use the fixed anchor.'
    C.write(dest,data)
    print(tag, base, 'bound', len(indexed))


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('kind',choices=['coverage','alone','fair'])
    p.add_argument('tag')
    p.add_argument('--base',default='r78a')
    a=p.parse_args()
    fair(a.tag,a.base) if a.kind=='fair' else floor(a.tag,a.base,a.kind)
