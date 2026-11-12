"""Back up and install the verified native-browser candidate, stopped only.

Does not start a browser, replace its profile, export auth, or change ports.
The service still needs live verification before calling rollout complete.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'experiments/yi-rootcause/20261007T2135Z'
SOURCE = 'yi-mimicgate-20261002'


def docker(*args):
    result = subprocess.run(['docker', *args], capture_output=True, text=True,
                            timeout=60, creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:
        raise RuntimeError('Docker operation failed; raw stderr is intentionally withheld')
    return result.stdout


def backup(path, file):
    result = subprocess.run(['docker', 'cp', SOURCE + ':' + path, str(file)],
                            capture_output=True, text=True, timeout=30,
                            creationflags=subprocess.CREATE_NO_WINDOW)
    if not result.returncode:
        return {'present': True, 'sha256': hashlib.sha256(file.read_bytes()).hexdigest()}
    if 'Could not find the file ' in result.stderr:
        return {'present': False}
    raise RuntimeError('Backup failed for an unexpected reason; no installation authorized')


def main():
    manifest = json.loads((OUT / 'matched-pair.json').read_text())
    state = json.loads(docker('inspect', SOURCE))[0]
    assert not state['State']['Running']
    assert state['State']['FinishedAt'] == manifest['source_finished_at']
    assert 'MIMICGATE_NATIVE_BROWSER_IDENTITY' not in {v.split('=', 1)[0] for v in state['Config']['Env']}
    for clone in manifest['clones'].values():
        assert not json.loads(docker('inspect', clone['container']))[0]['State']['Running']
    checks = []
    # Reconcile the original ambiguous assessment without changing its raw log.
    import sys
    sys.path.insert(0, str(ROOT / 'cli'))
    import mg
    for label in ('patchrightonly001', 'patchrightonly003'):
        file = OUT / ('cup-native_identity-' + label) / 'diagnostics.json'
        record = json.loads(file.read_text(encoding='utf-8'))
        ui = record['diagnostics']
        assert record['transport_success'] is True and ui['response_complete'] is True
        assert mg.assess_cup_answer(record['response'])['observed_answer'] == 8
        assert ui['temporary_chat']['verified'] and ui['non_personalized']['verified']
        assert ui['model']['selected_effort'] == 'xhigh' and ui['model']['fallback_reason'] is None
        assert record['container_oom_kill_delta'] == 0 and record['local_screenshot_evidence']['complete']
        checks.append({'file': str(file), 'sha256': hashlib.sha256(file.read_bytes()).hexdigest()})
    folder = OUT / ('production-candidate-' + datetime.now(timezone.utc).strftime('%H%M%S'))
    folder.mkdir(exist_ok=False)
    files = {
        '/app/src/browser/identity_policy.py': ROOT / 'src/browser/identity_policy.py',
        '/app/src/browser/environment_evidence.py': ROOT / 'src/browser/environment_evidence.py',
        '/app/src/mg_native_hint_settings.py': ROOT / 'work/mg_native_hint_settings.py',
        '/app/src/browser/stealth.py': ROOT / 'src/browser/stealth.py',
        '/app/src/api/probe_evidence.py': ROOT / 'src/api/probe_evidence.py',
        '/app/src/api/standard_completion.py': ROOT / 'src/api/standard_completion.py',
        '/app/src/request_observer.py': ROOT / 'src/request_observer.py',
    }
    # These configuration files contain only public opt-in policy fields.
    policies = {
        '/app/.env': 'MIMICGATE_NATIVE_BROWSER_IDENTITY=1\n',
        '/app/state/.mg-patchright-only.json': '{"additional_stealth":false}',
        '/app/state/.mg-native-hints.json': '{"mode":"baseline","park_idle_control":true}',
    }
    previous = {}
    for target in [*files, *policies]:
        name = target.strip('/').replace('/', '__')
        previous[target] = backup(target, folder / ('before-' + name))
    # Never overwrite an existing environment file, whose contents may include
    # private settings; this particular source was verified to have no file.
    if previous['/app/.env']['present']:
        raise RuntimeError('Existing environment file requires a preserving merge; nothing installed')
    for index, (target, text) in enumerate(policies.items()):
        local = folder / ('policy-' + str(index))
        local.write_text(text, encoding='utf-8')
        files[target] = local
    installed = {}
    for target, local in files.items():
        docker('cp', str(local), SOURCE + ':' + target)
        readback = folder / ('installed-' + target.strip('/').replace('/', '__'))
        docker('cp', SOURCE + ':' + target, str(readback))
        assert readback.read_bytes() == local.read_bytes()
        installed[target] = hashlib.sha256(readback.read_bytes()).hexdigest()
    after = json.loads(docker('inspect', SOURCE))[0]
    assert not after['State']['Running'] and after['State']['FinishedAt'] == state['State']['FinishedAt']
    assert after['Mounts'] == state['Mounts'] and after['HostConfig'] == state['HostConfig']
    report = {'utc': datetime.now(timezone.utc).isoformat(), 'container': SOURCE,
              'backups': previous, 'installed_sha256': installed,
              'verified_candidate_runs': checks, 'installed_while_stopped': True,
              'production_restored': False, 'live_source_verified': False,
              'auth_or_browser_profile_modified': False, 'ports_or_resource_limits_modified': False,
              'candidate_policy': 'Native browser identity, no additional Stealth injection, no manually supplied high entropy hints',
              'original_container_started': False}
    (folder / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({'folder': str(folder), **report}))


if __name__ == '__main__':
    main()
