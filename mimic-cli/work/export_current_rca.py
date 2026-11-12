"""Export an index of preserved trials; retain incomplete evidence as incomplete."""
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'experiments/yi-rootcause/20261006T1313Z'
LATEST = ROOT / 'experiments/yi-rootcause/20261006T1625Z'
sys.path.insert(0, str(ROOT / 'cli'))
import mg

GROUPS = {
    '20261006T131535.725451Z-85410fcf': 'original Docker before capacity fix',
    '20261006T132216.764538Z-a9022518': 'no additional stealth, first trial',
    '20261006T132945.420748Z-c44bca45': 'no additional stealth, auth lost during generation',
    '20261006T135051.867975Z-ff5af4f9': 'API not ready; no generation submitted',
    '20261006T135153.147778Z-c29f01a6': 'capacity fix; original stealth retained',
    '20261006T135722.713531Z-0856725e': 'device aligned; screenshot hook accidentally absent',
    '20261006T140700.653495Z-8cb9f225': 'device aligned; abstained with lower bound 6',
    '20261006T162916.437303Z-c5eccc45': 'original Docker after reboot; capacity guard active; original cookie set',
    '20261006T163417.467388Z-9708255f': 'native cookies + New York; 15-minute timeout; partial x=8 visible, incomplete',
}

def main():
    events = {}
    for file in list(OUT.rglob('*.jsonl')) + list(LATEST.rglob('*.jsonl')):
        for line in file.read_text(encoding='utf-8').splitlines():
            try:
                event = json.loads(line)
                events[json.dumps(event, sort_keys=True)] = event
            except ValueError:
                pass
    wires = [r for r in events.values() if r.get('event') == 'generation_wire_request']
    records = []
    names = set(GROUPS)
    names.update(p.stem.removeprefix('clone-probe-') for p in OUT.glob('clone-probe-*.json'))
    for wrapper in OUT.glob('clone-probe-*.json'):
        information = json.loads(wrapper.read_text(encoding='utf-8'))
        name = wrapper.stem.removeprefix('clone-probe-')
        if name not in GROUPS and name >= '20261006T163400' and information.get('container') == 'yi-rca-capacity-20261006':
            GROUPS[name] = information.get('condition') or 'native non-conversation cookies imported; New York; Chrome 153; 30-minute wait'
        if information.get('container') == 'yi-rca-chrome154-20261006':
            GROUPS[name] = 'official Chrome 154; copied native-cookie/New York diagnostic profile'
        if information.get('container') == 'yi-rca-auth-only-20261006':
            GROUPS[name] = information.get('condition') or 'original production profile copied; native auth cookie only; Chrome 153; Los Angeles'
        if information.get('container') == 'yi-mimicgate-20261002':
            GROUPS[name] = information.get('condition') or 'production validation after native cookie import'
    for name in sorted(names):
        run = ROOT / 'runs' / name
        data = json.loads((run / 'diagnostics.json').read_text(encoding='utf-8'))
        diagnostics = data.get('diagnostics', {})
        submitted = diagnostics.get('submitted_at')
        page_id = diagnostics.get('worker_page_id') or diagnostics.get('model', {}).get('bound_page_object_id')
        candidates = [r for r in wires if r.get('page_object_id') == page_id
            and isinstance(submitted, (float, int)) and abs(r.get('wire_epoch', 0) - submitted) < 10]
        wire = min(candidates, key=lambda r: abs(r['wire_epoch'] - submitted)) if candidates else None
        screenshots = []
        for file in sorted((run / 'screenshots').glob('*')):
            if file.suffix in ('.jpg', '.png'):
                screenshots.append({'path': str(file), 'sha256': hashlib.sha256(file.read_bytes()).hexdigest()})
        assessment = mg.assess_cup_answer(data.get('response', ''))
        records.append({'run_id': name, 'condition': GROUPS.get(name, 'additional diagnostic trial'),
            'run_path': str(run), 'cli_started_utc': data['timestamp'],
            'actual_wire_utc': datetime.fromtimestamp(wire['wire_epoch'], timezone.utc).isoformat() if wire else None,
            'completed_utc': datetime.fromtimestamp(diagnostics['completed_at'], timezone.utc).isoformat()
                if diagnostics.get('completed_at') else None,
            'cli_elapsed_seconds': data.get('elapsed_seconds'),
            'ui_thinking_time': diagnostics.get('screenshot_evidence', {}).get('thinking_time_ui_labels', []),
            'submitted': bool(submitted), 'assessment_current_parser': assessment,
            'response_complete': bool(diagnostics.get('response_complete')),
            'configured_response_timeout_ms': diagnostics.get('response_timeout_ms'),
            'assessment_original_record': data.get('probe_assessment'),
            'wire_request_metadata': wire.get('metadata') if wire else None,
            'screenshots': screenshots, 'screenshot_evidence_complete': len(screenshots) >= 2,
            'error': data.get('error'),
            'partial_answer_observation': 'x=8 visible in failure screenshot; generation was still active; not a pass'
                if name == '20261006T163417.467388Z-9708255f' else None})
    document = {'generated_utc': datetime.now(timezone.utc).isoformat(), 'trials': records,
        'raw_records_preserved': True, 'infrastructure_failures_not_counted_as_model_trials': True}
    (LATEST / 'TRIAL_INDEX.json').write_text(json.dumps(document, ensure_ascii=False, indent=2), encoding='utf-8')
    with (LATEST / 'RESULTS.csv').open('w', encoding='utf-8-sig', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['run_id','condition','actual_wire_utc','completed_utc','ui_thinking_time',
            'observed_answer','assessment_status','submitted','response_complete','screenshots_complete','partial_answer_observation','run_path'])
        for record in records:
            a = record['assessment_current_parser']
            writer.writerow([record['run_id'],record['condition'],record['actual_wire_utc'],record['completed_utc'],
                '; '.join(record['ui_thinking_time']),a['observed_answer'],a['status'],record['submitted'],
                record['response_complete'],record['screenshot_evidence_complete'],record['partial_answer_observation'],record['run_path']])
    print(json.dumps({'trials_indexed': len(records), 'index': str(LATEST / 'TRIAL_INDEX.json')}))

if __name__ == '__main__':
    main()
