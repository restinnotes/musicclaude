"""Sequential cup trials with complete answers, timings and Docker screenshots."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from cup_repeat import summarize


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser()
    parser.add_argument('--profile', required=True)
    parser.add_argument('--container', required=True)
    parser.add_argument('--count', type=int, default=3)
    parser.add_argument('--resume', type=Path)
    args = parser.parse_args()
    batch = args.resume or ROOT / 'runs' / ('cup-' + args.profile + '-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    batch.mkdir(exist_ok=bool(args.resume))
    state = json.loads((batch / 'state.json').read_text(encoding='utf-8')) if args.resume else {
        'profile': args.profile, 'container': args.container, 'planned_runs': args.count,
        'started_utc': datetime.now(timezone.utc).isoformat()}
    state['status'] = 'running'
    state.pop('error', None)
    existing = (batch / 'results.jsonl').read_text(encoding='utf-8').splitlines() if (batch / 'results.jsonl').exists() else []
    print('BATCH ' + str(batch), flush=True)
    for idx in range(len(existing) + 1, args.count + 1):
        state['current_run'] = idx
        (batch / 'state.json').write_text(json.dumps(state, indent=2), encoding='utf-8')
        print(json.dumps({'event': 'started', 'sequence': idx, 'utc': datetime.now(timezone.utc).isoformat()}), flush=True)
        try:
            proc = subprocess.run([sys.executable, str(ROOT / 'cli' / 'mg.py'), '--profile', args.profile, 'probe', 'cup'],
                cwd=ROOT, capture_output=True, text=True, encoding='utf-8', timeout=2400,
                creationflags=subprocess.CREATE_NO_WINDOW)
        except subprocess.TimeoutExpired:
            state.update(status='stopped', error='cli_timeout')
            break
        (batch / f'{idx:02d}-stdout.txt').write_text(proc.stdout, encoding='utf-8')
        (batch / f'{idx:02d}-stderr.txt').write_text(proc.stderr, encoding='utf-8')
        match = re.search(r'^Run:\s*(.+)$', proc.stderr, re.MULTILINE)
        if not match:
            state.update(status='stopped', error='missing_run_path')
            break
        run = Path(match.group(1).strip())
        record = json.loads((run / 'diagnostics.json').read_text(encoding='utf-8'))
        row = summarize(record, run)
        row.update(profile=args.profile, sequence=idx, exit_code=proc.returncode)
        screenshot = record.get('diagnostics', {}).get('screenshot_evidence') or {}
        request_id = row.get('request_id')
        source = screenshot.get('directory')
        expected = '/app/state/probe-artifacts/' + str(request_id)
        if source == expected and re.fullmatch('[0-9a-f]{32}', str(request_id)):
            dest = run / 'screenshots'
            dest.mkdir(exist_ok=True)
            copy = subprocess.run(['docker', 'cp', args.container + ':' + source + '/.', str(dest)],
                capture_output=True, timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
            row['screenshot_copy_success'] = copy.returncode == 0
            row['screenshot_path'] = str(dest / (screenshot.get('stage', 'response') + '-full.jpg'))
            row['capture_stage'] = screenshot.get('stage')
            row['thinking_time_ui_labels'] = screenshot.get('thinking_time_ui_labels', [])
            row['screenshot_capture_seconds'] = screenshot.get('capture_seconds')
        else:
            row['screenshot_copy_success'] = False
        with (batch / 'results.jsonl').open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(row, ensure_ascii=False) + '\n')
        print(json.dumps({'event': 'completed', **row}, ensure_ascii=False), flush=True)
        timed_out_cleanly = (row['error_type'] == 'timeout' and row['actual_effort'] in {'high', 'xhigh'}
                             and record.get('diagnostics', {}).get('generation_stop_verified') is True)
        if not timed_out_cleanly and (not row['transport_success'] or not row['response_complete'] or row['actual_effort'] not in {'high', 'xhigh'}):
            state.update(status='stopped', error=row['error_type'])
            break
        if not row['screenshot_copy_success'] and not timed_out_cleanly:
            state.update(status='stopped', error='screenshot_missing')
            break
        if idx < args.count:
            time.sleep(10)
    else:
        state['status'] = 'complete'
    state['completed_utc'] = datetime.now(timezone.utc).isoformat()
    (batch / 'state.json').write_text(json.dumps(state, indent=2), encoding='utf-8')
    print(json.dumps(state), flush=True)


if __name__ == '__main__':
    main()
