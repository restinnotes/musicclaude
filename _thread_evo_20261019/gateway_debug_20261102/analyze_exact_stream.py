"""Summarize content structure, without exposing reasoning or raw response text."""
import collections
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).parent / 'exact-stream'
raw = (ROOT / 'response.sse').read_bytes()
types = collections.Counter()
paths = collections.Counter()
strings = collections.defaultdict(lambda: {'count': 0, 'characters': 0, 'max': 0})
messages = []
done = False
errors = 0


def walk(value, path='', depth=0):
    if depth > 12:
        return
    if isinstance(value, str):
        record = strings[path]
        record['count'] += 1
        record['characters'] += len(value)
        record['max'] = max(record['max'], len(value))
    elif isinstance(value, dict):
        if 'content_type' in value:
            kind = value['content_type']
            types[kind if kind in {'text','code','dil','thoughts','reasoning_recap'} else 'other'] += 1
        if isinstance(value.get('author'), dict):
            messages.append({'role': value['author'].get('role'), 'channel': value.get('channel'),
                'status': value.get('status'), 'content_keys': list((value.get('content') or {}).keys())})
        for key, child in value.items():
            # Only structural names; arbitrary mapping keys may be private IDs.
            safe = key if key in {'message','content','parts','text','code','data','v','value','metadata',
                'p','o','path','type','channel','status','author','role','content_type','patches','delta',
                'dil','format','language','recipient','name'} else '*'
            walk(child, path + '/' + safe, depth + 1)
    elif isinstance(value, list):
        for child in value:
            walk(child, path + '/[]', depth + 1)


for line in raw.decode('utf-8', errors='replace').splitlines():
    if not line.startswith('data:'):
        continue
    data = line[5:].strip()
    if data == '[DONE]':
        done = True
        continue
    try:
        value = json.loads(data)
    except ValueError:
        errors += 1
        continue
    walk(value)
    if isinstance(value, dict):
        path = value.get('p', value.get('path'))
        if isinstance(path, str) and len(path) < 150:
            paths[path] += 1

summary = {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(), 'sse_done': done,
    'json_parse_errors': errors, 'content_types': dict(types), 'patch_paths': dict(paths),
    'string_shapes': dict(strings), 'messages': messages}
(ROOT / 'structure.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
print(json.dumps(summary, ensure_ascii=False, indent=2))
