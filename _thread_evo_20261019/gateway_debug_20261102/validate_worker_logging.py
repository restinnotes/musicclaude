import hashlib
import json
import subprocess
from pathlib import Path

root = Path(__file__).parent
checks = {}
for local, remote in [('client_worker_logging_fixed.py', '/app/src/chatgpt/client.py'),
                      ('standard_completion_worker_logging_fixed.py', '/app/src/api/standard_completion.py')]:
    local_hash = hashlib.sha256((root / local).read_bytes()).hexdigest()
    code = f'from pathlib import Path;import hashlib;print(hashlib.sha256(Path({remote!r}).read_bytes()).hexdigest())'
    remote_hash = subprocess.check_output(['docker', 'exec', 'yi-mimicgate-20261002', 'python', '-c', code], text=True).strip()
    assert local_hash == remote_hash
    checks[remote] = local_hash
data = {'hashes': checks, 'tests': {'worker_logging': 4, 'reader_dom_clipboard_warning': 13,
    'completion_guards': 11, 'schedule': 13},
    'root_cause_of_empty_answer': 'unresolved; upstream 200 plus terminal metadata observed, UI body empty',
    'production_cooldown_seconds': {'ordinary_failure': 60, 'explicit_suspicious_behavior': 1800},
    'actual_retry_remote_id': '8bc3a2b1b043abaf93d5'}
result_path = root / 'worker_logging_actual_result.json'
if result_path.exists():
    result = json.loads(result_path.read_text(encoding='utf-8'))
    body = result['body']
    diagnostics = body['mimicgate_diagnostics']
    answer = body['choices'][0]['message']['content']
    assert result['http_status'] == 200 and diagnostics['response_complete'] is True
    assert diagnostics['model']['model'] == 'gpt-6'
    assert diagnostics['model']['selected_effort'] == 'high'
    assert diagnostics['temporary_chat']['verified'] and diagnostics['non_personalized']['verified']
    assert diagnostics['prompt_content_verified'] and answer.strip()
    data['actual_retry'] = {'http_status': result['http_status'], 'seconds': result['seconds'],
        'characters': len(answer), 'response_complete': True, 'model': 'gpt-6', 'effort': 'high',
        'temporary_verified': True, 'unpersonalized_verified': True, 'prompt_verified': True}
(root / 'worker_logging_validation.json').write_text(json.dumps(data, indent=2), encoding='utf-8')
print('Deployed hashes verified')
