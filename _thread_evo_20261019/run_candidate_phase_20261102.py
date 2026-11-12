"""Run one reviewed phase for both works, then return control for reading outputs."""
import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import evo
import mg_schedule
import pipe


def main():
    p = argparse.ArgumentParser()
    p.add_argument('spec')
    p.add_argument('tag')
    p.add_argument('phase', choices=('A1', 'A2', 'A4'))
    p.add_argument('--work', choices=('op60', 'op61'), help='Continue one reviewed work while the other is still running')
    args = p.parse_args()
    pipe.token(args.tag, 'tag')
    mg_schedule.check()
    spec = pipe.load_spec(args.spec)
    works = (args.work,) if args.work else ('op60', 'op61')
    contexts = {w: pipe.work_context(w, 'qu') for w in works}
    jobs = []
    for w, (builtins, graph) in contexts.items():
        outputs = {}
        for sid in spec['_deps'][args.phase]:
            rid = f'sc{args.tag}_{w}_{sid}'
            assert evo.done(rid), f'Missing reviewed prerequisite {rid}'
            outputs[sid] = pipe.call(rid, '', spec['_steps'][sid]['model'], spec['name'])
        message = pipe.render_step(spec, args.phase, builtins, outputs)
        assert message.strip()
        rid = f'sc{args.tag}_{w}_{args.phase}'
        folder = evo.RUNS / rid
        folder.mkdir(exist_ok=True)
        frozen = folder / 'prepared_input.txt'
        if frozen.exists():
            assert frozen.read_text(encoding='utf-8') == message, 'Input changed for existing run'
        else:
            frozen.write_text(message, encoding='utf-8')
        jobs.append((w, rid, message, graph))
        print('READY', rid, 'prompt_count=1', 'characters=', len(message), flush=True)

    def run(job):
        w, rid, message, graph = job
        result = pipe.call(rid, message, spec['_steps'][args.phase]['model'], spec['name'])
        (evo.RUNS / rid / 'parsed.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        if args.phase == spec['final']:
            pipe.save(w, graph, result, spec['note'], args.tag, 'qu')
        return rid

    errors = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {pool.submit(run, job): job[1] for job in jobs}
        for future in as_completed(futures):
            try:
                print('PHASE_COMPLETE_READ_REQUIRED', future.result(), flush=True)
            except Exception as e:
                errors.append((futures[future], repr(e)))
    if errors:
        raise SystemExit(str(errors))


if __name__ == '__main__':
    main()
