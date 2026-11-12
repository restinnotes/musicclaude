"""Opt-in screenshots for controlled browser comparisons, before tab cleanup."""
from pathlib import Path
import hashlib
import json
import os
import time


async def capture_probe_evidence(client, stage):
    if not Path('/app/state/capture-probes.enabled').exists():
        return None
    request_id = client._standard_request_id
    directory = Path('/app/state/probe-artifacts') / request_id
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    started = time.time()
    record = {'stage': stage, 'request_id': request_id, 'captured_at': started,
              'source': 'live browser page owned by this standard request', 'files': []}
    try:
        for suffix, full_page in [('viewport', False), ('full', True)]:
            filename = stage + '-' + suffix + '.jpg'
            image = await client.page.screenshot(type='jpeg', quality=85,
                                                  full_page=full_page, timeout=12000)
            path = directory / filename
            path.write_bytes(image)
            os.chmod(path, 0o600)
            record['files'].append({'filename': filename, 'sha256': hashlib.sha256(image).hexdigest()})
        labels = await client.page.get_by_text(__import__('re').compile(r'^(Worked for|Thought for)\s')).all_text_contents()
        record['thinking_time_ui_labels'] = labels
        # ChatGPT uses an inner scroll container: full_page can be identical to
        # the viewport and leave a long final answer below a thought summary.
        # Preserve the initial page images, then record the answer's ending.
        if stage == 'response':
            try:
                message = client.page.locator('[data-message-author-role="assistant"]').last
                await message.evaluate('(el) => el.scrollIntoView({block: "end", behavior: "instant"})')
                await client.page.wait_for_timeout(250)
                image = await client.page.screenshot(type='jpeg', quality=85, timeout=12000)
                filename = 'response-answer.jpg'
                path = directory / filename
                path.write_bytes(image)
                os.chmod(path, 0o600)
                record['files'].append({'filename': filename, 'sha256': hashlib.sha256(image).hexdigest()})
                record['answer_view_capture_success'] = True
            except Exception as error:
                record['answer_view_capture_success'] = False
                record['answer_view_error_class'] = type(error).__name__
        record['success'] = True
    except Exception as error:
        record.update(success=False, error_class=type(error).__name__)
    record['capture_seconds'] = round(time.time() - started, 3)
    path = directory / (stage + '.json')
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    os.chmod(path, 0o600)
    return {'directory': str(directory), **record}
