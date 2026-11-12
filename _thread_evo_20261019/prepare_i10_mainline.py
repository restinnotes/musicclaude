"""Stage I10 copies of the unchanged mainline; no model calls or product edits.

Existing N12 bead placement is retained. Only citations are rendered again from
the already checked qurefs graph. These staged files do not certify I14.
"""
import json
from collections import Counter

import covjudge
import experiment_batch as B

DEST = B.ROOT / 'runs/_batches/i14_after_round30/reviewable_delivery'


def body(g):
    return {'center': g['center'], 'segments': [
        {'sec': s['sec'], 'bars': s['bars'], 'relation': s['relation'],
         'items': [{k: v for k, v in item.items() if k != 'cite'} for item in s['items']]}
        for s in g['segments']]}


def visible_beads(w):
    beads = [dict(b) for b in covjudge.beads(w) if b['role'] != '演奏条件']
    for name in ('beads_clean', 'beads_lang'):
        path = B.ROOT / 'evaluations' / name / f'{w}.json'
        if path.exists():
            patch = json.loads(path.read_text(encoding='utf-8'))
            beads = [dict(b, text=patch.get(b['id'], b['text'])) for b in beads]
    return beads


def prepare():
    receipts = {}
    for w in B.F.WORKS:
        original, graph = (B.V.graph_of(w, tag) for tag in ('qu', 'qurefs'))
        if body(original) != body(graph):
            raise ValueError('only citations may differ: ' + w)
        source = B.V.OUT / f'合写_{w}_qu.md'
        paragraphs = source.read_text(encoding='utf-8').split('\n\n')
        old_items = [line[2:] for line in B.V.view(original).splitlines() if line.startswith('- ')]
        new_items = [line[2:] for line in B.V.view(graph).splitlines() if line.startswith('- ')]
        assert len(old_items) == len(new_items) == sum(len(s['items']) for s in graph['segments'])
        # Exact paragraph positions preserve all original bead arrangement.
        cursor = 0
        for old, new in zip(old_items, new_items):
            hits = [i for i in range(cursor, len(paragraphs)) if paragraphs[i] == old]
            if len(hits) != 1:
                raise ValueError('ambiguous or missing original item paragraph: ' + old)
            pos = hits[0]
            paragraphs[pos] = new
            cursor = pos + 1
        joined = '\n\n'.join(paragraphs)
        beads = visible_beads(w)
        expected = Counter('> ' + ('也可以听成：' if b['role'] == '另一种理解' else '') + b['text'] for b in beads)
        actual = Counter(line for line in joined.splitlines() if line.startswith('> ') and not line.startswith('> <small>'))
        if expected != actual:
            raise ValueError('bead text missing, changed, added or duplicated: ' + w)
        # Exact line item sequence, stripping only optional rendering citations.
        rendered = [p for p in paragraphs if p in set(new_items)]
        if rendered != new_items:
            raise ValueError('line items changed or reordered: ' + w)
        title = covjudge.NAME[w]
        line_only = f'# {title}｜只看线（Q15/qu，引用恢复版 qurefs）\n\n' + B.V.view(graph) + '\n'
        joined = joined.replace('\n\n', '\n\n版本：Q15/qu（引用恢复版 qurefs）。\n\n', 1)
        B.write_frozen(DEST / f'{w}_只看线_Q15qu.md', line_only)
        B.write_frozen(DEST / f'{w}_线与珠子_Q15qu.md', joined)
        receipts[w] = {'mainline_body_unchanged': True, 'item_count': len(new_items),
                       'bead_count': len(beads), 'line_sha256': B.digest(line_only),
                       'joined_sha256': B.digest(joined), 'arrangement_source': str(source),
                       'arrangement_source_sha256': B.digest(source.read_text(encoding='utf-8')),
                       'citation_graph_sha256': B.digest(B.json_text(graph)),
                       'placement': 'Existing N12/qu arrangement, same line text and bead text; not a new coverage measurement.'}
    B.write_frozen(DEST / 'integrity.json', B.json_text({'staged_only': True, 'i14': 'pending', 'works': receipts}))
    print(B.json_text(receipts))


if __name__ == '__main__':
    prepare()
