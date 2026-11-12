import json
from pathlib import Path
root = Path(__file__).resolve().parents[2]
rows = []
for path in (root / 'runs').glob('*/diagnostics.json'):
    try:
        record = json.loads(path.read_text(encoding='utf-8-sig'))
    except (ValueError, OSError):
        continue
    if record.get('profile') == 'shiyan' and record.get('probe') == 'cup':
        rows.append({'run_id': record.get('run_id'), 'timestamp': record.get('timestamp'),
                     'seconds': record.get('elapsed_seconds'), 'effort': record.get('actual_reasoning_effort'),
                     'answer': record.get('probe_assessment', {}).get('observed_answer'),
                     'prompt_sha256': record.get('prompt_sha256'), 'error': (record.get('error') or {}).get('type')})
print(json.dumps(sorted(rows, key=lambda r: r['timestamp'])[-5:], ensure_ascii=False, indent=2))
