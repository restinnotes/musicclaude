"""Copy only allowlisted passive request metadata, never credentials or prompt contents."""
from collections import deque
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
START = json.loads((HERE / 'manifest.json').read_text(encoding='utf-8'))['created_utc']
CONTAINER = 'yi-mimicgate-20261002'
CODE = '''
from collections import deque
import json
from pathlib import Path
keys = ['utc', 'event', 'request_id', 'text_sha256', 'text_characters', 'model',
    'reasoning_effort', 'thinking_effort', 'status', 'page_object_id', 'session_cookie_count',
    'submitted_at', 'attempted_at', 'minimum_interval_seconds', 'wire_epoch', 'send_attempt_at',
    'previous_attempt_gap_seconds', 'bytes_observed', 'sse_done',
    'error_type', 'exception_class', 'metadata_records', 'response_complete']
events = {'request_auth_preflight', 'submission_attempt', 'generation_wire_request',
    'generation_request_metadata', 'generation_response_started', 'generation_stream_metadata',
    'generation_stream_finished', 'standard_request_failed', 'auth_cookie_loss_observed'}
with Path('/app/state/yi-session-observer.jsonl').open() as f:
    lines = deque(f, maxlen=8000)
out = []
for line in lines:
    try: row = json.loads(line)
    except ValueError: continue
    if row.get('event') in events:
        selected = {key: row[key] for key in keys if key in row}
        if isinstance(row.get('metadata'), dict):
            selected.update({key: row['metadata'][key] for key in keys if key in row['metadata']})
        out.append(selected)
print(json.dumps(out))
'''

result = subprocess.run(['docker', 'exec', CONTAINER, '/opt/venv/bin/python', '-c', CODE],
    capture_output=True, text=True, timeout=20, creationflags=subprocess.CREATE_NO_WINDOW)
if result.returncode:
    raise SystemExit('Passive metadata unavailable; no browser mutation or resend performed')
rows = [row for row in json.loads(result.stdout) if row.get('utc', '') >= START]
hash_jobs = {}
for folder in (HERE / 'jobs').iterdir():
    submitted = folder / 'submitted-prompt.txt'
    prompt = submitted if submitted.exists() else folder / 'prompt.txt'
    content = prompt.read_text(encoding='utf-8-sig')
    hash_jobs[hashlib.sha256(content.encode('utf-8')).hexdigest()] = folder.name
    hash_jobs[hashlib.sha256(content.strip().encode('utf-8')).hexdigest()] = folder.name
for row in rows:
    if row.get('text_sha256') in hash_jobs:
        row['job_id'] = hash_jobs[row['text_sha256']]
snapshot = {'captured_utc': datetime.now(timezone.utc).isoformat(),
    'source': 'existing passive browser observer, allowlisted metadata only', 'events': rows}
(HERE / 'gateway-observations.json').write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding='utf-8')
requests = [row for row in rows if row['event'] == 'generation_wire_request' and row.get('job_id')]
print(json.dumps({'actual_browser_requests': requests,
    'research_failures': [row for row in rows if row['event'] == 'standard_request_failed'],
    'auth_cookie_loss_events': sum(row['event'] == 'auth_cookie_loss_observed' for row in rows)}, ensure_ascii=False))
