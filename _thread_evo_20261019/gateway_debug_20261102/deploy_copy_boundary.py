"""Deploy only after admission says idle; preserve production model/guards."""
import hashlib
import json
import subprocess
from pathlib import Path

root = Path(__file__).parent
container = 'yi-mimicgate-20261002'


def run(*args):
    return subprocess.check_output(['docker', *args], encoding='utf-8')


run('exec','-w','/app',container,'python','/app/state/gateway-fix-20261102/check_idle.py')
run('exec',container,'cp','/app/src/chatgpt/detector.py',
    '/app/state/gateway-fix-20261102/detector_before_geometry_boundary.py')
run('cp',str(root / 'detector_copy_boundary_fixed.py'),f'{container}:/app/src/chatgpt/detector.py')
expected = hashlib.sha256((root / 'detector_copy_boundary_fixed.py').read_bytes()).hexdigest()
actual = run('exec',container,'python','-c',
    "from pathlib import Path;import hashlib;print(hashlib.sha256(Path('/app/src/chatgpt/detector.py').read_bytes()).hexdigest())").strip()
assert actual == expected
run('restart',container)
subprocess.run(['python',str(root / 'wait_gateway_ready.py')], check=True)
record = json.loads((root / 'copy_boundary_validation.json').read_text())
record.update(deployed_sha256=actual, deployed_complete=True, gateway_ready=True)
(root / 'copy_boundary_validation.json').write_text(json.dumps(record, indent=2))
print('DEPLOYED_READY',actual,flush=True)
