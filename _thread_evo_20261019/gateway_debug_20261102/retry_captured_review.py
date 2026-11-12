"""Retry exactly one missing real review after passive capture is ready."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import evo
import mg_call
import mg_schedule

RUN = os.environ.get('CAPTURE_RUN_ID', 'v6b2_op60_g6_r26t3_vsqu')
CAPTURE = os.environ.get('CAPTURE_DIRECTORY', '/app/state/gateway-fix-20261102/failure-exact-1848')


def main():
    os.environ.setdefault('MG_GLOBAL', '1')
    os.environ.setdefault('MG_SLOTS', '1')
    mg_schedule.check()
    assert not evo.done(RUN), 'Review already complete; do not resubmit'
    req = json.loads((evo.RUNS / RUN / 'mg_request.json').read_text(encoding='utf-8'))
    old = json.loads(mg_call.docker('exec', mg_call.CONTAINER, 'cat',
        f"{mg_call.SPOOL}/{req['remote_id']}/result.json"))
    assert old.get('http_status') == 502 and old.get('no_automatic_retry') is True
    # The normal global slot still serializes submission; another authorized
    # task may be finishing on its own worker, so do not restart any service.
    mg_call.docker('cp', str(Path(__file__).with_name('capture_exact_stream.py')),
        f'{mg_call.CONTAINER}:/app/state/gateway-fix-20261102/capture_exact_stream.py')
    mg_call.docker('exec', '-d', '-w', '/app', '-e', f'CAPTURE_DIRECTORY={CAPTURE}',
        '-e', f"CAPTURE_PROMPT_HASH={req['prompt_sha256']}", mg_call.CONTAINER,
        '/opt/venv/bin/python', '/app/state/gateway-fix-20261102/capture_exact_stream.py')
    for _ in range(20):
        ready = mg_call.docker('exec', mg_call.CONTAINER, 'python', '-c',
            f"from pathlib import Path;print(Path('{CAPTURE}/ready.json').exists())").strip()
        if ready == 'True':
            break
        time.sleep(.5)
    else:
        raise RuntimeError('Passive capture not ready; no request submitted')
    print('CAPTURE_READY', req['prompt_sha256'], flush=True)
    result = evo.call(RUN, req['prompt'],
        prompt_text=(evo.RUNS / RUN / 'prompt.txt').read_text(encoding='utf-8'),
        model=evo.G6, meta=json.loads((evo.RUNS / RUN / 'meta.json').read_text(encoding='utf-8')))
    print('REVIEW_COMPLETE' if result else 'REVIEW_FAILED', flush=True)
    local = Path(__file__).with_name(Path(CAPTURE).name)
    local.mkdir(exist_ok=True)
    subprocess.run(['docker', 'cp', f'{mg_call.CONTAINER}:{CAPTURE}/.', str(local)], check=True)


if __name__ == '__main__':
    main()
