"""Opt-in screenshots for controlled browser comparisons, before tab cleanup."""
from pathlib import Path
import asyncio
import hashlib
import json
import os
import re
import time


async def capture_probe_evidence(client, stage):
    if not getattr(client, '_capture_probe_evidence', False) and not Path('/app/state/capture-probes.enabled').exists():
        return None
    request_id = client._standard_request_id
    directory = Path('/app/state/probe-artifacts') / request_id
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    started = time.time()
    record = {'stage': stage, 'request_id': request_id, 'captured_at': started,
              'source': 'live browser page owned by this standard request', 'files': []}
    try:
        labels = await client.page.get_by_text(re.compile(r'^(Worked for|Thought for)\s')).all_text_contents()
        record['thinking_time_ui_labels'] = labels
        if stage == 'response':
            # Keep the original viewport (including the thinking-time label)
            # before separately capturing the completed conclusion.
            image = await client.page.screenshot(type='jpeg', quality=85, full_page=False, timeout=12000)
            path = directory / 'response-viewport.jpg'
            path.write_bytes(image)
            os.chmod(path, 0o600)
            record['files'].append({'filename': path.name, 'sha256': hashlib.sha256(image).hexdigest()})
            record['viewport_captured_before_conclusion_scroll'] = True
            # Long answers use an internal scroll container, so full_page does
            # not necessarily show the conclusion. Scroll only after the
            # response is complete, through this request's existing driver.
            # Preserve a native screenshot rather than reconstructing text.
            record['conclusion_scrolled_into_view'] = False
            scroll_errors = []
            for name, selector in [
                ('assistant_content_search_unit', '[data-content-search-unit-key$=":assistant"]'),
                ('assistant_message_role', '[data-message-author-role="assistant"]'),
            ]:
                try:
                    root = client.page.locator(selector).last
                    if not await root.count():
                        continue
                    conclusion = root.locator('p, .katex-display, li').last
                    if not await conclusion.count():
                        continue
                    await conclusion.scroll_into_view_if_needed(timeout=3000)
                    record['conclusion_scrolled_into_view'] = True
                    record['conclusion_scroll_method'] = name
                    break
                except Exception as error:
                    scroll_errors.append(type(error).__name__)
            if not record['conclusion_scrolled_into_view']:
                try:
                    controls = [client.page.get_by_role('button', name=re.compile(
                        r'^(Scroll to bottom|Jump to bottom|滚动到底部|回到底部)$', re.I)),
                        client.page.locator('[data-testid="scroll-to-bottom-button"]')]
                    for locator in controls:
                        for index in range(await locator.count()):
                            button = locator.nth(index)
                            if await button.is_visible():
                                await button.click(timeout=3000)
                                record['conclusion_scrolled_into_view'] = True
                                record['conclusion_scroll_method'] = 'scroll_to_bottom_button'
                                break
                        if record['conclusion_scrolled_into_view']:
                            break
                except Exception as error:
                    scroll_errors.append(type(error).__name__)
            if not record['conclusion_scrolled_into_view']:
                try:
                    # Virtualized answers may not have mounted the last
                    # paragraph yet. Scroll its actual conversation ancestor.
                    # This runs AFTER completion, in the existing utility world.
                    scrolled = await client.page.evaluate('''() => {
                        const main = document.querySelector('main');
                        if (!main) return false;
                        const roots = main.querySelectorAll('[data-content-search-unit-key$=":assistant"], [data-message-author-role="assistant"], .markdown, .prose');
                        let node = roots.length ? roots[roots.length-1] : main;
                        for (; node; node=node.parentElement) {
                            const y=getComputedStyle(node).overflowY;
                            if (node.scrollHeight>node.clientHeight+50 && /^(auto|scroll|overlay)$/.test(y)) {
                                node.scrollTop=node.scrollHeight;
                                return true;
                            }
                        }
                        return false;
                    }''', isolated_context=True)
                    if scrolled is True:
                        record['conclusion_scrolled_into_view'] = True
                        record['conclusion_scroll_method'] = 'conversation_scroll_container'
                except Exception as error:
                    scroll_errors.append(type(error).__name__)
            if scroll_errors:
                record['conclusion_scroll_error_classes'] = scroll_errors
            if record['conclusion_scrolled_into_view']:
                await asyncio.sleep(.25)
        captures = [('full', True)] if stage == 'response' else [('viewport', False), ('full', True)]
        for suffix, full_page in captures:
            filename = stage + '-' + suffix + '.jpg'
            image = await client.page.screenshot(type='jpeg', quality=85,
                                                  full_page=full_page, timeout=12000)
            path = directory / filename
            path.write_bytes(image)
            os.chmod(path, 0o600)
            record['files'].append({'filename': filename, 'sha256': hashlib.sha256(image).hexdigest()})
        record['success'] = True
    except Exception as error:
        record.update(success=False, error_class=type(error).__name__)
    record['capture_seconds'] = round(time.time() - started, 3)
    path = directory / (stage + '.json')
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    os.chmod(path, 0o600)
    return {'directory': str(directory), **record}
