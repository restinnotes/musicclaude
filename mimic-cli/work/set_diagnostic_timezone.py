"""Change only the copied browser's timezone, after confirmed idle graceful close."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time
import urllib.request

sys.path.insert(0, 'work')
import finish_yi_rca as finish

def main():
    selected = sys.argv[1]
    assert selected in ('America/Los_Angeles', 'America/New_York')
    out = Path('experiments/yi-rootcause/20261006T1625Z') / sys.argv[2]
    assert out.resolve().parent == Path('experiments/yi-rootcause/20261006T1625Z').resolve()
    out.mkdir(exist_ok=False)
    finish.OUT = out
    finish.CONTAINER = 'yi-rca-capacity-20261006'
    finish.mg.CONTAINER = finish.CONTAINER
    finish.mg.API = 'http://127.0.0.1:8662'
    finish.main()
    before = out / 'manager.before.py'
    finish.docker('cp', finish.CONTAINER + ':/app/src/browser/manager.py', str(before))
    text = before.read_text(encoding='utf-8')
    old = 'America/New_York' if selected == 'America/Los_Angeles' else 'America/Los_Angeles'
    marker = 'timezone_id="' + old + '"'
    assert text.count(marker) == 1
    text = text.replace(marker, 'timezone_id="' + selected + '"')
    after = out / 'manager.after.py'
    after.write_text(text, encoding='utf-8')
    finish.docker('cp', str(after), finish.CONTAINER + ':/app/src/browser/manager.py')
    finish.docker('start', finish.CONTAINER)
    for _ in range(20):
        try:
            health = json.loads(urllib.request.urlopen('http://127.0.0.1:8662/healthz', timeout=2).read())
            assert health['status'] == 'ok'
            break
        except Exception:
            time.sleep(2)
    else:
        raise RuntimeError('Diagnostic browser did not become healthy; no probe sent')
    record = {'utc': datetime.now(timezone.utc).isoformat(), 'container': finish.CONTAINER,
        'single_change': 'timezone', 'before': old, 'after': selected,
        'cookie_import_performed':False, 'original_container_modified':False,
        'manager_sha256':hashlib.sha256(after.read_bytes()).hexdigest()}
    (out / 'condition.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    print(json.dumps(record))

if __name__ == '__main__':
    main()
