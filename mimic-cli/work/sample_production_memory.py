"""Small read-only resource/provenance sample for the original yi container."""
from datetime import datetime, timezone
import json
from pathlib import Path
from clone_yi_no_stealth import docker
from runtime_memory_guard import snapshot

record = {'utc':datetime.now(timezone.utc).isoformat(),
    'container':'yi-mimicgate-20261002', 'windows':snapshot(),
    'docker_stats':docker('stats','--no-stream','--format','{{.MemUsage}} {{.CPUPerc}}',
        'yi-mimicgate-20261002').strip(),
    'private_stage_host_exists':Path('work/native-cookie-import.private.json').exists(),
    'private_stage_container_exists':docker('exec','yi-mimicgate-20261002',
        '/opt/venv/bin/python','-c',
        "from pathlib import Path;print(Path('/app/state/native-cookie-import.private.json').exists())").strip() == 'True'}
output = Path('experiments/yi-rootcause/20261006T1625Z/memory/production-resource-samples.jsonl')
with output.open('a',encoding='utf-8') as file:
    file.write(json.dumps(record) + '\n')
print(json.dumps(record))
