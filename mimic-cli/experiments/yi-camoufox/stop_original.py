"""Close the idle original API/browser before the original X display exits."""
from pathlib import Path
from datetime import datetime, timezone
import json
import subprocess
import sys
import time

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parents[1]/'cli'))
import mg
mg.configure_profile('yi')
_, snapshot = mg.http_json('/v1/tabs', mg.read_auth())
assert snapshot['concurrency']['in_flight'] == 0, 'Original has active requests; no shutdown performed'
batch = json.loads((here/'stages-state.json').read_text())['baseline_batch']
assert json.loads((Path(batch)/'state.json').read_text())['status'] == 'complete', 'Baseline is not complete'
container = 'yi-mimicgate-20261002'
def command(args):
    return subprocess.run(args, check=True, capture_output=True, text=True,
                          creationflags=subprocess.CREATE_NO_WINDOW).stdout.strip()
started = datetime.now(timezone.utc).isoformat()
# Cinit caches its respawn policy at startup. Hold the next app respawn in a
# harmless sleep, then restore the exact start script before container shutdown.
# This keeps the original X display alive until the browser has flushed data.
backup = here/'original-startapp.backup'
command(['docker','cp',container+':/startapp.sh',str(backup)])
prepare = """from pathlib import Path
import json,os,signal,time
expected=[b'/opt/venv/bin/python',b'-m',b'src.api.server']
pids=[int(p.parent.name) for p in Path('/proc').glob('[0-9]*/cmdline') if p.read_bytes().split(b'\\0')[:-1]==expected]
assert len(pids)==1, 'Exact API process not found; no signal sent'
p=Path('/startapp.sh')
p.write_text('#!/bin/sh\\nexec sleep 3600\\n')
p.chmod(0o755)
Path('/app/state/export-yi-cookies.enabled').unlink(missing_ok=True)
log=Path('/app/state/yi-session-observer.jsonl')
offset=log.stat().st_size if log.exists() else 0
os.kill(pids[0],signal.SIGTERM)
print(json.dumps({'pid':pids[0],'log_offset':offset}))
"""
details = json.loads(command(['docker','exec',container,'python','-c',prepare]))
closed = False
markers = []
try:
    deadline = time.monotonic()+45
    while time.monotonic()<deadline:
        read = """from pathlib import Path
import json
p=Path('/app/state/yi-session-observer.jsonl')
events=[json.loads(l) for l in p.read_bytes()[OFFSET:].decode().splitlines() if l.strip()]
expected=[b'/opt/venv/bin/python',b'-m',b'src.api.server']
api_present=any(p.read_bytes().split(b'\\0')[:-1]==expected for p in Path('/proc').glob('[0-9]*/cmdline'))
print(json.dumps({'context_closed':any(e['event']=='backend_context_closed' for e in events),'api_exited':not api_present,
 'markers':[{'utc':e['utc'],'event':e['event']} for e in events if e['event']=='backend_context_closed']}))
""".replace('OFFSET',str(details['log_offset']))
        observation = json.loads(command(['docker','exec',container,'python','-c',read]))
        markers = observation['markers']
        if observation['context_closed'] and observation['api_exited']:
            closed = True
            break
        time.sleep(1)
finally:
    command(['docker','cp',str(backup),container+':/startapp.sh'])
    command(['docker','exec',container,'chmod','755','/startapp.sh'])
assert closed, 'Original browser closure not confirmed; no forced stop performed'
command(['docker','stop','-t','45',container])
state = json.loads(command(['docker','inspect',container,'--format','{{json .State}}']))
record = {'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),
          'in_flight_before_shutdown':0,'api_process':details['pid'],
          'browser_close_confirmed':closed,'shutdown_markers':markers,
          'startup_script_restored':True,'api_exit_confirmed':True,'container_status':state['Status'],
          'exit_code':state['ExitCode'],'oom_killed':state['OOMKilled'],
          'profile_and_state_volumes_preserved':True}
(here/'original-shutdown-evidence.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps({k:record[k] for k in ['browser_close_confirmed','container_status','oom_killed']}))
