"""Switch between existing owned experiment arms after an idle check."""
import argparse
from datetime import datetime, timezone
import json
import sys
import time
from build_mg_storage_pair import OUT, SOURCE, ROOT, docker
import runtime_memory_guard
sys.path.insert(0, str(ROOT / 'cli'))
import mg


def main(condition):
    manifest = json.loads((OUT / 'matched-pair.json').read_text())
    source_before = json.loads(docker('inspect', SOURCE))[0]['State']
    assert not source_before['Running']
    stopped = []
    for arm in manifest['clones'].values():
        state = json.loads(docker('inspect', arm['container']))[0]['State']
        if not state['Running']:
            continue
        mg.CONTAINER = arm['container']; mg.API = arm['api_url']
        concurrency = mg.http_json('/v1/tabs', mg.read_auth())[1]['concurrency']
        assert concurrency['in_flight'] == 0 and concurrency['waiting'] == 0
        docker('stop', '--timeout', '30', arm['container'])
        stopped.append(arm['container'])
    memory = runtime_memory_guard.snapshot()
    record = dict(utc=datetime.now(timezone.utc).isoformat(), stopped=stopped,
                  target=condition, memory_before_start=memory, started=False)
    if condition != 'stop':
        # One capped diagnostic browser, with existing WSL cache; no stress run.
        reason = runtime_memory_guard.headroom_error(memory, 2, 5)
        if reason:
            print(json.dumps(record)); raise RuntimeError(reason)
        target = manifest['clones'][condition]['container']
        config = json.loads(docker('inspect', target))[0]
        assert config['HostConfig']['Memory'] == 1610612736
        assert config['HostConfig']['MemorySwap'] == 1610612736
        docker('start', target)
        record['started'] = True
        mg.CONTAINER = target; mg.API = manifest['clones'][condition]['api_url']
        # Docker start returns before the API listener is ready. Readiness is
        # read-only and must precede any UI setup or model submission.
        deadline = time.monotonic() + 120
        record['api_ready'] = False
        while time.monotonic() < deadline:
            try:
                status, _ = mg.http_json('/healthz')
                if status == 200:
                    record['api_ready'] = True
                    break
            except Exception:
                pass
            time.sleep(2)
    source_after = json.loads(docker('inspect', SOURCE))[0]['State']
    assert not source_after['Running'] and source_after['FinishedAt'] == source_before['FinishedAt']
    record['source_state_unchanged'] = True
    file = OUT / ('transition-' + datetime.now(timezone.utc).strftime('%H%M%S') + '.json')
    file.write_text(json.dumps(record, indent=2), encoding='utf-8')
    print(json.dumps(record))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('condition', choices=['control', 'local_storage', 'native_identity', 'stop'])
    main(parser.parse_args().condition)
