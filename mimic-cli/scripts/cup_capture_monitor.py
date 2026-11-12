"""Archive actual Docker tab screenshots using MimicGate's existing monitor API."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'cli'))
import mg


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    batch = Path(sys.argv[1])
    mg.configure_profile(sys.argv[2] if len(sys.argv) > 2 else 'yi')
    started = batch.stat().st_mtime - 600
    token = mg.read_auth()
    hashes = {}
    seen_runs = set()
    deadline = time.monotonic() + 5400
    while time.monotonic() < deadline:
        state = json.loads((batch / 'state.json').read_text(encoding='utf-8'))
        candidates = [p for p in (ROOT / 'runs').glob('2026*') if p.is_dir() and p.stat().st_mtime >= started]
        pending = [p for p in candidates if not (p / 'diagnostics.json').exists()]
        if pending:
            run = max(pending, key=lambda p: p.name)
            try:
                _, monitor = mg.http_json('/v1/tabs', token, timeout=10)
                tabs = [t for t in monitor['tabs'] if t.get('is_busy') and not t.get('is_control')
                        and t.get('url', '').startswith('https://chatgpt.com/')]
                # Sequential cup batch owns one worker; avoid misattributing other jobs.
                if len(tabs) == 1 and monitor['concurrency']['in_flight'] == 1:
                    tab = tabs[0]
                    request = urllib.request.Request(mg.API + f"/v1/tabs/{tab['index']}/screenshot",
                        headers={'Authorization': 'Bearer ' + token})
                    with urllib.request.urlopen(request, timeout=10) as response:
                        data = response.read()
                        content_type = response.headers.get('Content-Type', '')
                    if content_type.startswith('image/jpeg') and data.startswith(b'\xff\xd8'):
                        digest = hashlib.sha256(data).hexdigest()
                        if hashes.get(run.name) != digest:
                            screenshots = run / 'screenshots'
                            screenshots.mkdir(exist_ok=True)
                            now = datetime.now(timezone.utc)
                            shot = screenshots / (now.strftime('%Y%m%dT%H%M%S.%fZ') + '.jpg')
                            shot.write_bytes(data)
                            (run / 'docker-browser-last-observed.jpg').write_bytes(data)
                            entry = {'retrieved_at_utc': now.isoformat(), 'run_id': run.name,
                                     'tab_index': tab['index'], 'page_url': tab['url'],
                                     'file': str(shot), 'sha256': digest,
                                     'source': 'Docker browser via MimicGate monitor screenshot API',
                                     'cache_max_age_seconds': 4, 'stage': 'live_observation'}
                            with (screenshots / 'index.jsonl').open('a', encoding='utf-8') as handle:
                                handle.write(json.dumps(entry, ensure_ascii=False) + '\n')
                            hashes[run.name] = digest
                            if run.name not in seen_runs:
                                print(json.dumps({'event': 'first_screenshot', 'run_id': run.name, 'file': str(shot)}), flush=True)
                                seen_runs.add(run.name)
            except Exception as error:
                with (batch / 'screenshot-errors.jsonl').open('a', encoding='utf-8') as handle:
                    handle.write(json.dumps({'utc': datetime.now(timezone.utc).isoformat(),
                                             'error_class': type(error).__name__}) + '\n')
        if state['status'] != 'running':
            print(json.dumps({'status': 'complete', 'runs_with_screenshots': sorted(seen_runs)}), flush=True)
            return
        time.sleep(1)


if __name__ == '__main__':
    main()
