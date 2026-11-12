"""Prepare observation-only Yi baseline patches and an isolated Fox copy."""
from pathlib import Path
import shutil

here = Path(__file__).resolve().parent
root = here.parents[1]
work = root/'work'/'yi-camoufox-comparison'
baseline = work/'src-baseline'
reference = here.parent/'shiyan-camoufox'
assert not (here/'src').exists(), 'Prepared source already exists; do not overwrite it'
shutil.copytree(baseline, here/'src')

manager = (baseline/'browser'/'manager.py').read_text(encoding='utf-8')
needle = '        # Use existing page or create one\n'
assert manager.count(needle)==1
addition = """        # Authorized same-account transfer, private and before first navigation.
        if Path('/app/state/export-yi-cookies.enabled').exists():
            import json
            transfer = Path('/app/state/yi-transfer')
            transfer.mkdir(parents=True, exist_ok=True, mode=0o700)
            cookie_file = transfer / 'cookies.json'
            cookie_file.write_text(json.dumps(await self._context.cookies()), encoding='utf-8')
            cookie_file.chmod(0o600)

"""
manager = manager.replace(needle, addition+needle, 1)
(work/'manager.observation.py').write_text(manager,encoding='utf-8')
(here/'src/browser/chromium_manager.py').write_text(manager,encoding='utf-8')
(here/'src/browser/manager.py').write_text('from src.browser.camoufox_manager import BrowserManager\n',encoding='utf-8')

source = (baseline/'api/standard_completion.py').read_text(encoding='utf-8')
assert 'capture_probe_evidence' not in source
source = source.replace('from fastapi.responses import JSONResponse',
                        'from src.api.probe_evidence import capture_probe_evidence\nfrom fastapi.responses import JSONResponse',1)
source = source.replace('            response = await client.send_message(',
                        "            await capture_probe_evidence(client, 'prepared')\n            response = await client.send_message(",1)
source = source.replace('            diagnostics = dict(client._standard_evidence)',
                        "            response_completed_at = time.time()\n            screenshot_evidence = await capture_probe_evidence(client, 'response')\n            diagnostics = dict(client._standard_evidence)\n            diagnostics['screenshot_evidence'] = screenshot_evidence",1)
source = source.replace('"completed_at": time.time(),','"completed_at": response_completed_at,',1)
source = source.replace('            kind = classify_error(exc)\n            from src.session_observer',
                        "            kind = classify_error(exc)\n            screenshot_evidence = await capture_probe_evidence(client, 'failure')\n            from src.session_observer",1)
source = source.replace('            diagnostics = dict(getattr(client, "_standard_evidence", {}))',
                        '            diagnostics = dict(getattr(client, "_standard_evidence", {}))\n            diagnostics["request_id"] = client._standard_request_id\n            diagnostics["screenshot_evidence"] = screenshot_evidence',1)
(work/'standard_completion.observation.py').write_text(source,encoding='utf-8')
(here/'src/api/standard_completion.py').write_text(source,encoding='utf-8')
shutil.copy2(reference/'src/api/probe_evidence.py',here/'src/api/probe_evidence.py')
shutil.copy2(reference/'src/browser/human.py',here/'src/browser/human.py')
fox = (reference/'src/browser/camoufox_manager.py').read_text(encoding='utf-8').replace('shiyan','yi').replace('Shiyan','Yi')
fox = fox.replace('        self._context = await self._camoufox_cm.__aenter__()',
                  '        self._context = await self._camoufox_cm.__aenter__()\n        from src.session_observer import attach_context_audit\n        attach_context_audit(self._context)',1)
(here/'src/browser/camoufox_manager.py').write_text(fox,encoding='utf-8')
for name in ['Dockerfile','.dockerignore','entrypoint.py']:
    shutil.copy2(reference/name,here/name)
entry = (here/'entrypoint.py').read_text(encoding='utf-8').replace('"allow_high_fallback":true','"allow_high_fallback":false')
(here/'entrypoint.py').write_text(entry,encoding='utf-8')
for path in (here/'src').rglob('*.py'):
    compile(path.read_text(encoding='utf-8'),str(path),'exec')
compile(entry,'entrypoint.py','exec')
print('Yi source preserved; prepared cookie export/screenshots and strict Extra High Fox candidate.')
