"""Batch proposals, exact-input reuse and crossed experiments.

prepare-advisors NAME -> run-advisors NAME -> import-advisors NAME
generate MANIFEST -> read returned stages and record inspection -> generate again
screen MANIFEST runs blind gates for the whole batch before survivor-only floors.
All run commands are explicit; preparing/importing/planning never calls a model.
"""
import argparse
import copy
import hashlib
import itertools
import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import screen_flow as F
import evo
import pipe
import v6fix as V

ROOT = Path(__file__).resolve().parent


def digest(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def write_frozen(path, data):
    path = Path(path)
    if path.exists():
        if path.read_text(encoding='utf-8') != data:
            raise ValueError(f'frozen artifact changed: {path}; choose a new batch/tag')
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data, encoding='utf-8')


def json_text(x):
    return json.dumps(x, ensure_ascii=False, indent=2)


def reuse_completed(rid, message, model, sources):
    """No fuzzy reuse, no stale predecessor output, no in-flight overwrite."""
    target = evo.RUNS / rid
    if (target / 'mg_request.json').exists() or (target / 'output.txt').exists():
        return False
    allowed = {'g6': {'gpt-6', 'gpt-6-thinking', 'gpt-6-sol'},
               'g56': {'gpt-5.6', 'gpt-5-6-thinking', 'gpt-5.6-sol'}}[model]
    for source in sources:
        folder = evo.RUNS / source
        if not evo.done(source):
            continue
        inp, rec = folder / 'input.txt', folder / 'call.log'
        if not inp.exists() or inp.read_text(encoding='utf-8') != message or not rec.exists():
            continue
        log = json.loads(rec.read_text(encoding='utf-8'))
        if (not log.get('completed') or log.get('model') not in allowed
                or log.get('thinking_effort') != 'high' or log.get('route') != 'mimic'):
            continue
        target.mkdir(exist_ok=True)
        raw = evo.output(source)
        # Copy original response exactly, not a parsed/reserialized substitute.
        (target / 'input.txt').write_text(message, encoding='utf-8')
        (target / 'prompt.txt').write_text(message, encoding='utf-8')
        (target / 'output.txt').write_text(raw, encoding='utf-8')
        receipt = {'source_run': source, 'input_sha256': digest(message),
                   'output_sha256': digest(raw), 'model': log['model'],
                   'thinking_effort': 'high', 'new_model_calls': 0}
        (target / 'reuse.json').write_text(json_text(receipt), encoding='utf-8')
        (target / 'call.log').write_text(json_text({**log, 'run_id': rid, 'reuse_source': source}), encoding='utf-8')
        return True
    return False


def reviewed(rid):
    folder = evo.RUNS / rid
    p = folder / 'inspection.json'
    if not p.exists() or not evo.done(rid):
        return False
    d = json.loads(p.read_text(encoding='utf-8'))
    return (d.get('read_complete') is True and d.get('hard_constraints_ok') is True
            and d.get('output_sha256') == digest(evo.output(rid)))


def record_review(rid, approved, notes):
    """Executor calls only after actually reading output; no extra model review."""
    if not evo.done(rid):
        raise ValueError('cannot review an incomplete run')
    d = {'read_complete': True, 'hard_constraints_ok': approved,
         'output_sha256': digest(evo.output(rid)), 'notes': notes}
    (evo.RUNS / rid / 'inspection.json').write_text(json_text(d), encoding='utf-8')


def load_manifest(path):
    d = json.loads(Path(path).read_text(encoding='utf-8'))
    pipe.token(d['name'], 'batch name')
    tags = [c['tag'] for c in d['candidates']]
    if not tags or len(tags) != len(set(tags)):
        raise ValueError('empty/duplicate candidate tags')
    for c in d['candidates']:
        pipe.token(c['tag'], 'candidate tag')
        spec = pipe.load_spec(ROOT / c['spec'])
        if set(spec['_steps']) != {'A1', 'A2', 'A3', 'A4'} or spec['final'] != 'A4':
            raise ValueError('batch requires the approved four-step interface')
        if any(s['model'] != 'g6' for s in spec['steps']):
            raise ValueError('production model must remain GPT-6')
        if c.get('spec_sha256') and c['spec_sha256'] != spec_hash(spec):
            raise ValueError(f"{c['tag']}: frozen scheme/prompt changed")
    if not 1 <= d.get('workers', 4) <= 10:
        raise ValueError('workers must be 1..10')
    return d


def spec_hash(spec):
    return digest(json_text({'spec': {k: v for k, v in spec.items() if not k.startswith('_')},
                             'prompts': spec['_texts']}))


def generate_work(candidate, w, base, sources):
    spec = pipe.load_spec(ROOT / candidate['spec'])
    builtins, graph = pipe.work_context(w, base)
    outputs = {}
    for sid in ('A1', 'A2', 'A3', 'A4'):
        message = pipe.render_step(spec, sid, builtins, outputs)
        rid = f"sc{candidate['tag']}_{w}_{sid}"
        folder = evo.RUNS / rid
        folder.mkdir(exist_ok=True)
        inp = folder / 'input.txt'
        if inp.exists() and inp.read_text(encoding='utf-8') != message:
            raise ValueError(f'{rid}: existing input differs; use a new tag')
        write_frozen(folder / 'prepared_input.txt', message)
        source_ids = [f'sc{t}_{w}_{sid}' for t in sources]
        reused = reuse_completed(rid, message, spec['_steps'][sid]['model'], source_ids)
        if not evo.done(rid):
            evo.check_submission(V.JUDGES[spec['_steps'][sid]['model']])
        result = pipe.call(rid, message, spec['_steps'][sid]['model'], spec['name'])
        outputs[sid] = result
        if sid == 'A4':
            pipe.save(w, graph, result, spec['note'], candidate['tag'], base)
        # Reused prerequisites have already been inspected in their source run.
        # A new stage must be read before downstream calls; no paid review layer.
        if (folder / 'inspection.json').exists():
            d = json.loads((folder / 'inspection.json').read_text(encoding='utf-8'))
            if d.get('hard_constraints_ok') is False:
                return {'work': w, 'status': 'discard_hard_constraint', 'run_id': rid}
        if not reused and not (folder / 'reuse.json').exists() and not reviewed(rid):
            return {'work': w, 'status': 'read_required', 'run_id': rid}
    return {'work': w, 'status': 'generation_complete'}


def generate(manifest):
    F.configure()
    require_prompt_review(manifest)
    tasks = [(c, w) for c in manifest['candidates'] for w in F.WORKS]
    def one(job):
        c, w = job
        return {'tag': c['tag'], **generate_work(c, w, manifest['base'], manifest.get('source_tags', []))}
    with ThreadPoolExecutor(max_workers=manifest.get('workers', 4)) as pool:
        results = list(pool.map(one, tasks))
    p = ROOT / 'runs' / '_batches' / manifest['name'] / 'generation.json'
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json_text(results), encoding='utf-8')
    return results


def require_prompt_review(manifest):
    p = ROOT / 'runs' / '_batches' / manifest['name'] / 'prompt_review.json'
    expected = {c['tag']: c['spec_sha256'] for c in manifest['candidates']}
    if not p.exists():
        raise ValueError('read generic prompts and four-step compatibility first; use review-prompts')
    d = json.loads(p.read_text(encoding='utf-8'))
    if d.get('approved') is not True or d.get('schemes') != expected:
        raise ValueError('prompt review does not match frozen candidates')


def screen_batch(manifest):
    F.configure()
    for c in manifest['candidates']:
        for w in F.WORKS:
            if not reviewed(f"sc{c['tag']}_{w}_A4"):
                raise ValueError(f"{c['tag']} {w}: read full final output and record bound inspection first")
    base = manifest['base']
    with ThreadPoolExecutor(max_workers=manifest.get('workers', 4)) as pool:
        blind = dict(zip((c['tag'] for c in manifest['candidates']),
                         pool.map(lambda c: F.run_blind(c['tag'], base), manifest['candidates'])))
    results = {}
    survivors = [c for c in manifest['candidates'] if blind[c['tag']]['status'] == 'pass']
    if survivors:
        # Warm only the missing baseline floors, once, after the batch blind gate.
        for kind in ('coverage', 'alone'):
            F.run_floor(base, base, kind)
    # Floors are sequential per survivor: fewer duplicate IDs and resource bursts.
    for c in manifest['candidates']:
        state = blind[c['tag']]
        if state['status'] == 'pass':
            results[c['tag']] = F.screen(c['tag'], base, attempt=c.get('attempt', 1))
        else:
            results[c['tag']] = F.save_state(c['tag'], base, {
                'status': state['status'], 'blind': state,
                'next': F.feedback_policy(state, attempt=c.get('attempt', 1))})
    p = ROOT / 'runs' / '_batches' / manifest['name'] / 'screen.json'
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json_text(results), encoding='utf-8')
    return results


def prepare_advisors(name, scheme, count=10, base='qurefs', sources=('qu', 'qb')):
    pipe.token(name, 'batch name')
    if count < 3:
        raise ValueError('batch needs at least three candidates')
    spec = pipe.load_spec(scheme)
    rules = (ROOT / '迭代准则.md').read_text(encoding='utf-8')
    limits = rules[rules.index('## 二、迭代范围和硬约束'):rules.index('## 三、流程')]
    materials = {'standard': (ROOT / '标准.md').read_text(encoding='utf-8'), 'hard_constraints': limits,
                 'prompts': spec['_texts'],
                 'products': {w: V.view(V.graph_of(w, base), center=True) for w in F.WORKS},
                 'history': (ROOT / '试验记录.md').read_text(encoding='utf-8'),
                 'user_judgments': (ROOT / '用户判定.md').read_text(encoding='utf-8')}
    # I01 is shared input for the batch, not ten newly purchased candidate reviews.
    materials['existing_open_review_problems'] = {
        p.parent.name: V.parse(p.parent.name) for p in sorted((ROOT / 'runs').glob('eo2_*_qu_*/output.txt'))}
    tasks = []
    for index, judge in enumerate(('g6', 'g56', 'gem')):
        n = count // 3 + int(index < count % 3)
        rid = f'batch_{name}_advisor_{judge}'
        message = (f'请为同一四步写作流程提供{n}套彼此有实质区别的A4完整提示词，只改写线层，复用A1/A2/A3。'
                   '先诊断哪句任务定义影响成品，再分别写假设与完整提示词；不只换词或堆禁令。'
                   '不改标准、分段、珠子、Center、生产模型、High或联网权限。通用生产提示词不得包含眼前作品或情节例子。'
                   '每段2–4条、每条一句，保持原A4占位符、最终JSON接口与四步语义。'
                   '若某个问题确实只能改上游，明确记在analysis，不用伪造A4能修好的方案。'
                   '仅输出JSON：{"analysis":"诊断与不能由A4解决的问题","candidates":'
                   '[{"hypothesis":"独立假设","A4":"完整通用A4提示词"}]}。\n【完整材料】\n' + json_text(materials))
        write_frozen(evo.RUNS / rid / 'prepared_input.txt', message)
        tasks.append({'run_id': rid, 'judge': judge, 'requested': n, 'sha256': digest(message)})
    d = {'name': name, 'base': base, 'scheme': str(Path(scheme).relative_to(ROOT) if Path(scheme).is_absolute() else scheme),
         'count': count, 'source_tags': list(sources), 'workers': 4, 'advisors': tasks,
         'scheme_sha256': spec_hash(spec)}
    path = ROOT / 'runs' / '_batches' / name / 'advisors.json'
    write_frozen(path, json_text(d))
    return path


def run_advisors(d):
    F.configure()
    def one(task):
        rid = task['run_id']
        msg = (evo.RUNS / rid / 'prepared_input.txt').read_text(encoding='utf-8')
        if digest(msg) != task['sha256']:
            raise ValueError('frozen advisor input changed')
        if not evo.done(rid):
            evo.check_submission(V.JUDGES.get(task['judge'], evo.G6))
            if task['judge'] == 'gem':
                result = evo.call_gemini_direct(rid, msg, meta={'stage': 'I02 batch proposals'})
                if not result:
                    reason = (evo.RUNS / rid / 'call_fail_direct.log').read_text(encoding='utf-8')
                    F.mg_schedule.fail(rid, reason)
                    raise RuntimeError(f'{rid}: advisor incomplete')
            else:
                F.submit([(rid, msg, V.JUDGES[task['judge']], 'I02 batch proposals')], 1)
        return rid
    with ThreadPoolExecutor(max_workers=3) as pool:
        return list(pool.map(one, d['advisors']))


def import_advisors(d):
    original = pipe.load_spec(ROOT / d['scheme'])
    if spec_hash(original) != d['scheme_sha256']:
        raise ValueError('source scheme changed after advisor preparation')
    candidates, bodies = [], set()
    for task in d['advisors']:
        answer = V.parse(task['run_id'])
        if (not answer or not isinstance(answer.get('candidates'), list)
                or len(answer['candidates']) > task['requested']):
            raise ValueError(f"{task['run_id']}: missing or incomplete candidate batch")
        for item in answer['candidates']:
            body = item['A4']
            required = ('{SECTIONS}', '{CENTER}', '{ROUTES}', '{TARGETS}')
            if not all(t in body for t in required) or digest(body) in bodies:
                raise ValueError('missing A4 interface or exact duplicate candidate')
            bodies.add(digest(body))
            tag = f"{d['name']}c{len(candidates)+1:02d}"
            new = {k: copy.deepcopy(v) for k, v in original.items() if not k.startswith('_')}
            new.update(name=tag, note=item['hypothesis'])
            step = next(s for s in new['steps'] if s['id'] == 'A4')
            if any(e['prompt_file'] == step['prompt_file'] for e in new.get('edits', [])):
                raise ValueError('materialize source A4 edits before importing proposals')
            step['prompt_file'] = f'{tag}_A4.txt'
            write_frozen(ROOT / 'schemes' / step['prompt_file'], body)
            path = ROOT / 'schemes' / f'{tag}.json'
            write_frozen(path, json_text(new))
            loaded = pipe.load_spec(path)
            candidates.append({'tag': tag, 'spec': f'schemes/{tag}.json', 'hypothesis': item['hypothesis'],
                               'author_run': task['run_id'], 'attempt': 1, 'spec_sha256': spec_hash(loaded)})
    manifest = {k: d[k] for k in ('name', 'base', 'source_tags', 'workers')}
    if not candidates:
        raise ValueError('no usable hypotheses; do not manufacture a batch')
    manifest['candidates'] = candidates
    manifest['prompt_review_required'] = True
    path = ROOT / 'runs' / '_batches' / d['name'] / 'manifest.json'
    write_frozen(path, json_text(manifest))
    return path


def cross(name, upstreams, writers, base, sources, split_upstream=False):
    """Factorial A1/A2/A3 x A4; never splice or edit generated prose."""
    pipe.token(name, 'cross name')
    candidates = []
    pairs = itertools.product(upstreams, repeat=2) if split_upstream else ((p, p) for p in upstreams)
    for up_path, a2_path in pairs:
        up = pipe.load_spec(up_path)
        a2_spec = pipe.load_spec(a2_path)
        for writer_path in writers:
            writer = pipe.load_spec(writer_path)
            new = {k: copy.deepcopy(v) for k, v in up.items() if not k.startswith('_')}
            old_a2 = up['_steps']['A2']['prompt_file']
            new['steps'] = [copy.deepcopy(a2_spec['_steps']['A2']) if s['id'] == 'A2' else s
                            for s in new['steps']]
            new['edits'] = ([e for e in new.get('edits', []) if e['prompt_file'] != old_a2]
                            + [e for e in a2_spec.get('edits', [])
                               if e['prompt_file'] == a2_spec['_steps']['A2']['prompt_file']])
            step = copy.deepcopy(writer['_steps']['A4'])
            if set(up['_steps']) != set(writer['_steps']) or up['final'] != 'A4':
                raise ValueError('cross requires compatible four-step schemes')
            # Changes on A4 travel with writer, changes on A1-A3 with upstream.
            old_a4 = up['_steps']['A4']['prompt_file']
            new['steps'] = [step if s['id'] == 'A4' else s for s in new['steps']]
            new['edits'] = ([e for e in new.get('edits', []) if e['prompt_file'] != old_a4]
                            + [e for e in writer.get('edits', []) if e['prompt_file'] == step['prompt_file']])
            tag = f'{name}c{len(candidates)+1:02d}'
            new.update(name=tag, note=f'cross A1={up_path} A2={a2_path} A4={writer_path}')
            path = ROOT / 'schemes' / f'{tag}.json'
            write_frozen(path, json_text(new))
            loaded = pipe.load_spec(path)
            candidates.append({'tag': tag, 'spec': f'schemes/{tag}.json', 'upstream': str(up_path),
                               'a2_source': str(a2_path), 'writer': str(writer_path),
                               'spec_sha256': spec_hash(loaded), 'attempt': 1})
    manifest = {'name': name, 'base': base, 'source_tags': sources, 'workers': 4,
                'candidates': candidates, 'prompt_review_required': True}
    path = ROOT / 'runs' / '_batches' / name / 'manifest.json'
    write_frozen(path, json_text(manifest))
    return path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    a = sub.add_parser('prepare-advisors')
    a.add_argument('name'); a.add_argument('--scheme', default='schemes/Q15.json')
    a.add_argument('--count', type=int, default=10); a.add_argument('--base', default='qurefs')
    a.add_argument('--sources', nargs='+', default=['qu', 'qb'])
    for command in ('run-advisors', 'import-advisors', 'generate', 'screen'):
        a = sub.add_parser(command); a.add_argument('manifest')
    a = sub.add_parser('review')
    a.add_argument('run_id'); a.add_argument('--reject', action='store_true'); a.add_argument('--notes', required=True)
    a = sub.add_parser('review-prompts')
    a.add_argument('manifest'); a.add_argument('--notes', required=True)
    a = sub.add_parser('cross')
    a.add_argument('name'); a.add_argument('--upstreams', nargs='+', required=True)
    a.add_argument('--writers', nargs='+', required=True); a.add_argument('--base', default='qurefs')
    a.add_argument('--sources', nargs='+', required=True)
    a.add_argument('--split-upstream', action='store_true', help='separately cross A1 and A2 after locating an upstream problem')
    args = p.parse_args()
    if args.command == 'prepare-advisors':
        result = str(prepare_advisors(args.name, args.scheme, args.count, args.base, args.sources))
    elif args.command == 'review':
        record_review(args.run_id, not args.reject, args.notes); result = 'review recorded'
    elif args.command == 'review-prompts':
        d = load_manifest(args.manifest)
        target = ROOT / 'runs' / '_batches' / d['name'] / 'prompt_review.json'
        target.write_text(json_text({'approved': True, 'schemes': {c['tag']: c['spec_sha256'] for c in d['candidates']},
                                    'notes': args.notes}), encoding='utf-8')
        result = 'executor prompt review recorded'
    elif args.command == 'cross':
        result = str(cross(args.name, args.upstreams, args.writers, args.base, args.sources, args.split_upstream))
    elif args.command in ('run-advisors', 'import-advisors'):
        d = json.loads(Path(args.manifest).read_text(encoding='utf-8'))
        result = run_advisors(d) if args.command == 'run-advisors' else str(import_advisors(d))
    else:
        d = load_manifest(args.manifest)
        result = generate(d) if args.command == 'generate' else screen_batch(d)
    print(json_text(result))


if __name__ == '__main__':
    main()
