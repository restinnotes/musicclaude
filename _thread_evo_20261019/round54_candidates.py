"""Execute reviewed adviser mechanisms, pausing at every new full-read boundary.

No model prose is composed or repaired here. All prompts come from the frozen
adviser answers, except the sampling experiment deliberately reuses actual Q15.
"""
import argparse
import copy
import hashlib
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor

os.environ.setdefault('JV', '2')
import experiment_batch as B

BASE = 'r50progress1rr'
ROOT = B.ROOT / 'runs/_batches/round54_broader'
SELECTION = (
    ('r54role', 'r54_advisor_g6a', 0, 'rolemap'),
    ('r54ground', 'r54_advisor_g6b', 0, 'upstream'),
    ('r54weave', 'r54_advisor_g6a', 2, 'fullgraph'),
    ('r54reader', 'r54_advisor_g6b', 2, 'edits'),
    ('r54sample', 'r54_advisor_g6a', 3, 'sample'),
)


def prepare():
    candidates = []
    q15 = (B.ROOT / 'schemes/Q15_A4.txt').read_text(encoding='utf-8')
    for tag, author, index, mode in SELECTION:
        assert B.reviewed(author), author
        plan = B.V.parse(author)['candidates'][index]
        stages = copy.deepcopy(plan['steps'])
        if mode == 'sample':
            # Isolate the sampling mechanism. The adviser claimed verbatim Q15
            # reuse but supplied a different prompt; use the real source file.
            selector = stages[1]
            stages = [{'id': 'sample_A', 'prompt': q15}, {'id': 'sample_B', 'prompt': q15}, selector]
        if mode == 'upstream':
            stages.append({'id': 'A4', 'prompt': q15})
        frozen = []
        for k, step in enumerate(stages, 1):
            prompt = step['prompt']
            placeholders = sorted(set(re.findall(r'\{([A-Z_]+)\}', prompt)))
            assert set(placeholders) <= {'SECTIONS', 'CENTER', 'LINE', 'BEADS', 'REVIEWS', 'ROUTES', 'TARGETS', 'CANDIDATES'}
            if mode == 'upstream' and k < 3:
                assert not ({'BEADS', 'TARGETS', 'REVIEWS', 'LINE'} & set(placeholders))
            path = ROOT / 'prompts' / f'{tag}_P{k}.txt'
            B.write_frozen(path, prompt)
            frozen.append({'id': f'P{k}', 'author_id': step['id'], 'path': str(path.relative_to(B.ROOT)), 'sha256': B.digest(prompt), 'placeholders': placeholders})
        candidates.append({'tag': tag, 'author': author, 'author_index': index, 'name': plan['name'], 'mode': mode,
                           'hypothesis': plan['hypothesis'], 'risk': plan['risk'], 'steps': frozen})
    manifest = {'base': BASE, 'workers': 4, 'candidates': candidates,
                'source_hashes': {w: B.digest((B.V.OUT / f'{w}_{BASE}.json').read_text(encoding='utf-8')) for w in B.F.WORKS},
                'deduplication': '10 proposals collapse to role planning, upstream provenance, global reweave, unrestricted causal post-edit, and two-sample selection. SourceChain/EvidenceRoute overlap Grounded Spine; ArcFirst/ArcWeave overlap RoleMap; RoleRepair overlaps Reader Rebuild. Do not buy synonymous schemes to reach 10.',
                'sample_interface_correction': 'Sampling uses actual Q15_A4.txt verbatim, not adviser rewritten sample prompt; selector unchanged. Independent source hashes recorded.',
                'next': 'full read each new stage, apply only reviewed pairs, balanced quick4 against current mainline; no automatic advancement'}
    B.write_frozen(ROOT / 'candidates.json', B.json_text(manifest))
    B.write_frozen(ROOT / 'prompt_review.json', B.json_text({'approved': True, 'all_advisers_full_read': True,
        'generic_and_interfaces_checked': True, 'schema_and_model_unchanged': True,
        'stages': {c['tag']: [s['sha256'] for s in c['steps']] for c in candidates}}))
    print(B.json_text({'candidates': [c['tag'] for c in candidates], 'production_calls_max': 18, 'calls': 0}), flush=True)


def rid(c, w, k):
    return f"sc{c['tag']}_{w}_P{k}"


def parsed(r):
    assert B.evo.done(r), 'Do not parse or resubmit incomplete responses'
    return B.pipe.call(r, '', 'g6', 'R54')


def stage_seen(c, w, k):
    r = rid(c, w, k)
    if c['mode'] != 'sample' or k == 3:
        return B.reviewed(r)
    # A rejected inner sample does not invalidate the other independent draw.
    # Both must be read; the selector may only return an approved sample.
    p = B.evo.RUNS / r / 'inspection.json'
    if not p.exists() or not B.evo.done(r):
        return False
    d = json.loads(p.read_text(encoding='utf-8'))
    return d.get('read_complete') is True and d.get('output_sha256') == B.digest(B.evo.output(r))


def context(w, candidate=None):
    built, _ = B.pipe.work_context(w, BASE)
    spec = B.pipe.load_spec(B.ROOT / 'schemes/Q15.json')
    outputs = {s: B.pipe.call(f'scqu_{w}_{s}', '', 'g6', 'Q15') for s in ('A1', 'A2', 'A3')}
    sources = spec['_steps']['A4']['replace']
    reviews = []
    needs_reviews = not candidate or any('REVIEWS' in step['placeholders'] for step in candidate['steps'])
    if needs_reviews:
        for j in ('g6', 'g56', 'gem'):
            for k in ((1,) if j == 'gem' else (1, 2)):
                r = f'eo2_{w}_{BASE}_{j}_r{k}'
                assert B.reviewed(r)
                reviews.append({'rid': r, 'raw': B.evo.output(r)})
    if candidate and candidate.get('include_parent_blind'):
        import round50_measure as measure
        acceptance = json.loads((B.ROOT / 'runs/_batches/round50_from_r49b' / f'{BASE}_acceptance.json').read_text(encoding='utf-8'))
        for r, _, _ in measure.jobs('fair', BASE, acceptance['base']):
            assert B.reviewed(r), r
            reviews.append({'rid': r, 'scope': 'Current accepted version versus its parent; not a measurement of this candidate', 'raw': B.evo.output(r)})
    if candidate and candidate.get('paired_delta_context'):
        import round50_measure as measure
        import build_version_comparison as comparison
        acceptance = json.loads((B.ROOT / 'runs/_batches/round50_from_r49b' / f'{BASE}_acceptance.json').read_text(encoding='utf-8'))
        parent = acceptance['base']
        checked = comparison.comparison(BASE, parent)
        assert len(checked['rows']) == 8 and not checked['pending']
        paired = []
        for r, _, _ in measure.jobs('fair', BASE, parent):
            if f'_{w}_' not in r:
                continue
            assert B.reviewed(r)
            current_x = r.endswith('_newX')
            paired.append({'rid': r, 'X_version': BASE if current_x else parent,
                           'Y_version': parent if current_x else BASE, 'raw': B.evo.output(r)})
        assert len(paired) == 4
        reviews = {'current_version': BASE, 'baseline_version': parent,
                   'baseline_line': B.V.view(B.V.graph_of(w, parent), ids=True),
                   'paired_blind_reviews': paired, 'current_open_reviews': reviews,
                   'acceptance': acceptance,
                   'scope': 'Per-work complete paired4 plus current open5; joint acceptance records all8. Fixed BEADS are already accepted N03i display wording; original open reviews used canonical wording, no bead edits are permitted.'}
    bead_text = B.V.beads(w)
    if candidate and candidate.get('bead_input') == 'original_A3':
        bead_text = built['BEADS_TEXT']
    if candidate and candidate.get('bead_input') == 'N03i_display':
        overlay = {}
        for name in ('beads_clean', 'beads_lang'):
            path = B.ROOT / 'evaluations' / name / f'{w}.json'
            if path.exists():
                overlay.update(json.loads(path.read_text(encoding='utf-8')))
        for bead in B.V.covjudge.beads(w):
            if bead['role'] == '演奏条件':
                continue
            old, new = bead['text'], overlay.get(bead['id'], bead['text'])
            assert bead_text.count(old) == 1, 'Ambiguous bead input conversion'
            bead_text = bead_text.replace(old, new)
        delivery = B.ROOT / f'deliver_20261103_{BASE}' / f'{w}_线与珠子_{BASE}.md'
        delivered = delivery.read_text(encoding='utf-8')
        assert all(delivered.count(overlay.get(b['id'], b['text'])) == 1
                   for b in B.V.covjudge.beads(w) if b['role'] != '演奏条件')
    # These are data fields, not newly written production instructions.
    line_source = candidate.get('line_source', BASE) if candidate else BASE
    if line_source != BASE:
        assert B.digest((B.V.OUT / f'{w}_{line_source}.json').read_text(encoding='utf-8')) == candidate['line_source_hashes'][w]
    return {'SECTIONS': built['SEGMENTS'], 'CENTER': built['CENTER'],
            'LINE': B.V.view(B.V.graph_of(w, line_source), ids=True), 'BEADS': bead_text,
            'REVIEWS': B.json_text(reviews),
            'ROUTES': B.pipe.resolve(sources['{ROUTES}'], built, outputs),
            'TARGETS': B.pipe.resolve(sources['{TARGETS}'], built, outputs)}


def message(c, w, k):
    values = context(w, c)
    if c.get('route_sources'):
        source = c['route_sources'][w]
        assert B.reviewed(source['rid']), 'Read reused route output first'
        folder = B.evo.RUNS / source['rid']
        assert B.digest((folder / 'prepared_input.txt').read_text(encoding='utf-8')) == source['input_sha256']
        route = B.evo.output(source['rid'])
        assert B.digest(route) == source['output_sha256'], 'Reused route changed'
        values['ROUTES'] = route
    if c['mode'] == 'upstream' and k == 2:
        values['ROUTES'] = B.evo.output(rid(c, w, 1))
    if c['mode'] == 'upstream' and k == 3:
        values['ROUTES'] = B.evo.output(rid(c, w, 1)) + '\n\n【宏观评审结果】\n' + B.evo.output(rid(c, w, 2))
    if c['mode'] == 'route_trace' and k == 2:
        values['ROUTES'] = B.evo.output(rid(c, w, 1))
    if c['mode'] == 'affect' and k == 2:
        values['TARGETS'] = B.evo.output(rid(c, w, 1))
    if c['mode'] == 'sample' and k == 3:
        values['CANDIDATES'] = B.json_text({'A': parsed(rid(c, w, 1)), 'B': parsed(rid(c, w, 2))})
    step = c['steps'][k-1]
    prompt = (B.ROOT / step['path']).read_text(encoding='utf-8')
    assert B.digest(prompt) == step['sha256']
    for key in step['placeholders']:
        prompt = prompt.replace('{' + key + '}', values[key])
    return prompt


def verify_input(c, w, k):
    """Bind full instructions, including the existing long-prompt attachment route."""
    r = rid(c, w, k)
    folder = B.evo.RUNS / r
    expected = message(c, w, k)
    assert (folder / 'prepared_input.txt').read_text(encoding='utf-8') == expected
    assert (folder / 'prompt.txt').read_text(encoding='utf-8') == expected
    actual = (folder / 'input.txt').read_text(encoding='utf-8')
    proof = {'rid': r, 'full_input_sha256': B.digest(expected), 'body_sha256': B.digest(actual)}
    if actual == expected:
        return {**proof, 'mode': 'message_body'}
    receipt = json.loads((folder / 'call.log').read_text(encoding='utf-8'))
    assert receipt['completed'] and receipt['route'] == 'gpt3-serial'
    assert receipt['message_sha256'] == B.digest(actual)
    wrapper = ('这次的任务全文太长，放在附件 full_prompt.txt 里。请把附件从头到尾完整读完（不要只检索片段），'
               '然后严格按附件里的要求作答，只输出附件要求的格式。')
    assert actual == wrapper and len(expected) > 60000
    attachment = folder / 'full_prompt.txt'
    assert attachment.read_text(encoding='utf-8') == expected
    entries = json.loads((B.ROOT / receipt['job_directory'] / 'attachment-manifest.json').read_text(encoding='utf-8'))
    digest = hashlib.sha256(attachment.read_bytes()).hexdigest()
    assert entries == [{'name': 'full_prompt.txt', 'size': attachment.stat().st_size, 'sha256': digest}]
    return {**proof, 'mode': 'verified_full_prompt_attachment', 'attachment_bytes_sha256': digest}


def collect(route='mimic', only=None):
    import msvcrt
    os.environ['THREAD_ROUTE'] = route
    B.F.configure()
    manifest = json.loads((ROOT / 'candidates.json').read_text(encoding='utf-8'))
    assert manifest['base'] == BASE, 'Wrong baseline for frozen batch'
    for w, sha in manifest['source_hashes'].items():
        assert B.digest((B.V.OUT / f'{w}_{BASE}.json').read_text(encoding='utf-8')) == sha
    with (ROOT / 'production_receiver.lock').open('a+') as lock:
        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        def one(job):
            c, w = job
            disposition = ROOT / f'{c["tag"]}_disposition.json'
            if disposition.exists() and json.loads(disposition.read_text(encoding='utf-8')).get('status') in ('archive', 'hard_constraint_archive'):
                return {'tag': c['tag'], 'work': w, 'status': 'pair_archived_no_submission'}
            for k in range(1, len(c['steps'])+1):
                r = rid(c, w, k)
                inspected = B.evo.RUNS / r / 'inspection.json'
                inner_sample = c['mode'] == 'sample' and k < 3
                if inspected.exists() and json.loads(inspected.read_text(encoding='utf-8')).get('hard_constraints_ok') is False and not inner_sample:
                    return {'tag': c['tag'], 'work': w, 'rid': r, 'status': 'hard_rejected'}
                if c['mode'] == 'sample' and k == 3 and not any(B.reviewed(rid(c, w, n)) for n in (1, 2)):
                    return {'tag': c['tag'], 'work': w, 'status': 'both_inner_samples_rejected'}
                msg = message(c, w, k)
                B.write_frozen(B.evo.RUNS / r / 'prepared_input.txt', msg)
                if not B.evo.done(r):
                    try:
                        B.evo.check_submission(B.evo.G6)
                        answer = B.evo.call(r, msg, model=B.evo.G6, meta={'stage': f'{ROOT.name}-{c["mode"]}', 'web': True})
                        if not answer:
                            return {'tag': c['tag'], 'work': w, 'rid': r, 'status': 'incomplete_inspect_original_receiver'}
                    except Exception as e:
                        return {'tag': c['tag'], 'work': w, 'rid': r, 'status': 'not_complete', 'error': str(e)}
                if not stage_seen(c, w, k):
                    return {'tag': c['tag'], 'work': w, 'rid': r, 'status': 'full_read_required'}
            return {'tag': c['tag'], 'work': w, 'status': 'all_stages_reviewed'}
        tasks = [(c, w) for c in manifest['candidates'] if not only or c['tag'] in only for w in B.F.WORKS]
        with ThreadPoolExecutor(max_workers=4) as pool:
            rows = list(pool.map(one, tasks))
        (ROOT / 'production_collection.json').write_text(B.json_text({'terminal': True, 'route': route, 'rows': rows}), encoding='utf-8')
        print(B.json_text(rows), flush=True)


def checked_result(c, w):
    k = len(c['steps'])
    for n in range(1, k+1):
        assert stage_seen(c, w, n), f'Full read missing: {rid(c, w, n)}'
    d = parsed(rid(c, w, k))
    if c['mode'] == 'sample':
        assert any(B.reviewed(rid(c, w, n)) and d == parsed(rid(c, w, n)) for n in (1, 2)), 'Selector must return one approved sample unchanged'
    if c['mode'] == 'edits':
        g = copy.deepcopy(B.V.graph_of(w, BASE))
        by_id = B.V.index(g)
        seen = set()
        assert isinstance(d.get('edits'), list)
        for e in d['edits']:
            assert e['id'] in by_id and e['id'] not in seen and e['op'] in ('replace', 'delete'), e
            seen.add(e['id'])
            sec, item = by_id[e['id']]
            if e['op'] == 'replace':
                item['text'] = e['text']
            else:
                sec['items'].remove(item)
        d = {'segments': g['segments']}
    return validate_graph(d, w)


def validate_graph(d, w):
    """The same structural checks for complete final graphs and inner samples."""
    g_ref = B.V.graph_of(w, BASE)
    assert isinstance(d, dict) and isinstance(d.get('segments'), list), 'Complete segments missing'
    d = copy.deepcopy(d)
    # A model may repeat the exact supplied measure range in a section label.
    # Drop only that redundant label metadata, never infer or change boundaries.
    for s in d['segments']:
        if s['sec'] not in {ref['sec'] for ref in g_ref['segments']}:
            matching = [ref for ref in g_ref['segments']
                        if s['sec'] == f"{ref['sec']}｜{ref['bars']} 小节"]
            assert len(matching) == 1, f'Unknown section or changed measure range: {s["sec"]}'
            s['sec'] = matching[0]['sec']
    assert [s['sec'] for s in d['segments']] == [s['sec'] for s in g_ref['segments']], 'Exact section order/set required'
    seen = set()
    for s in d['segments']:
        assert s.get('relation') in ('没在想', '还说不清', '正在面对'), s['sec']
        assert 2 <= len(s['items']) <= 4, s['sec']
        for it in s['items']:
            text = it['text']
            assert isinstance(text, str) and text.strip() and text == text.strip(), it
            assert len(re.findall(r'[。！？!?]', text)) == 1 and text[-1] in '。！？!?', f'Not one complete sentence: {it}'
            assert not re.search(r'〔[^〕]*〕|\[S\d+-\d+\]', text), 'Copied cite markup in body'
            assert isinstance(it.get('id'), str) and it['id'] not in seen
            assert isinstance(it.get('cite', []), list) and all(cite in seen for cite in it.get('cite', [])), f'Nonexistent/forward/deleted cite: {it}'
            seen.add(it['id'])
    return d


def apply(tag):
    manifest = json.loads((ROOT / 'candidates.json').read_text(encoding='utf-8'))
    c = next(c for c in manifest['candidates'] if c['tag'] == tag)
    prepared = {w: checked_result(c, w) for w in B.F.WORKS}
    assert all(not (B.V.OUT / f'{w}_{tag}.json').exists() for w in B.F.WORKS), 'Never overwrite an existing version'
    for w, d in prepared.items():
        original_body = [i['text'] for s in d['segments'] for i in s['items']]
        B.pipe.save(w, B.V.graph_of(w, BASE), d, f'{BASE}; {c["name"]}; model output only', tag, BASE)
        after = B.V.graph_of(w, tag)
        assert original_body == [i['text'] for s in after['segments'] for i in s['items']], 'Mechanical conversion changed body'
    B.write_frozen(ROOT / f'{tag}_applied.json', B.json_text({'tag': tag, 'base': BASE,
        'body_source': 'fully read model result, mechanical conversion only', 'model_calls': 0,
        **({'route_sources': c['route_sources']} if c.get('route_sources') else {}),
        'source_rids': {w: rid(c, w, len(c['steps'])) for w in B.F.WORKS},
        'source_output_hashes': {w: B.digest(B.evo.output(rid(c, w, len(c['steps'])))) for w in B.F.WORKS},
        'graph_hashes': {w: B.digest((B.V.OUT / f'{w}_{tag}.json').read_text(encoding='utf-8')) for w in B.F.WORKS}}))


def quick_state(tag):
    """Audit the four balanced, fully read votes without submitting requests."""
    import round37_fair as fair
    import round50_measure as measure
    messages = {r: msg for r, msg, _ in measure.jobs('fair', tag, BASE)}
    rows, pending = [], []
    for w in B.F.WORKS:
        expected = [s['sec'] for s in B.V.graph_of(w, BASE)['segments']]
        for j in B.F.JUDGES:
            seat = 'newX' if (w, j) in (('op60', 'g6'), ('op61', 'g56')) else 'newY'
            r = fair.rid_of(w, j, tag, BASE, seat)
            if not B.reviewed(r):
                pending.append({'rid': r, 'done': B.evo.done(r), 'read': False})
                continue
            assert (B.evo.RUNS / r / 'prepared_input.txt').read_text(encoding='utf-8') == messages[r], r
            d = B.V.parse(r)
            assert len(d['sections']) == len(expected) and {s['sec'] for s in d['sections']} == set(expected), r
            assert d['better'] in ('X', 'Y', '差不多')
            assert all(s[k] in ('X', 'Y', '差不多') for s in d['sections'] for k in B.F.DIMENSIONS)
            assert all(d[k] in ('是', '否') for k in ('X_replacing_Y_regress', 'Y_replacing_X_regress'))
            rows.append({'rid': r, 'output_sha256': B.digest(B.evo.output(r)),
                         'input_sha256': B.digest(messages[r]), **fair.read(w, j, tag, BASE, seat)})
    sums = {k: sum(r['net'][k] for r in rows) for k in B.F.DIMENSIONS}
    wins = sum(r['new_win'] for r in rows)
    d = {'tag': tag, 'base': BASE, 'complete': len(rows), 'pending': pending,
         'wins': wins, 'no_regress': sum(r['no_regress'] for r in rows),
         'net_sums': sums, 'pass': len(rows) == 4 and wins >= 3 and all(sums[k] >= 0 for k in B.F.DIMENSIONS[:3]),
         'cannot_reach_3_wins': wins + len(pending) < 3, 'rows': rows}
    (ROOT / f'{tag}_quick.json').write_text(B.json_text(d), encoding='utf-8')
    return d


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=('prepare', 'collect', 'apply', 'quick'))
    p.add_argument('--route', default='mimic', choices=('mimic', 'gpt3s'))
    p.add_argument('--only', help='comma separated frozen tags; no simultaneous collectors')
    p.add_argument('--base', default=BASE)
    p.add_argument('--batch', default=ROOT.name)
    args = p.parse_args()
    assert all(x and all(ch.isalnum() or ch in '_-' for ch in x) for x in (args.base, args.batch))
    BASE, ROOT = args.base, B.ROOT / 'runs/_batches' / args.batch
    if args.action == 'prepare':
        assert BASE == 'r50progress1rr' and ROOT.name == 'round54_broader', 'New batches require a separately reviewed frozen selection'
        prepare()
    elif args.action in ('apply', 'quick'):
        assert args.only and ',' not in args.only, 'apply/quick requires one --only tag'
        if args.action == 'apply':
            apply(args.only)
        else:
            print(B.json_text(quick_state(args.only)), flush=True)
    else:
        collect(args.route, args.only.split(',') if args.only else None)
