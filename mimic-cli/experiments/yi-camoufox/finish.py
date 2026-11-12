"""Close the idle candidate browser before its display; retain every volume."""
from datetime import datetime, timezone
from pathlib import Path
import json
import subprocess
import sys
import time

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parents[1]/'cli'))
import mg
mg.configure_profile('yi-camoufox')
_, snapshot = mg.http_json('/v1/tabs', mg.read_auth())
assert snapshot['concurrency']['in_flight'] == 0, 'Candidate has an active request; no shutdown performed'
def command(args):
    return subprocess.run(args, check=True, capture_output=True, text=True,
                          creationflags=subprocess.CREATE_NO_WINDOW).stdout.strip()
container = 'yi-camoufox-20261006'
started = datetime.now(timezone.utc).isoformat()
script = """from pathlib import Path
import os,signal
expected=[b'/opt/venv/bin/python',b'-m',b'src.api.server']
pids=[int(p.parent.name) for p in Path('/proc').glob('[0-9]*/cmdline') if p.read_bytes().split(b'\\0')[:-1]==expected]
assert len(pids)==1, 'Expected candidate API process was not found; no signal sent'
os.kill(pids[0],signal.SIGTERM)
"""
command(['docker','exec',container,'/opt/venv/bin/python','-c',script])
deadline = time.monotonic()+45
while time.monotonic()<deadline:
    state = json.loads(command(['docker','inspect',container,'--format','{{json .State}}']))
    if not state['Running']:
        break
    time.sleep(1)
else:
    raise RuntimeError('Graceful shutdown has not finished; no forced termination performed')
logs = command(['docker','logs',container])
markers = [line for line in logs.splitlines() if any(word in line for word in
           ['Shutting down', 'Browser closed', 'Application shutdown complete'])]
mounts = json.loads(command(['docker','inspect',container,'--format','{{json .Mounts}}']))
record = {'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),
          'in_flight_before_shutdown':0,'browser_close_confirmed':any('Browser closed' in l for l in markers),
          'shutdown_markers':markers,'container_status':state['Status'],
          'exit_code':state['ExitCode'],'oom_killed':state['OOMKilled'],
          'volumes_preserved':[{'name':m.get('Name'),'destination':m['Destination'],'writable':m['RW']} for m in mounts]}
(here/'shutdown-evidence.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps({k:record[k] for k in ['browser_close_confirmed','container_status','exit_code','oom_killed']}))
