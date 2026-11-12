"""Snapshot reviewed fixes from the idle, normally stopped original container."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from clone_yi_no_stealth import docker

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'experiments/yi-rootcause/20261006T1625Z'
CONTAINER = 'yi-mimicgate-20261002'
TAG = 'mimicgate-yi-session-guard:20261006'
state = json.loads(docker('inspect','--format','{{json .State}}',CONTAINER))
assert state['Status']=='exited' and state['ExitCode']==0 and not state['OOMKilled']
manifest = OUT / 'fixed-image.json'
old = json.loads(manifest.read_text(encoding='utf-8'))
(OUT / 'fixed-image-before-final.json').write_text(json.dumps(old,indent=2),encoding='utf-8')
image = docker('commit',CONTAINER,TAG).strip()
record = {**old,'image_id':image,'updated_utc':datetime.now(timezone.utc).isoformat(),
    'previous_image_id':old['image_id'],
    'deployment_manifest':'../20261006T1313Z/production-memory-safe-observer-final/deployment.json',
    'request_observer_sha256':hashlib.sha256((ROOT / 'src/request_observer.py').read_bytes()).hexdigest(),
    'native_cookie_values_baked_into_image':False,
    'profile_volumes_baked_into_image':False,'image_pushed':False,
    'container_stopped_during_commit':True}
manifest.write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(record))
