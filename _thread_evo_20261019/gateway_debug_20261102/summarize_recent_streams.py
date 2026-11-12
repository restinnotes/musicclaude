import json
from pathlib import Path

rows = []
for line in Path('/app/state/yi-session-observer.jsonl').open():
    try:
        row = json.loads(line)
    except ValueError:
        continue
    if row.get('event') == 'generation_stream_finished' and row.get('utc', '') > '2026-11-02T23:00':
        rows.append(row)
Path('/app/state/gateway-fix-20261102/recent_streams.json').write_text(json.dumps(rows, indent=2))
for row in rows:
    print(json.dumps({key: row.get(key) for key in ('utc','status','bytes_observed','sse_done',
        'oversized_lines_dropped','network_error','wire_duration_seconds')}, ensure_ascii=False))
