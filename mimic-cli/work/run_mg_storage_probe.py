"""One explicit MG-clone probe, with full reply, native screenshots and time.

Never retries a submission. A terminal diagnostics file belongs to the fixed
destination supplied before HTTP, rather than discovery of other callers' runs.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'cli'))
import mg
import runtime_memory_guard as memory_guard
from build_mg_storage_pair import OUT, SOURCE, docker


def container_memory_snapshot(container):
    # Inspect the existing cgroup, without attaching another browser driver.
    code='''import json
from pathlib import Path
p=Path('/sys/fs/cgroup')
events={}
for line in (p/'memory.events').read_text().splitlines():
 k,v=line.split()
 if k in ('low','high','max','oom','oom_kill','oom_group_kill'):events[k]=int(v)
print(json.dumps({'current_bytes':int((p/'memory.current').read_text()),
 'peak_bytes':int((p/'memory.peak').read_text()),'events':events}))
'''
    try:
        return dict(utc=datetime.now(timezone.utc).isoformat(),
                    **json.loads(docker('exec',container,'/opt/venv/bin/python','-c',code)))
    except Exception as error:
        return dict(available=False,error_class=type(error).__name__)


def main(args):
    manifest = json.loads((OUT / 'matched-pair.json').read_text())
    clone = manifest['clones'][args.condition]
    container = clone['container']
    if json.loads(docker('inspect', SOURCE))[0]['State']['Running']:
        raise RuntimeError('Source must remain stopped for this experiment')
    if not json.loads(docker('inspect', container))[0]['State']['Running']:
        raise RuntimeError('Explicit diagnostic container is stopped')
    for key,other in manifest['clones'].items():
        if key != args.condition and json.loads(docker('inspect',other['container']))[0]['State']['Running']:
            raise RuntimeError('Only one matched browser may run at once')
    preparation = json.loads((OUT / ('preparation-' + args.condition + '.json')).read_text())
    if preparation.get('success') is not True:
        raise RuntimeError('Offline preparation did not pass')
    run = OUT / ('cup-' + args.condition + '-' + args.label)
    run.mkdir(exist_ok=False)
    mg.configure_profile('yi')
    mg.API = clone['api_url']
    mg.CONTAINER = container
    prompt = (ROOT / 'prompts/cup.txt').read_text(encoding='utf-8-sig')
    record = dict(run_id=run.name, timestamp=datetime.now(timezone.utc).isoformat(),
        experiment_condition=args.condition, clone=container, api_url=mg.API,
        command='probe', profile='yi', probe='cup', prompt=prompt,
        prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
        requested_model=mg.MODEL, requested_reasoning_effort=mg.EFFORT,
        success=False, response='', http_status=None, diagnostics={}, error=None,
        source_container_modified=False, automatic_resend=False)
    record['requested_native_hint_mode'] = args.native_hints
    record['standard_call_started'] = False
    record['container_memory_before'] = container_memory_snapshot(container)
    (run / 'started.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
    print(json.dumps(dict(preparing_one_standard_probe=True, run=str(run))), flush=True)
    started = time.monotonic()
    memory_guard.OUT = run / 'memory'
    memory_guard.OUT.mkdir(parents=True)
    timeline = memory_guard.ProbeMemoryTimeline(container, minimum_physical_gib=1,
        minimum_commit_gib=3)
    try:
        with timeline:
            if args.native_hints:
                if args.condition != 'native_identity':
                    raise RuntimeError('Native hints require the isolated native identity arm')
                state=mg.http_json('/v1/tabs',mg.read_auth())[1]['concurrency']
                if state['in_flight'] or state['waiting']:
                    raise RuntimeError('Hint comparison clone is busy')
                script=ROOT/'work/mg_native_hint_settings.py'
                docker('cp',str(script),container+':/tmp/mg_native_hint_settings.py')
                hint_setting=json.loads(docker('exec','-w','/app',container,
                    '/opt/venv/bin/python','/tmp/mg_native_hint_settings.py',args.native_hints))
                record['native_hint_experiment']=hint_setting
                if hint_setting.get('mode')!=args.native_hints:
                    raise RuntimeError('Native hint configuration was not verified')
            record['standard_call_started'] = True
            (run / 'started.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
            answer = mg.standard_call(prompt, record)
        record['transport_success'] = True
        record['probe_assessment'] = mg.assess_cup_answer(answer)
        record['success'] = record['probe_assessment']['normal']
    except mg.CLIError as error:
        record['http_status'] = error.status or record['http_status']
        record['error'] = dict(type=error.kind, message=str(error))
        if error.diagnostics:
            record['diagnostics'] = error.diagnostics
    except Exception as error:
        record['error'] = dict(type='probe_failed', exception_class=type(error).__name__,
            message='Probe ended without automatic resend; inspect explicit job evidence')
    finally:
        record['elapsed_seconds'] = round(time.monotonic() - started, 3)
        record['finished_utc'] = datetime.now(timezone.utc).isoformat()
        record['memory'] = timeline.summary()
        record['container_memory_after'] = container_memory_snapshot(container)
        before=record['container_memory_before'].get('events',{})
        after=record['container_memory_after'].get('events',{})
        if 'oom_kill' in before and 'oom_kill' in after:
            record['container_oom_kill_delta'] = after['oom_kill']-before['oom_kill']
            if record['container_oom_kill_delta']>0:
                record['experiment_validity'] = 'memory_interference'
                record['success'] = False
        record['local_screenshot_evidence'] = mg.save_probe_screenshots(record, run)
        if not record['local_screenshot_evidence']['complete']:
            record['success'] = False
        (run / 'prompt.txt').write_text(prompt, encoding='utf-8')
        (run / 'response.txt').write_text(record['response'], encoding='utf-8')
        (run / 'diagnostics.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(dict(terminal=True, run=str(run), assessment=record.get('probe_assessment'),
        elapsed_seconds=record['elapsed_seconds'], error=record['error'],
        screenshot_evidence_complete=record.get('local_screenshot_evidence',{}).get('complete'))), flush=True)
    return 0 if record['success'] else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('condition', choices=['control', 'local_storage','native_identity'])
    parser.add_argument('--label', required=True)
    parser.add_argument('--native-hints',choices=['baseline','high_entropy'])
    args = parser.parse_args()
    if not args.label.isalnum() or len(args.label) > 24:
        parser.error('Probe label must be short alphanumeric')
    raise SystemExit(main(args))
