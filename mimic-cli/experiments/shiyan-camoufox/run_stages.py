"""Finish current controlled comparison, one browser container at a time."""
from datetime import datetime, timezone
from pathlib import Path
import json
import subprocess
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / 'runs' / 'cup-shiyan-20261006T032801Z'
DIRECTORY = Path(__file__).resolve().parent
FLAGS = subprocess.CREATE_NO_WINDOW


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    state = {'status': 'waiting_baseline', 'baseline_batch': str(BASELINE)}

    def save(**changes):
        state.update(changes)
        state['updated_utc'] = datetime.now(timezone.utc).isoformat()
        (DIRECTORY / 'stages-state.json').write_text(json.dumps(state, indent=2), encoding='utf-8')
        print(json.dumps(state), flush=True)

    save()
    for _ in range(1200):
        baseline = json.loads((BASELINE / 'state.json').read_text(encoding='utf-8-sig'))
        if baseline['status'] != 'running':
            break
        time.sleep(3)
    else:
        save(status='stopped', error='baseline_wait_timeout')
        return
    if baseline['status'] != 'complete':
        save(status='stopped', error='baseline_not_completed')
        return
    rows = [json.loads(line) for line in (BASELINE / 'results.jsonl').read_text(encoding='utf-8').splitlines()]
    if len(rows) != 3 or not all(r['actual_effort'] == 'high' and
        ((r['response_complete'] and r['screenshot_copy_success']) or r['error_type'] == 'timeout') for r in rows):
        save(status='stopped', error='baseline_evidence_incomplete')
        return
    save(status='stopping_chrome', baseline_answers=[r['answer'] for r in rows])
    result = subprocess.run(['docker', 'stop', '--timeout', '45', 'shiyan-mimicgate-20261002'],
        capture_output=True, timeout=60, creationflags=FLAGS)
    if result.returncode:
        save(status='stopped', error='chrome_stop_failed')
        return
    result = subprocess.run(['docker', 'start', 'shiyan-camoufox-20261006'],
        capture_output=True, timeout=30, creationflags=FLAGS)
    if result.returncode:
        save(status='stopped', error='camoufox_start_failed')
        return
    save(status='starting_camoufox')
    for _ in range(90):
        try:
            with urllib.request.urlopen('http://127.0.0.1:8653/healthz', timeout=3) as response:
                if response.status == 200:
                    break
        except Exception:
            pass
        time.sleep(2)
    else:
        save(status='stopped', error='camoufox_health_timeout')
        return
    save(status='testing_camoufox')
    process = subprocess.Popen([sys.executable, str(ROOT / 'scripts' / 'cup_comparison.py'),
        '--profile', 'shiyan-camoufox', '--container', 'shiyan-camoufox-20261006', '--count', '3'],
        cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8',
        creationflags=FLAGS)
    assert process.stdout is not None
    for line in process.stdout:
        with (DIRECTORY / 'candidate-console.jsonl').open('a', encoding='utf-8') as handle:
            handle.write(line)
        if line.startswith('BATCH '):
            save(candidate_batch=line[6:].strip())
        print(line.rstrip(), flush=True)
    process.wait()
    assert process.stderr is not None
    (DIRECTORY / 'candidate-stderr.txt').write_text(process.stderr.read(), encoding='utf-8')
    candidate = json.loads((Path(state['candidate_batch']) / 'state.json').read_text(encoding='utf-8'))
    save(status='complete' if candidate['status'] == 'complete' else 'stopped',
         candidate_status=candidate['status'], candidate_error=candidate.get('error'))


if __name__ == '__main__':
    main()
