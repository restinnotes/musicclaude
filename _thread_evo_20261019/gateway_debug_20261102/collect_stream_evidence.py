"""Collect only already saved metadata for these exact failed requests."""
import json
from pathlib import Path

hashes = {'3b36588f62ee52c9e0d4533efc76c802b87afd78ba401f13988611542694f7aa',
          'a79109c6d836a50d9838cc08e6531afcf22215f649d427f6f45a2b2e11d335eb'}
rows = []
for line in Path('/app/state/yi-session-observer.jsonl').open():
    try:
        row = json.loads(line)
    except ValueError:
        continue
    if row.get('utc', '') < '2026-11-02T22:49:50':
        continue
    if row.get('event') == 'generation_stream_finished' and row.get('metadata', {}).get('text_sha256') in hashes:
        rows.append(row)
dest = Path('/app/state/gateway-fix-20261102/t3_failure_stream_metadata.json')
dest.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
print('Saved', len(rows), 'exact request stream records')
