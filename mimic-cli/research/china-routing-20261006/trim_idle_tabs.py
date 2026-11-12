"""Release only idle, blank ephemeral mg worker tabs through its lease-protected API."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'cli'))
sys.path.insert(0, str(HERE.parents[1] / 'work'))
import mg
from runtime_memory_guard import snapshot

token = mg.read_auth()
_, inventory = mg.http_json('/v1/tabs', token, timeout=10)
rows = inventory.get('tabs', [])
eligible = sorted((row['index'] for row in rows if row.get('session_key') == 'ephemeral'
    and row.get('is_control') is False and row.get('is_busy') is False
    and row.get('url') == 'about:blank'), reverse=True)
record = {'utc':datetime.now(timezone.utc).isoformat(), 'before_memory':snapshot(),
    'policy':'only idle blank ephemeral workers; API independently rejects control/leased pages',
    'closed':[], 'rejected':[]}
for index in eligible:
    try:
        _, result = mg.http_json('/v1/tabs/' + str(index) + '/close', token, {}, timeout=10)
        record['closed'].append(result)
    except mg.CLIError as error:
        record['rejected'].append({'index':index, 'error_type':error.kind})
record['after_memory'] = snapshot()
with (HERE / 'idle-trim-events.jsonl').open('a', encoding='utf-8') as handle:
    handle.write(json.dumps(record) + '\n')
print(json.dumps(record))
