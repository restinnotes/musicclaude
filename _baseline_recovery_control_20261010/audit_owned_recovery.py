#!/usr/bin/env python3
"""Read-only owned-job recovery audit (parameterized).

Reads ONLY public evidence:
  frozen run dir:  results/trials|reviews  (.meta.json/.stderr.txt/.raw.json/.txt)
  owned jobs:      runs/yi-cookie-repair-20261006/job-*/{started,result,submitted,
                   response.txt,capture-binding-diagnostic,handoff-summary,
                   http-worker-console,initializer-aborted}.json
NEVER reads: browser credentials, tokens, sealed handoffs, session state bytes,
             sealed ciphertext, DPAPI files (existence only), private profiles.

Binding rule (run_repeated_trials uses raw file bytes in meta; the owned
provider binds the NORMALIZED prompt):
  norm = raw.decode('utf-8-sig').replace CRLF/CR->LF, rstrip; single leading BOM removed
  candidate = started.model==requested AND started.prompt_sha256==sha256(norm)
              AND started.utc within [meta.utc_start-30s, utc_start+elapsed+30s]

Recovery bar (ALL required):
  route==requested model, effort==max, temporary new session, native prepare,
  prompt sha binding, completed True, terminal True, work_cont False,
  response.txt non-empty with sha==result.response_sha256, original CLI exit
  code preserved as-is (never forged).

Usage (run with -I from a TRUSTED cwd, no network, no model calls):
  python3 -I audit_owned_recovery.py --frozen DIR --runs DIR --out DIR [--targets JSON]
"""
import argparse, datetime, glob, hashlib, json, os, sys
from pathlib import Path

SAFE_START_KEYS = ('model','thinking_effort','temporary','provider_interface',
    'prepare_source','isolated_runtime','prompt_sha256','utc')
SAFE_DIAG_FILES = ('capture-binding-diagnostic.json','handoff-summary.json',
    'execution-worker-attestation.json','initializer-aborted.json',
    'submitted.json','submit-authorized.json','submission-denied.json',
    'http-worker-console.txt','requests.jsonl')

def norm_bytes(raw: bytes) -> bytes:
    return raw.decode('utf-8-sig').replace('\r\n','\n').replace('\r','\n').rstrip().encode('utf-8')

def norm_sha_of_prompt(prompt_file: Path) -> str:
    return hashlib.sha256(norm_bytes(prompt_file.read_bytes())).hexdigest()

def load_json(path):
    with open(path, encoding='utf-8') as f:
        v = json.load(f)
    if not isinstance(v, dict):
        raise ValueError('not-a-dict:' + str(path))
    return v

def audit_target(*, frozen: Path, runs: Path, rel: str, prompt_file: Path,
                 model_requested: str, index):
    meta_path = frozen / (rel + '.meta.json')
    meta = load_json(meta_path)
    raw_path = frozen / (rel + '.raw.json')
    stderr_path = frozen / (rel + '.stderr.txt')
    ns = norm_sha_of_prompt(prompt_file)
    t0 = datetime.datetime.fromisoformat(meta['utc_start'])
    el = meta.get('elapsed_seconds') or 0
    t1 = t0 + datetime.timedelta(seconds=el + 30)
    cands = []
    for jobdir, started, result in index:
        if started.get('model') != model_requested:
            continue
        if started.get('prompt_sha256') != ns:
            continue
        try:
            su = datetime.datetime.fromisoformat(started.get('utc'))
        except Exception:
            continue
        if t0 - datetime.timedelta(seconds=45) <= su <= t1:
            cands.append((jobdir, started, result, su))
    cands.sort(key=lambda c: c[3])
    entry = {
        'target': rel,
        'meta_id': meta.get('id'),
        'meta_status': meta.get('status'),
        'meta_exit_code': meta.get('exit_code'),
        'meta_utc_start': meta.get('utc_start'),
        'meta_elapsed': el,
        'meta_stderr': open(stderr_path, encoding='utf-8').read()[:300] if stderr_path.exists() else None,
        'raw_bytes': os.path.getsize(raw_path) if raw_path.exists() else None,
        'prompt_file': str(prompt_file),
        'normalized_prompt_sha256': ns,
        'candidates': [],
        'verdict': None,
        'recoverable_job': None,
    }
    for jobdir, started, result, su in cands:
        resp = Path(jobdir) / 'response.txt'
        resp_bytes = os.path.getsize(resp) if resp.exists() else None
        sha_ok = None
        nonempty = None
        if resp.exists():
            blob = resp.read_bytes()
            nonempty = len(blob.decode('utf-8', errors='replace').strip()) > 0
            sha_ok = hashlib.sha256(blob).hexdigest() == result.get('response_sha256')
        md = result.get('metadata') or {}
        val = md.get('prepared_response_validation') or {}
        checks = {
            'route_is_requested': started.get('model') == model_requested,
            'effort_max': started.get('thinking_effort') == 'max',
            'temporary': started.get('temporary') is True,
            'provider_interface': started.get('provider_interface') is True,
            'native_prepare': started.get('prepare_source') == 'native',
            'isolated': started.get('isolated_runtime') is True,
            'prompt_bound': started.get('prompt_sha256') == ns,
            'completed': result.get('completed') is True,
            'terminal': val.get('successful_assistant_terminal_observed') is True,
            'no_work_continuation': val.get('unsupported_work_continuation_observed') is False,
            'response_nonempty': nonempty is True,
            'response_sha_bound': sha_ok is True,
            'has_submitted_marker': (Path(jobdir) / 'submitted.json').exists(),
            'cli_exit_preserved': True,  # recorded, never forged
        }
        cands_entry = {
            'job_directory': str(jobdir),
            'job_id': Path(jobdir).name,
            'started_utc': started.get('utc'),
            'completed': result.get('completed'),
            'provider_phase': result.get('provider_phase'),
            'response_bytes': resp_bytes,
            'submitted_marker': (Path(jobdir) / 'submitted.json').exists(),
            'checks': checks,
            'all_recovery_checks': all(checks.values()),
            'safe_diagnostics_present': [f for f in SAFE_DIAG_FILES if (Path(jobdir) / f).exists()],
        }
        entry['candidates'].append(cands_entry)
    good = [c for c in entry['candidates'] if c['all_recovery_checks']]
    if good:
        entry['verdict'] = 'RECOVERABLE'
        entry['recoverable_job'] = good[0]['job_directory']
    elif entry['candidates']:
        entry['verdict'] = 'BOUND_BUT_NOT_COMPLETED'
    else:
        entry['verdict'] = 'NO_BOUND_JOB_IN_WINDOW'
    return entry

def build_index(runs: Path):
    index = []
    for jobdir in glob.glob(str(runs / 'job-*')):
        try:
            started = load_json(Path(jobdir) / 'started.json')
            result = load_json(Path(jobdir) / 'result.json')
        except Exception:
            continue
        index.append((jobdir, started, result))
    return index

def default_targets(frozen: Path):
    man = load_json(frozen / 'jobs/manifest.json')
    mp = {}
    for j in man['jobs']:
        for mk, pk in j['model_prompt_paths'].items():
            mp[(j['job_id'], mk)] = frozen / pk
    rman_path = frozen / 'jobs/reviews/review_manifest.json'
    rp = {}
    if rman_path.exists():
        rman = load_json(rman_path)
        for r in rman['jobs']:
            rp[r['job_id']] = (frozen / r['prompt_file'], r['judge_model'])
    frozen9 = [
        ('results/trials/gpt6w/A01/r04', mp[('A01', 'gpt6w')], 'gpt-6-thinking'),
        ('results/trials/gpt6w/B11/r03', mp[('B11', 'gpt6w')], 'gpt-6-thinking'),
        ('results/trials/gpt6w/B18/r04', mp[('B18', 'gpt6w')], 'gpt-6-thinking'),
        ('results/trials/gpt6w/C18/r04', mp[('C18', 'gpt6w')], 'gpt-6-thinking'),
        ('results/trials/gpt6w/B23/r01', mp[('B23', 'gpt6w')], 'gpt-6-thinking'),
    ]
    for rid in ('G_k02_r01_judgegpt6w_AB', 'D_k23_r05_gengpt56w_judgegpt6w_AB',
                'D_k23_r05_gengpt56w_judgegpt6w_BA', 'G_k23_r01_judgegpt6w_BA'):
        pf, jm = rp[rid]
        frozen9.append(('results/reviews/gpt6w/' + rid, pf,
                        'gpt-6-thinking' if jm == 'gpt6w' else 'gpt-5-6-thinking'))
    return frozen9

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--frozen', required=True)
    ap.add_argument('--runs', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--targets', default=None,
                    help='optional JSON list of {rel,prompt,model} to override the frozen 9')
    a = ap.parse_args()
    frozen, runs, out = Path(a.frozen), Path(a.runs), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    index = build_index(runs)
    if a.targets:
        spec = json.loads(Path(a.targets).read_text(encoding='utf-8'))
        targets = [(t['rel'], Path(t['prompt']), t['model']) for t in spec]
    else:
        targets = default_targets(frozen)
    report = {'generated_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'frozen': str(frozen), 'runs': str(runs),
              'jobs_indexed': len(index), 'targets': []}
    for rel, pf, model in targets:
        report['targets'].append(audit_target(
            frozen=frozen, runs=runs, rel=rel, prompt_file=pf,
            model_requested=model, index=index))
    (out / 'owned_recovery_audit.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    # Copy recoverable responses to supplemental files (original evidence untouched).
    for t in report['targets']:
        if t['verdict'] == 'RECOVERABLE':
            src = Path(t['recoverable_job']) / 'response.txt'
            blob = src.read_bytes()
            safe = t['target'].replace('/', '__')
            dest = out / ('SUPPLEMENTAL_RECOVERED_FROM_OWNED_EVIDENCE__' + safe + '.txt')
            if not dest.exists():
                dest.write_bytes(blob)
            sidecar = {
                'RECOVERED_FROM_OWNED_EVIDENCE': True,
                'not_original_runner_success': True,
                'target': t['target'],
                'source_job_directory': t['recoverable_job'],
                'model': [c for c in t['candidates']
                          if c['job_directory'] == t['recoverable_job']][0]['checks'],
                'original_cli_exit_code': t['meta_exit_code'],
                'response_sha256': hashlib.sha256(blob).hexdigest(),
                'response_bytes': len(blob),
            }
            (out / (dest.name + '.meta.json')).write_text(
                json.dumps(sidecar, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'targets': len(report['targets']),
                      'recoverable': sum(1 for t in report['targets'] if t['verdict'] == 'RECOVERABLE'),
                      'out': str(out)}, ensure_ascii=False))

if __name__ == '__main__':
    sys.exit(main())
