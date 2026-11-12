"""Freeze a fully reviewed acceptance and arrange immutable deliverables. No calls."""
import json
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import experiment_batch as B
import round37_fair as FAIR
import screen_flow as F
import covjudge
import v6weave


def accept(tag, base):
    reviews = []
    for w in F.WORKS:
        for j in F.JUDGES:
            reviews += [f'v6b3_{w}_{j}_{tag}_vs{base}_{seat}' for seat in ('newX', 'newY')]
            reviews += [f'{prefix}_{w}_{j}_{t}' for prefix in ('cov2', 'al2') for t in (base, tag)]
    assert all(B.reviewed(rid) for rid in reviews), 'A full-read, hash-bound review is missing'
    fair = FAIR.summary(tag, base)
    assert fair['complete'] == 8 and fair['pass'], fair
    floors = F.floor_state(tag, base)
    assert floors['status'] == 'pass', floors
    for w in F.WORKS:
        graph = B.V.graph_of(w, tag)
        expected = {s['sec'] for s in graph['segments']}
        expected_beads = {(b['sec'], b['id'].split('-')[-1]) for b in covjudge.beads(w) if b['role'] != '演奏条件'}
        assert graph['center'] == B.V.graph_of(w, base)['center']
        assert all(2 <= len(s['items']) <= 4 for s in graph['segments'])
        for j in F.JUDGES:
            d = B.V.parse(f'cov2_{w}_{j}_{tag}')['beads']
            assert len(d) == len(expected_beads) and {(x['sec'], x['bead']) for x in d} == expected_beads
            d = B.V.parse(f'al2_{w}_{j}_{tag}')['sections']
            assert len(d) == len(expected) and {x['sec'] for x in d} == expected
            assert all(x['self'] in ('成立', '勉强', '不成立') for x in d)
        for j in F.JUDGES:
            for seat in ('newX', 'newY'):
                d = B.V.parse(f'v6b3_{w}_{j}_{tag}_vs{base}_{seat}')
                assert len(d['sections']) == len(expected) and {x['sec'] for x in d['sections']} == expected
                assert all(x[k] in ('X', 'Y', '差不多') for x in d['sections'] for k in F.DIMENSIONS)
                assert all(d[k] in ('是', '否') for k in ('X_replacing_Y_regress', 'Y_replacing_X_regress'))
    v6weave.main(tag)
    out = B.ROOT / f'deliver_20261103_{tag}'
    out.mkdir(exist_ok=True)
    integrity = {}
    for w in F.WORKS:
        graph = B.V.graph_of(w, tag)
        joined = (B.V.OUT / f'合写_{w}_{tag}.md').read_text(encoding='utf-8')
        items = [i['text'] for s in graph['segments'] for i in s['items']]
        beads = [b for b in covjudge.beads(w) if b['role'] != '演奏条件']
        # N03i is the already accepted display wording used by v6weave and the
        # r49b delivery. The audit's canonical wording is a separate source.
        for folder in ('beads_clean', 'beads_lang'):
            source = B.ROOT / 'evaluations' / folder / f'{w}.json'
            if source.exists():
                overlay = json.loads(source.read_text(encoding='utf-8'))
                beads = [dict(b, text=overlay.get(b['id'], b['text'])) for b in beads]
        baseline_joined = (B.ROOT / f'deliver_20261103_{base}' / f'{w}_线与珠子_{base}.md').read_text(encoding='utf-8')
        assert all(baseline_joined.count(b['text']) == 1 for b in beads), 'Display beads differ from accepted baseline'
        assert all(joined.count(t) == 1 for t in items), 'Missing or repeated line text'
        assert all(joined.count(b['text']) == 1 for b in beads), 'Missing or repeated canonical bead text'
        B.write_frozen(out / f'{w}_只看线_{tag}.md', f'# {w}｜线（{tag}）\n\n' + B.V.view(graph))
        B.write_frozen(out / f'{w}_线与珠子_{tag}.md', joined)
        integrity[w] = {'线条数': len(items), '字数': sum(map(len, items)), '珠子数': len(beads),
                        '珠子逐字一致': True, '线逐字在合写内': True,
                        '每段条数': [len(s['items']) for s in graph['segments']],
                        '珠子版本': 'N03i display wording, unchanged from accepted baseline delivery',
                        'source_sha256': B.digest((B.V.OUT / f'{w}_{tag}.json').read_text(encoding='utf-8'))}
    B.write_frozen(out / 'integrity.json', B.json_text(integrity))
    receipt = {'tag': tag, 'base': base, 'accepted_at': datetime.now(ZoneInfo('America/New_York')).isoformat(),
               'fair': fair, 'floor': floors, 'integrity': integrity,
               'review_output_hashes': {rid: B.digest(B.evo.output(rid)) for rid in reviews},
               'scope': 'Accepted comparison and floors; unresolved diagnostic issues remain. Annotation r49b stays bound to r49b.'}
    B.write_frozen(B.ROOT / 'runs/_batches/round50_from_r49b' / f'{tag}_acceptance.json', B.json_text(receipt))
    print(B.json_text({'accepted': tag, 'base': base, 'delivery': str(out), 'integrity': integrity}))


if __name__ == '__main__':
    accept(*sys.argv[1:3])
