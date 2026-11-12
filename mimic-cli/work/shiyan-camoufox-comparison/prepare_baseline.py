from pathlib import Path
root = Path(__file__).resolve().parent
source = (root / 'standard_completion.baseline.py').read_text(encoding='utf-8')
source = source.replace('            response = await client.send_message(',
    "            from src.api.probe_evidence import capture_probe_evidence\n"
    "            await capture_probe_evidence(client, 'prepared')\n"
    '            response = await client.send_message(', 1)
source = source.replace("            diagnostics = dict(client._standard_evidence)\n            diagnostics.update({\"prompt_submitted\": True",
    "            response_completed_at = time.time()\n"
    "            screenshot_evidence = await capture_probe_evidence(client, 'response')\n"
    "            diagnostics = dict(client._standard_evidence)\n"
    "            diagnostics['screenshot_evidence'] = screenshot_evidence\n"
    "            diagnostics.update({\"prompt_submitted\": True", 1)
source = source.replace('"completed_at": time.time(),', '"completed_at": response_completed_at,', 1)
(root / 'standard_completion.observation.py').write_text(source, encoding='utf-8')
# Export cookies before navigation into a private transfer file. Values are never printed.
manager = (root / 'manager.baseline.py').read_text(encoding='utf-8')
needle = '        # Use existing page or create one\n'
addition = """        # User-authorized same-account browser comparison; export before navigation.
        if Path('/app/state/export-shiyan-cookies.enabled').exists():
            import json
            transfer = Path('/app/state/shiyan-transfer')
            transfer.mkdir(parents=True, exist_ok=True, mode=0o700)
            cookie_file = transfer / 'cookies.json'
            cookie_file.write_text(json.dumps(await self._context.cookies()), encoding='utf-8')
            cookie_file.chmod(0o600)

"""
assert needle in manager
manager = manager.replace(needle, addition + needle, 1)
(root / 'manager.observation.py').write_text(manager, encoding='utf-8')
compile(source, 'standard_completion.observation.py', 'exec')
compile(manager, 'manager.observation.py', 'exec')
print('Observation-only patches prepared; original browser and send behavior preserved.')
