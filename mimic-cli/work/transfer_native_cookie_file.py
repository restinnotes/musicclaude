"""Transfer an explicitly prepared native-cookie bundle locally, delete both staging files."""
import json
from pathlib import Path
import sys

sys.path.insert(0,'work')
from clone_yi_no_stealth import docker
container = sys.argv[1]
assert container in ('yi-rca-auth-only-20261006','yi-mimicgate-20261002')
role = 'production' if container == 'yi-mimicgate-20261002' else 'diagnostic'
source = Path('work/native-cookie-import.private.json')
out = Path(sys.argv[2])
assert out.resolve().is_relative_to(Path('experiments/yi-rootcause/20261006T1625Z').resolve())
try:
    docker('cp','work/import_native_cookies_clone.py',container+':/app/import_native_cookies_clone.py')
    docker('cp',str(source),container+':/app/state/native-cookie-import.private.json')
    raw = docker('exec','-w','/app',container,'/opt/venv/bin/python','import_native_cookies_clone.py',role)
    record = json.loads(raw)
    out.write_text(json.dumps(record,indent=2),encoding='utf-8')
    print(json.dumps(record))
finally:
    source.unlink(missing_ok=True)
    docker('exec',container,'/opt/venv/bin/python','-c',
        "from pathlib import Path; Path('/app/state/native-cookie-import.private.json').unlink(missing_ok=True)")
