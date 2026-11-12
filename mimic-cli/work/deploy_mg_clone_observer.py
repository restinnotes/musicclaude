"""Install the same verified passive observer into stopped diagnostic clones."""
import hashlib
import json
from pathlib import Path
from build_mg_storage_pair import OUT, ROOT, SOURCE, docker

FILES = ['browser/manager.py', 'chatgpt/client.py', 'config.py', 'request_observer.py',
    'session_observer.py', 'cookie_capacity.py', 'api/browser_gate.py',
    'api/standard_completion.py', 'api/probe_evidence.py', 'api/openai_routes.py']
FROZEN_OBSERVER_SHA = '3d96cb537dba7ca3a1bb37c3edccef7fa68a52a8ab131e7ec3fec4b6a164650e'


def main():
    manifest = json.loads((OUT / 'matched-pair.json').read_text())
    observer = ROOT / 'src/request_observer.py'
    if hashlib.sha256(observer.read_bytes()).hexdigest() != FROZEN_OBSERVER_SHA:
        raise RuntimeError('Observer changed after test freeze')
    proofs = {}
    for condition, details in manifest['clones'].items():
        name = details['container']
        state = json.loads(docker('inspect', name))[0]
        if state['State']['Running']:
            raise RuntimeError('Clone already running; refuse a live source edit')
        docker('cp', str(observer), name + ':/app/src/request_observer.py')
        path = OUT / 'code-readback' / condition
        path.mkdir(parents=True, exist_ok=True)
        hashes = {}
        for file in FILES:
            target = path / file
            target.parent.mkdir(parents=True, exist_ok=True)
            docker('cp', name + ':/app/src/' + file, str(target))
            hashes[file] = hashlib.sha256(target.read_bytes()).hexdigest()
        if hashes['request_observer.py'] != FROZEN_OBSERVER_SHA:
            raise RuntimeError('Clone observer readback mismatch')
        proofs[condition] = hashes
    if proofs['control'] != proofs['local_storage']:
        raise RuntimeError('Matched clone code differs')
    source = json.loads(docker('inspect', SOURCE))[0]
    assert not source['State']['Running']
    result = dict(clone_sources_identical=True, hashes=proofs,
        production_source_modified=False, observer_opt_in_both=True,
        source_stopped=True, production_finished_at=source['State']['FinishedAt'])
    (OUT / 'observer-deployment.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(dict(clone_sources_identical=True, file_count=len(FILES), source_stopped=True)))


if __name__ == '__main__':
    main()
