"""Mechanical application of fully read, approved local model edits; no calls."""
import copy
import json
import re
import sys
import experiment_batch as B
import round34_restore as R


def checked(w, base, rid, limit=8, preserve_ending=False):
    if not B.reviewed(rid):
        raise ValueError(f'{rid}: full-read approval missing')
    answer = B.V.parse(rid)
    if not isinstance(answer, dict) or not isinstance(answer.get('edits'), list):
        raise ValueError('edits JSON missing')
    graph = copy.deepcopy(B.V.graph_of(w, base))
    original = B.V.index(graph)
    touched = set()
    for e in answer['edits']:
        if e.get('op') not in ('replace', 'delete') or e.get('id') not in original:
            raise ValueError(f'unknown operation or ID: {e}')
        if e['id'] in touched:
            raise ValueError('duplicate edit')
        touched.add(e['id'])
        if preserve_ending and original[e['id']][0]['sec'] == graph['segments'][-1]['sec']:
            raise ValueError('ending changed in preserve-ending experiment')
        if e['op'] == 'replace':
            text = e.get('text', '')
            if not text.strip() or text != R.clean(text):
                raise ValueError('empty text or copied citation markup')
            if len(re.findall(r'[。！？!?]', text)) != 1 or text[-1] not in '。！？!?':
                raise ValueError(f'not one complete sentence: {e}')
            original[e['id']][1]['text'] = text
        else:
            original[e['id']][0]['items'].remove(original[e['id']][1])
    if len(touched) > limit or any(not 2 <= len(s['items']) <= 4 for s in graph['segments']):
        raise ValueError('edit limit or section shape violated')
    total = lambda g: sum(len(i['text']) for s in g['segments'] for i in s['items'])
    # Prompt's length target is a workflow preference, not a user standard or
    # acceptance threshold. Preserve and report deviations; do not trim text.
    answer['_length_target_deviation'] = max(0, total(graph) - total(B.V.graph_of(w, base)))
    return answer


def apply(tag, base='r49b', preserve_ending=False):
    answers = {w: checked(w, base, f'sc{tag}_{w}_A5', preserve_ending=preserve_ending) for w in B.F.WORKS}
    for w, answer in answers.items():
        if (B.V.OUT / f'{w}_{tag}.json').exists():
            raise ValueError('target already exists')
    for w, answer in answers.items():
        R.apply(w, tag, base, answer)
    receipt = {'tag': tag, 'base': base, 'body_source': 'approved model edits only', 'calls': 0,
               'length_target_deviation_chars': {w: a['_length_target_deviation'] for w, a in answers.items()},
               'output_hashes': {w: B.digest((B.V.OUT / f'{w}_{tag}.json').read_text(encoding='utf-8')) for w in B.F.WORKS}}
    B.write_frozen(B.ROOT / 'runs/_batches/round50_from_r49b' / f'{tag}_applied.json', B.json_text(receipt))


def apply_labels(source, target):
    prepared = {}
    for w in B.F.WORKS:
        rid = f'sc{source}_{w}_A11'
        if not B.reviewed(rid):
            raise ValueError('label full-read approval missing')
        d = json.loads((B.V.OUT / f'{w}_{source}.json').read_text(encoding='utf-8'))
        response = B.V.parse(rid)['relations']
        rel = {x['sec']: x['relation'] for x in response}
        if (len(rel) != len(response) or set(rel) != {s['sec'] for s in d['graph']['segments']}
                or set(rel.values()) - {'没在想', '还说不清', '正在面对'}):
            raise ValueError('invalid labels')
        before = [i['text'] for s in d['graph']['segments'] for i in s['items']]
        for s in d['graph']['segments']:
            s['relation'] = rel[s['sec']]
        assert before == [i['text'] for s in d['graph']['segments'] for i in s['items']]
        d['base'] = f'{source}, model-only Center relationship labels, {rid}'
        prepared[w] = d
    for w, d in prepared.items():
        B.write_frozen(B.V.OUT / f'{w}_{target}.json', B.json_text(d))
        B.write_frozen(B.V.OUT / f'{w}_{target}.md', f'# {w}｜线（{target}）\n\n' + B.V.view(d['graph']))


if __name__ == '__main__':
    apply(sys.argv[1], preserve_ending='progress' in sys.argv[1])
