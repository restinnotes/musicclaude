from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess

here = Path(__file__).resolve().parent
flags = subprocess.CREATE_NO_WINDOW
local = {p.relative_to(here/'src').as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
         for p in (here/'src').rglob('*.py')}
script = "from pathlib import Path; import hashlib,json; p=Path('/app/src'); print(json.dumps({f.relative_to(p).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in p.rglob('*.py')}))"
def command(args):
    return subprocess.run(args, check=True, capture_output=True, text=True, creationflags=flags).stdout.strip()
runtime = json.loads(command(['docker','exec','shiyan-camoufox-20261006','/opt/venv/bin/python','-c',script]))
mismatches = sorted(k for k in local if local[k] != runtime.get(k))
record = {'verified_at_utc':datetime.now(timezone.utc).isoformat(),
          'container':'shiyan-camoufox-20261006', 'source_files':len(local),
          'runtime_source_matches_rebuilt_image_source':not mismatches,
          'mismatches':mismatches, 'source_sha256':local,
          'container_creation_image':command(['docker','inspect','shiyan-camoufox-20261006','--format','{{.Image}}']),
          'rebuilt_image':command(['docker','image','inspect','shiyan-mimicgate-camoufox:comparison-20261006','--format','{{.Id}}']),
          'note':'Existing candidate container retained its profile; two source fixes were deployed with docker cp and graceful restart, then included in the rebuilt image.'}
(here/'runtime-source-manifest.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps({k:record[k] for k in ['source_files','runtime_source_matches_rebuilt_image_source','mismatches']}))
if mismatches:
    raise SystemExit(1)
