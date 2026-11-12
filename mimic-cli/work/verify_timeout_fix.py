from pathlib import Path
import json
import subprocess
import sys
import time
import urllib.request

sys.path.insert(0, 'work')
from clone_yi_no_stealth import docker
CONTAINER = 'yi-rca-capacity-20261006'
OUT = Path('experiments/yi-rootcause/20261006T1625Z/timeout-fix')

docker('cp', 'tests', CONTAINER + ':/app/tests')
command = ['docker', 'exec', '-w', '/app', CONTAINER, '/opt/venv/bin/python', '-m', 'unittest',
    'tests.test_submission_confirmation', 'tests.test_auth_preflight', 'tests.test_standard_contract',
    'tests.test_completion_signal']
result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', timeout=45,
    creationflags=subprocess.CREATE_NO_WINDOW)
(OUT / 'tests.txt').write_text(result.stdout + result.stderr, encoding='utf-8')
print(result.stdout + result.stderr)
assert result.returncode == 0
verification = docker('exec', '-w', '/app', CONTAINER, '/opt/venv/bin/python', '-c',
    "from src.config import Config; import py_compile; py_compile.compile('src/chatgpt/client.py',doraise=True); print(Config.STANDARD_RESPONSE_TIMEOUT)").strip()
assert verification == '1800000'
for _ in range(15):
    try:
        health = json.loads(urllib.request.urlopen('http://127.0.0.1:8662/healthz', timeout=2).read())
        assert health['status'] == 'ok'
        break
    except Exception:
        time.sleep(2)
else:
    raise RuntimeError('Diagnostic container did not become healthy; no probe was submitted')
(OUT / 'validation.json').write_text(json.dumps({'tests_passed': True,
    'standard_response_timeout_ms': int(verification), 'health': health}, indent=2), encoding='utf-8')
print(json.dumps({'timeout_ms': int(verification), 'health': health}))
