"""Reconcile terminal UI replies with passive wire evidence; never submit."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'experiments/yi-rootcause/20261007T2135Z'
sys.path.insert(0, str(ROOT / 'cli'))
import mg


def main():
    observer_files = sorted(OUT.glob('observer-native_identity-*.json'))
    events = {}
    for file in observer_files:
        for row in json.loads(file.read_text(encoding='utf-8')):
            if row.get('event') not in ('generation_wire_request', 'generation_wire_cookie_metadata', 'generation_stream_finished'):
                continue
            key = (row.get('event'), row.get('cdp_request_id'), row.get('wire_epoch'))
            events[key] = (row, file)
    runs = []
    for label in ('hintsbaseline005', 'hintshigh002', 'hintshigh003', 'hintsrollback006',
                  'patchrightonly001', 'patchrightonly002', 'patchrightonly003'):
        folder = OUT / ('cup-native_identity-' + label)
        file = folder / 'diagnostics.json'
        if not file.is_file():
            continue
        data = json.loads(file.read_text(encoding='utf-8'))
        ui = data.get('diagnostics', {})
        submitted = ui.get('submitted_at')
        matching = [(row, source) for row, source in events.values()
                    if submitted is not None and row.get('wire_epoch') is not None
                    and abs(row['wire_epoch'] - submitted) < 5]
        wires = [(row, source) for row, source in matching if row['event'] == 'generation_wire_request']
        cookies = [row for row, source in matching if row['event'] == 'generation_wire_cookie_metadata']
        finished = [(row, source) for row, source in matching if row['event'] == 'generation_stream_finished']
        stream = finished[0][0] if len(finished) == 1 else {}
        stream_complete = (stream.get('metadata_observation_complete') is True
                           and stream.get('sse_done') is True and stream.get('failed') is False)
        route = [item['server_ste_metadata'] for item in stream.get('metadata_records', [])
                 if 'server_ste_metadata' in item] if stream_complete else []
        response = (folder / 'response.txt').read_text(encoding='utf-8')
        runs.append({
            'label': label, 'standard_call_started': data.get('standard_call_started'),
            'prompt_submitted': ui.get('prompt_submitted', False),
            'transport_success': data.get('transport_success', False),
            'answer_assessment': mg.assess_cup_answer(response),
            'total_seconds': data.get('elapsed_seconds'),
            'ui_thinking_time': data.get('local_screenshot_evidence', {}).get('thinking_time_ui_labels'),
            'response_complete': ui.get('response_complete'),
            'temporary_chat_verified': ui.get('temporary_chat', {}).get('verified'),
            'unpersonalized_verified': ui.get('non_personalized', {}).get('verified'),
            'model': data.get('actual_model'), 'effort': data.get('actual_reasoning_effort'),
            'native_hint_mode': data.get('requested_native_hint_mode'),
            'browser_context_present': wires[0][0].get('metadata', {}).get('browser_context_present') if len(wires) == 1 else None,
            'actual_sent_hint_names': sorted({name for row in cookies for name in row.get('header_names', []) if name.startswith('sec-ch-ua')}),
            'stream_metadata_complete': stream_complete, 'observed_server_route': route,
            'oom_kill_delta': data.get('container_oom_kill_delta'),
            'diagnostic_file': str(file), 'diagnostic_sha256': hashlib.sha256(file.read_bytes()).hexdigest(),
            'response_sha256': hashlib.sha256((folder / 'response.txt').read_bytes()).hexdigest(),
            'screenshots_complete': data.get('local_screenshot_evidence', {}).get('complete', False),
            'observer_sources': sorted({str(source) for row, source in matching}),
        })
    result = {'utc': datetime.now(timezone.utc).isoformat(), 'runs': runs,
              'production_restored': False, 'stable_browser_treatment_verified': False,
              'note': 'Answer recognition is separate from an independently checked proof. A preflight rejection is not a model answer. Server route correlation does not establish a browser fingerprint cause.'}
    file = OUT / 'browser-treatment-verification-summary.json'
    file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'file': str(file), 'sha256': hashlib.sha256(file.read_bytes()).hexdigest(),
                      'runs': [{key: row[key] for key in ('label', 'answer_assessment', 'prompt_submitted', 'total_seconds', 'browser_context_present', 'actual_sent_hint_names', 'stream_metadata_complete', 'observed_server_route')}
                               for row in runs]}, ensure_ascii=False))


if __name__ == '__main__':
    main()
