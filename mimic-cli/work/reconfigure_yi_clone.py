"""Graceful clone-only deployment; production browser/profile remain stopped."""
import json
from pathlib import Path
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'experiments/yi-rootcause/20261006T1313Z'
sys.path.insert(0, str(ROOT / 'work'))
import finish_yi_rca as finish


def main():
    phase = sys.argv[1]
    target = OUT / phase
    target.mkdir(exist_ok=False)
    finish.OUT = target
    finish.CONTAINER = 'yi-rca-capacity-20261006' if len(sys.argv) > 2 and sys.argv[2] == 'capacity' else 'yi-rca-no-stealth-20261006'
    finish.mg.CONTAINER = finish.CONTAINER
    finish.mg.API = 'http://127.0.0.1:8662'
    finish.main()
    if phase.startswith('stop'):
        return
    for name in ('request_observer.py', 'session_observer.py', 'cookie_capacity.py', 'api/standard_completion.py',
                 'api/probe_evidence.py', 'api/openai_routes.py', 'api/browser_gate.py', 'browser/manager.py', 'chatgpt/client.py'):
        finish.docker('cp', str(ROOT / 'src' / name), finish.CONTAINER + ':/app/src/' + name)
    if phase.startswith('timezone-new-york'):
        baseline = finish.docker('cp', finish.CONTAINER + ':/app/src/browser/manager.py', str(target / 'manager.before.py'))
        source = (target / 'manager.before.py').read_text(encoding='utf-8')
        assert source.count('timezone_id="America/Los_Angeles"') == 1
        modified = source.replace('timezone_id="America/Los_Angeles"', 'timezone_id="America/New_York"')
        file = target / 'manager.diagnostic.py'
        file.write_text(modified, encoding='utf-8')
        finish.docker('cp', str(file), finish.CONTAINER + ':/app/src/browser/manager.py')
    finish.docker('start', finish.CONTAINER)
    print(json.dumps({'phase': phase, 'container': finish.CONTAINER, 'utc': datetime.now(timezone.utc).isoformat()}))


if __name__ == '__main__':
    main()
