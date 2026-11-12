"""Start Fox only after the baseline browser is idle and safely stopped."""
from pathlib import Path
from datetime import datetime, timezone
import json
import subprocess
import sys
import time
import urllib.request

here=Path(__file__).resolve().parent
root=here.parents[1]
flags=subprocess.CREATE_NO_WINDOW
stage=json.loads((here/'stages-state.json').read_text())
assert json.loads((Path(stage['baseline_batch'])/'state.json').read_text())['status']=='complete'
def command(args):
    return subprocess.run(args,check=True,capture_output=True,text=True,creationflags=flags).stdout.strip()
original=json.loads(command(['docker','inspect','yi-mimicgate-20261002','--format','{{json .State}}']))
assert not original['Running'], 'Original browser still running; candidate not started'
command(['docker','start','yi-camoufox-20261006'])
deadline=time.monotonic()+180
while time.monotonic()<deadline:
    try:
        with urllib.request.urlopen('http://127.0.0.1:8654/healthz',timeout=3) as response:
            if response.status==200:
                break
    except Exception:
        pass
    time.sleep(2)
else:
    raise RuntimeError('Candidate has not become healthy; no formal probe sent')
command([sys.executable,str(here/'verify_runtime.py')])
command(['docker','cp','yi-camoufox-20261006:/app/state/cookie-import-evidence.json',str(here/'cookie-import-evidence.json')])
batch=root/'runs'/('cup-yi-camoufox-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
batch.mkdir()
batch_state={'profile':'yi-camoufox','container':'yi-camoufox-20261006','planned_runs':3,
             'started_utc':datetime.now(timezone.utc).isoformat(),'status':'running'}
(batch/'state.json').write_text(json.dumps(batch_state,indent=2),encoding='utf-8')
stage.update(status='candidate_running',candidate_batch=str(batch),updated_utc=datetime.now(timezone.utc).isoformat())
(here/'stages-state.json').write_text(json.dumps(stage,indent=2),encoding='utf-8')
monitors=[]
for script,args,label in [(root/'scripts'/'cup_capture_monitor.py',[str(batch),'yi-camoufox'],'screenshots'),
    (here/'memory_observer.py',[str(batch),'yi-camoufox-20261006'],'memory')]:
    handle=(batch/(label+'-monitor.log')).open('w',encoding='utf-8')
    monitors.append(subprocess.Popen([sys.executable,str(script),*args],stdout=handle,stderr=subprocess.STDOUT,creationflags=flags))
    handle.close()
proc=subprocess.run([sys.executable,str(root/'scripts'/'cup_comparison.py'),'--profile','yi-camoufox',
    '--container','yi-camoufox-20261006','--count','3','--resume',str(batch)],creationflags=flags)
for monitor in monitors:
    monitor.wait(timeout=45)
finished=json.loads((batch/'state.json').read_text())
stage.update(status='complete' if finished['status']=='complete' else 'candidate_stopped',
             updated_utc=datetime.now(timezone.utc).isoformat())
(here/'stages-state.json').write_text(json.dumps(stage,indent=2),encoding='utf-8')
command([sys.executable,str(here/'auth_summary.py'),'yi-camoufox','yi-camoufox-20261006',str(batch)])
command([sys.executable,str(here/'make_report.py')])
raise SystemExit(proc.returncode)
