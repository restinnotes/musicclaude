"""Bounded transport recovery of frozen paired candidates; no quality decisions."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import mg_schedule

ROOT = Path(__file__).resolve().parent
FOLDER = ROOT / 'runs/_batches/continue_r80'
GUARD = 'r68a:r67a,r78a:r67a,r78a:r49b,r78a:r54weave,r80a:r78a,r81a:r78a,r81b:r78a,r82a:r78a,r82b:r78a,r83a:r78a,r83b:r78a'
JOBS = [
    ['round65_fix.py', 'restore', tag, 'r84a', '--vs', 'r78a', '--route', 'mimic', '--max', '4']
    for tag in ('r86a', 'r86b')
] + [['continue_r80.py', 'r78a', 'r85a', 'r85b', '--scope-guard', '--semantic-check', '--max', '4', '--guard', GUARD]]


def wait_ordinary():
    while True:
        state = mg_schedule.status()
        if state.get('cooling') and state.get('cooldown_kind') == 'suspicious_behavior':
            raise SystemExit('Explicit protection: stopped all recovery submission.')
        remaining = state.get('cooldown_until', 0) - time.time()
        if remaining <= 0:
            return
        time.sleep(min(remaining, 30))


if __name__ == '__main__':
    env = {**os.environ, 'PYTHONIOENCODING': 'utf-8', 'MG_GLOBAL': '2', 'MG_SLOTS': '2', 'MG_ATTEMPTS': '1'}
    results = []
    for index, args in enumerate(JOBS):
        for attempt in range(1, 4):
            wait_ordinary()
            logpath = FOLDER / f'transport_recovery_{index}_{attempt}.log'
            print('RUN', index, attempt, args[:4], flush=True)
            with logpath.open('w', encoding='utf-8') as log:
                completed = subprocess.run([sys.executable, '-u', *args], cwd=ROOT, env=env,
                                           stdout=log, stderr=subprocess.STDOUT)
            results.append({'args': args, 'attempt': attempt, 'exit_code': completed.returncode, 'log': str(logpath)})
            (FOLDER / 'transport_recovery.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
            print('TERMINAL', index, attempt, completed.returncode, flush=True)
            if completed.returncode == 0:
                break
            state = mg_schedule.status()
            if state.get('cooldown_kind') != 'transient_failure':
                raise SystemExit('Non-transport failure: inspect original log; no automatic retry.')
        else:
            raise SystemExit('Bounded transport retries exhausted; remaining jobs were not submitted.')
