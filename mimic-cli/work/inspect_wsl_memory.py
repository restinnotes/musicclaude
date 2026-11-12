"""Read memory and WSL metadata through hidden CLI subprocesses."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, 'work')
from clone_yi_no_stealth import docker
out = Path('experiments/yi-rootcause/20261006T1625Z/memory')
out.mkdir(exist_ok=True)
keys = {'MemTotal','MemFree','MemAvailable','Cached','SReclaimable','AnonPages','Shmem','SwapTotal','SwapFree','Dirty','Slab'}
raw = docker('exec','lab-mimicgate','cat','/proc/meminfo')
memory = {line.split(':')[0]:int(line.split()[1]) for line in raw.splitlines() if line.split(':')[0] in keys}
def wsl(*args):
    result = subprocess.run(['wsl.exe',*args],capture_output=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
    output = result.stdout.decode('utf-16-le' if b'\0' in result.stdout else 'utf-8',errors='replace').strip()
    return {'exit_code':result.returncode,'output':output}
record = {'utc':datetime.now(timezone.utc).isoformat(),'linux_memory_kib':memory,
    'wsl_distros':wsl('--list','--quiet'), 'wsl_version':wsl('--version'),
    'running_container_stats':docker('stats','--no-stream','--format','{{.Name}} {{.MemUsage}} {{.CPUPerc}}').splitlines()}
(out / 'after-owned-containers-stopped.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
