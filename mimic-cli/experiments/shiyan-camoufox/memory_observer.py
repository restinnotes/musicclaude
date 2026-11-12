"""Record resource pressure during a known sequential comparison batch."""
from datetime import datetime, timezone
from pathlib import Path
import json
import subprocess
import sys
import time

batch = Path(sys.argv[1])
script = """from pathlib import Path
import json
p=Path('/sys/fs/cgroup')
def fields(name):
    return {line.split()[0]: int(line.split()[1]) for line in (p/name).read_text().splitlines()}
s=fields('memory.stat')
print(json.dumps({'memory_current_mib':round(int((p/'memory.current').read_text())/2**20,2),
 'anon_mib':round(s['anon']/2**20,2),'file_mib':round(s['file']/2**20,2),
 'swap_mib':round(int((p/'memory.swap.current').read_text())/2**20,2),
 'events':fields('memory.events')}))
"""
deadline = time.monotonic() + 5400
while time.monotonic() < deadline:
    state = json.loads((batch/'state.json').read_text())
    proc = subprocess.run(['docker', 'exec', 'shiyan-camoufox-20261006',
                           '/opt/venv/bin/python', '-c', script],
                          capture_output=True, text=True, timeout=15,
                          creationflags=subprocess.CREATE_NO_WINDOW)
    row = {'timestamp_utc':datetime.now(timezone.utc).isoformat(), 'sequence':state.get('current_run'),
           'source':'Docker cgroup v2', 'container':'shiyan-camoufox-20261006'}
    if proc.returncode == 0:
        row.update(json.loads(proc.stdout))
    else:
        row['read_failed'] = True
    with (batch/'memory.jsonl').open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(row) + '\n')
    if state['status'] != 'running':
        break
    time.sleep(30)
