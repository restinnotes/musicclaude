"""One-time debug reclaim of clean WSL page cache, with no service restart."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

out = Path('experiments/yi-rootcause/20261006T1625Z/memory')
out.mkdir(exist_ok=True)
base = ['wsl.exe','--distribution','docker-desktop','--user','root','--']
def run(*arguments, input=None):
    result = subprocess.run(base + list(arguments), input=input, capture_output=True,
        timeout=45, creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:
        raise RuntimeError('WSL memory operation failed: ' + arguments[0])
    return result.stdout.decode('utf-8',errors='replace')
def snapshot():
    keys = {'MemAvailable','Cached','Dirty','AnonPages','Shmem','SwapFree'}
    return {line.split(':')[0]:int(line.split()[1]) for line in run('cat','/proc/meminfo').splitlines()
        if line.split(':')[0] in keys}
before = snapshot()
run('sync')
run('tee','/proc/sys/vm/drop_caches',input=b'1\n')
after = snapshot()
record = {'utc':datetime.now(timezone.utc).isoformat(),'operation':'sync then clean page-cache reclaim',
    'wsl_distro':'docker-desktop','before_kib':before,'after_kib':after,
    'file_or_profile_deleted':False,'service_restarted':False,'persistent_wsl_config_modified':False}
name = sys.argv[1] if len(sys.argv)>1 else 'one-time-clean-cache-reclaim'
assert name.replace('-', '').isalnum()
path = out / (name + '.json')
assert not path.exists(), 'Preserve prior cache-reclaim evidence'
path.write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(record))
