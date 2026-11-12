"""Start the original MG after stopped deployment and host-memory checks."""
from datetime import datetime, timezone
import hashlib
import json
import sys
import time
from build_mg_storage_pair import ROOT, OUT, SOURCE, docker
import runtime_memory_guard

sys.path.insert(0, str(ROOT / 'cli'))
import mg


def main():
    deployment = OUT / 'production-candidate-001805/report.json'
    report = json.loads(deployment.read_text())
    assert report['installed_while_stopped'] and not report['auth_or_browser_profile_modified']
    manifest = json.loads((OUT / 'matched-pair.json').read_text())
    for arm in manifest['clones'].values():
        assert not json.loads(docker('inspect', arm['container']))[0]['State']['Running']
    source = json.loads(docker('inspect', SOURCE))[0]
    assert not source['State']['Running']
    assert source['State']['FinishedAt'] == manifest['source_finished_at']
    # Inspect hashes from the stopped source before starting any app process.
    folder = OUT / ('source-start-' + datetime.now(timezone.utc).strftime('%H%M%S'))
    folder.mkdir(exist_ok=False)
    verified = {}
    for path, expected in report['installed_sha256'].items():
        readback = folder / path.strip('/').replace('/', '__')
        docker('cp', SOURCE + ':' + path, str(readback))
        actual = hashlib.sha256(readback.read_bytes()).hexdigest()
        assert actual == expected
        verified[path] = actual
    memory = runtime_memory_guard.snapshot()
    reason = runtime_memory_guard.headroom_error(memory, 2, 5)
    record = {'utc': datetime.now(timezone.utc).isoformat(), 'container': SOURCE,
              'memory_before_start': memory, 'installed_hashes_verified': verified,
              'memory_limits_modified': False, 'profile_or_auth_modified': False,
              'started': False, 'api_ready': False, 'deployment_report': str(deployment)}
    if reason:
        record['preflight_rejection'] = reason
        (folder / 'report.json').write_text(json.dumps(record, indent=2))
        print(json.dumps(record))
        return 1
    docker('start', SOURCE)
    record['started'] = True
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        try:
            if mg.http_json('/healthz')[0] == 200:
                record['api_ready'] = True
                break
        except (mg.CLIError, OSError) as error:
            # A just-started Docker port can accept TCP before its listener is
            # ready. This is a read-only GET; do not restart the live container.
            record['last_readiness_error_class'] = type(error).__name__
        time.sleep(2)
    if record['api_ready']:
        policy = docker('exec', '-w', '/app', SOURCE, '/opt/venv/bin/python', '-c',
            'from src.config import Config;from src.browser.identity_policy import patchright_only_mode;'
            'import os,json;print(json.dumps({"native_identity_loaded":os.environ.get("MIMICGATE_NATIVE_BROWSER_IDENTITY")=="1",'
            '"patchright_only":patchright_only_mode(),"max_concurrency":Config.MAX_CONCURRENT_REQUESTS}))')
        record['live_process_configuration'] = json.loads(policy)
        assert record['live_process_configuration']['native_identity_loaded']
        assert record['live_process_configuration']['patchright_only']
        record['concurrency'] = mg.http_json('/v1/tabs', mg.read_auth())[1]['concurrency']
    record['memory_after_start'] = runtime_memory_guard.snapshot()
    record['finished_utc'] = datetime.now(timezone.utc).isoformat()
    (folder / 'report.json').write_text(json.dumps(record, indent=2))
    print(json.dumps({'folder': str(folder), **record}))
    return 0 if record['api_ready'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
