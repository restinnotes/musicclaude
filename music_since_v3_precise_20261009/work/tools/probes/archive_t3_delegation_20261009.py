"""Archive exact T3 task/result from the local transcript, without backend handles.

Only caller-selected public task text and terminal summary are persisted. The
transcript is read as JSON data under Python -I; no code from it is executed.
"""
import argparse
import hashlib
import json
from pathlib import Path


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def tool_json(content):
    value = json.loads(content) if isinstance(content, str) else content
    if isinstance(value, list):
        texts = [part['text'] for part in value if isinstance(part, dict) and part.get('type') == 'text']
        if len(texts) != 1:
            raise ValueError('ambiguous tool text parts')
        return json.loads(texts[0])
    if isinstance(value, dict):
        return value
    raise ValueError('unknown tool result shape')


def archive(transcript, client_id, destination):
    calls, result_rows = {}, []
    for line in Path(transcript).open(encoding='utf-8'):
        row = json.loads(line)
        parts = row.get('message', {}).get('content', [])
        if not isinstance(parts, list):
            continue
        for part in parts:
            if not isinstance(part, dict):
                continue
            if part.get('type') == 'tool_use':
                args = part.get('input', {})
                if part.get('name', '').endswith('delegate_task') and args.get('clientRequestId') == client_id:
                    calls[part['id']] = {'args': args, 'timestamp': row.get('timestamp')}
                elif part.get('name', '').endswith('task_status') and str(args.get('taskId', '')).endswith(client_id):
                    calls[part['id']] = {'status_query': True, 'timestamp': row.get('timestamp')}
            elif part.get('type') == 'tool_result':
                tool_id = part.get('tool_use_id')
                if tool_id not in calls:
                    continue
                value = tool_json(part.get('content'))
                if value.get('status') == 'completed' and isinstance(value.get('summary'), str):
                    result_rows.append((value, row.get('timestamp')))
    submissions = [call for call in calls.values() if 'args' in call]
    if len(submissions) != 1 or not result_rows:
        raise ValueError('require exactly one submitted task and a terminal result')
    if len({sha(value['summary'].encode()) for value, _ in result_rows}) != 1:
        raise ValueError('conflicting terminal results')
    submitted = submissions[0]
    result, completed = result_rows[-1]
    dest = Path(destination)
    dest.mkdir(parents=True, exist_ok=False)
    task = submitted['args']['task']
    response = result['summary']
    for name, text in (('task.txt', task), ('response.txt', response)):
        with (dest / name).open('xb') as stream:
            stream.write(text.encode('utf-8'))
    metadata = {'schema': 't3-public-delegation-archive/1', 'client_request_id': client_id,
                'submitted_at': submitted['timestamp'], 'terminal_observed_at': completed,
                'requested_target': submitted['args'].get('target'),
                'observed_t3_provider': result.get('providerInstanceId'),
                'observed_t3_model': result.get('model'), 'status': result['status'],
                'task_sha256': sha(task.encode()), 'response_sha256': sha(response.encode()),
                'task_utf8_bytes': len(task.encode()), 'response_utf8_bytes': len(response.encode()),
                'evidence_scope': 'exact parent transcript tool payload and terminal result; T3 reported model is not independent remote backend attestation',
                'backend_session_handles': 'not archived', 'production_ready': False}
    with (dest / 'meta.json').open('x', encoding='utf-8') as stream:
        json.dump(metadata, stream, ensure_ascii=False, indent=2)
    print(json.dumps(metadata, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--transcript', required=True)
    parser.add_argument('--client-id', required=True)
    parser.add_argument('--destination', required=True)
    args = parser.parse_args()
    archive(args.transcript, args.client_id, args.destination)


if __name__ == '__main__':
    main()
