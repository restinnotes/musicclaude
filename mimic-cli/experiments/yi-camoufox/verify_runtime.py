from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess

here = Path(__file__).resolve().parent
container = 'yi-camoufox-20261006'
def command(args):
    return subprocess.run(args, check=True, capture_output=True, text=True,
                          creationflags=subprocess.CREATE_NO_WINDOW).stdout.strip()
local = {p.relative_to(here/'src').as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
         for p in (here/'src').rglob('*.py')}
script = "from pathlib import Path; import hashlib,json; p=Path('/app/src'); print(json.dumps({f.relative_to(p).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in p.rglob('*.py')}))"
runtime = json.loads(command(['docker','exec',container,'/opt/venv/bin/python','-c',script]))
mismatches = sorted(set(local)^set(runtime) | {k for k in local if local[k] != runtime.get(k)})
mounts = json.loads(command(['docker','inspect',container,'--format','{{json .Mounts}}']))
record = {'verified_at_utc':datetime.now(timezone.utc).isoformat(), 'container':container,
          'source_files':len(local), 'runtime_source_matches_image_source':not mismatches,
          'mismatches':mismatches, 'source_sha256':local,
          'container_creation_image':command(['docker','inspect',container,'--format','{{.Image}}']),
          'built_image':command(['docker','image','inspect','yi-mimicgate-camoufox:comparison-20261006','--format','{{.Id}}']),
          'runtime_override_before_first_start':['api/probe_evidence.py: extra answer-ending screenshot after completion'],
          'mounts':[{'name':m.get('Name'), 'destination':m['Destination'], 'writable':m['RW']} for m in mounts]}
(here/'runtime-source-manifest.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps({'source_files':len(local),'mismatches':mismatches}))
if mismatches:
    raise SystemExit(1)
