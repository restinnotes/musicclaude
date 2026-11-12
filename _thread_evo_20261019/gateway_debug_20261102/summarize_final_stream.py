"""Summarize only explicitly final content; never print any response strings."""
import copy
import hashlib
import json
import sys
from pathlib import Path


def apply(state, patch):
    path = patch.get('p', '')
    op = patch.get('o')
    value = patch.get('v')
    if not path:
        return copy.deepcopy(value)
    keys = [part.replace('~1', '/').replace('~0', '~') for part in path[1:].split('/')]
    parent = state
    for key in keys[:-1]:
        parent = parent[int(key)] if isinstance(parent, list) else parent[key]
    key = int(keys[-1]) if isinstance(parent, list) else keys[-1]
    if op == 'remove':
        del parent[key]
    elif op == 'append':
        if isinstance(parent[key], dict):
            parent[key].update(copy.deepcopy(value))
        elif isinstance(parent[key], list):
            parent[key].extend(copy.deepcopy(value))
        else:
            parent[key] += value
    else:
        if isinstance(parent, list) and key == len(parent):
            parent.append(copy.deepcopy(value))
        else:
            parent[key] = copy.deepcopy(value)
    return state


def summarize(raw):
    state = {}; finals = []; last_path = ''; last_op = None; errors = 0; done = False
    def save():
        message = state.get('message', {}) if isinstance(state, dict) else {}
        if message.get('author', {}).get('role') != 'assistant' or message.get('channel') != 'final':
            return
        content = message.get('content', {})
        text = ''.join(p for p in content.get('parts', []) if isinstance(p, str))
        metadata = message.get('metadata', {})
        dil = metadata.get('model_dil_v2') or {}
        fallback = dil.get('fallbackMarkdown')
        finals.append({'status': message.get('status'), 'end_turn': message.get('end_turn'),
            'content_type': content.get('content_type'), 'text_characters': len(text),
            'text_sha256': hashlib.sha256(text.encode()).hexdigest(),
            'finish_type': (metadata.get('finish_details') or {}).get('type'),
            'fallback_characters': len(fallback) if isinstance(fallback, str) else None,
            'fallback_equals_text': fallback == text,
            'dil_fields': sorted(dil),
            'recovery_diagnostics': shape(dil.get('recoveryDiagnostics')),
            'component_shapes': shape(metadata.get('genui_components')),
            'json_valid': valid_json(text)})
    for line in raw.decode('utf-8', errors='strict').splitlines():
        if not line.startswith('data:'):
            continue
        data = line[5:].strip()
        if data == '[DONE]':
            done = True; continue
        try:
            row = json.loads(data)
            if not isinstance(row, dict) or 'v' not in row:
                continue
            path = row.get('p', last_path); op = row.get('o', last_op)
            if path == '' and isinstance(row['v'], dict) and 'message' in row['v']:
                save(); state = copy.deepcopy(row['v'])
            elif isinstance(row['v'], list) and (op == 'patch' or all(isinstance(v, dict) and 'p' in v for v in row['v'])):
                for patch in row['v']:
                    state = apply(state, patch)
            else:
                state = apply(state, {'p':path, 'o':op, 'v':row['v']})
            last_path = path; last_op = op
        except (ValueError, KeyError, TypeError, IndexError):
            errors += 1
    save()
    return {'bytes':len(raw), 'done':done, 'parse_or_patch_errors': errors, 'finals': finals}


def shape(value, depth=0):
    if isinstance(value, str):
        return {'characters': len(value), 'sha256': hashlib.sha256(value.encode()).hexdigest()}
    if isinstance(value, dict):
        return {key: shape(child, depth + 1) for key, child in value.items()} if depth < 4 else {'keys': sorted(value)}
    if isinstance(value, list):
        return [shape(child, depth + 1) for child in value[:12]]
    return value


def valid_json(text):
    try:
        json.loads(text)
        return True
    except ValueError:
        return False


if __name__ == '__main__':
    source = Path(sys.argv[1])
    summary = summarize(source.read_bytes())
    source.with_name('final_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))
