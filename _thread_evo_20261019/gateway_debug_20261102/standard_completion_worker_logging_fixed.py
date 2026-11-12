"""Standard CLI completion inside the existing MimicGate browser service."""
from __future__ import annotations

import asyncio
import copy
import re
import time
import uuid

from fastapi.responses import JSONResponse
from src.config import Config
from src.api.browser_gate import acquire_browser_page, browser_ui_lock, BrowserBusyError, get_concurrency_stats
from src.chatgpt.client import ChatGPTClient
from src.chatgpt.standard_mode import StandardStateError
from src.chatgpt.detector import is_incomplete_response_text, page_has_stop_button
from src.chatgpt.detector import _latest_assistant_turn_snapshot
from src.chatgpt.completion_guard import read_response_error
from src.api.probe_evidence import capture_probe_evidence


def classify_error(exc):
    if isinstance(exc, BrowserBusyError):
        return 'busy'
    if isinstance(exc, StandardStateError):
        return exc.kind
    message = str(exc).lower()
    if "closed" in message or "disconnect" in message or "browser" in message:
        return "browser_disconnected"
    if "model" in message or "effort" in message or "picker" in message or "slider" in message:
        return "model_state"
    if "timeout" in message or isinstance(exc, asyncio.TimeoutError):
        return "timeout"
    if "complete response" in message or "incomplete" in message:
        return "incomplete_response"
    if "input" in message or "selector" in message or "send button" in message:
        return "ui_selector"
    if "submitted" in message:
        return "submission_failed"
    return "browser_automation"


def safe_protocol_error_tags(exc):
    """Finite diagnostic labels only; never persist raw exception messages."""
    text = str(exc).lower()
    patterns = {
        'execution_context_destroyed': 'execution context was destroyed',
        'execution_context_missing': 'cannot find context',
        'object_missing': 'cannot find object',
        'frame_missing': 'no frame with given id',
        'target_closed': 'has been closed',
        'protocol_error': 'protocol error',
        'reference_error': 'referenceerror',
        'type_error': 'typeerror',
        'unexpected_token': 'unexpected token',
        'selector_error': 'selector',
        'page_crashed': 'page crashed',
        'target_navigated_or_closed': 'target navigated or closed',
        'handle_disposed': 'handle is disposed',
        'same_world_required': 'same javascript world',
        'document_unavailable': 'unable to get document',
        'not_an_object': 'was not an object',
        'service_stopped': 'service was stopped',
        'session_closed': 'session closed',
    }
    return [tag for tag, pattern in patterns.items() if pattern in text]


async def execute_standard_completion(request, base_client, *, capture_probe=False, persistent=False):
    try:
        return await _execute_standard_completion(request, base_client, capture_probe=capture_probe, persistent=persistent)
    except Exception as exc:
        # Includes page-lease failures before a client can be bound.
        kind = classify_error(exc)
        return JSONResponse(status_code=429 if kind == 'busy' else 502, content={"error": {
            "type": kind, "message": "MimicGate browser request failed before completion"},
            "mimicgate_diagnostics": {"response_complete": False,
                                      "exception_class": type(exc).__name__}})


async def _execute_standard_completion(request, base_client, *, capture_probe=False, persistent=False):
    if (request.model not in {"gpt-5.6-sol", "gpt-6"} or request.reasoning_effort not in {"high", "xhigh"}
            or request.stream or request.thread_id or request.conversation_id
            or request.tools or request.read_aloud or request.n not in {None, 1}
            or request.reasoning or len(request.messages) != 1
            or request.messages[0].role != "user"
            or not isinstance(request.messages[0].content, str)
            or not request.messages[0].content.strip()):
        return JSONResponse(status_code=400, content={"error": {
            "type": "standard_contract", "message": "Requires one text user prompt, gpt-5.6-sol or gpt-6, high or xhigh, non-streaming one-shot"}})
    if not isinstance(base_client, ChatGPTClient):
        return JSONResponse(status_code=503, content={"error": {
            "type": "provider_state", "message": "The existing ChatGPT browser client is unavailable"}})
    started = time.monotonic()
    # Native-identity diagnostics are single-request experiments. Keep the
    # unused owned control page blank while the normal worker runs, avoiding
    # two loaded app renderers inside the 1.5 GiB cap. No production behavior.
    import os
    if os.environ.get('MIMICGATE_NATIVE_BROWSER_IDENTITY') == '1':
        import json
        from pathlib import Path
        hint_marker=Path('/app/state/.mg-native-hints.json')
        if (hint_marker.is_file() and not hint_marker.is_symlink()
                and hint_marker.stat().st_size <= 128
                and json.loads(hint_marker.read_text()).get('park_idle_control') is True):
            async with browser_ui_lock:
                await base_client.page.goto('about:blank', wait_until='domcontentloaded', timeout=15000)
    # Each one-shot owns a separate worker page in the existing browser profile.
    async with acquire_browser_page() as lease:
        client = copy.copy(base_client.bind_page(lease.page))
        client._music_experiment_mode = True
        client._standard_request_id = uuid.uuid4().hex
        client._capture_probe_evidence = capture_probe
        client._standard_persistent = persistent    # 10-31: X-MimicGate-Mode persistent-standard
        client._standard_ui_lock_held = False
        client._recent_backend_events.clear()
        auth = None
        response = None
        try:
            await browser_ui_lock.acquire()
            client._standard_ui_lock_held = True
            # Isolated native-identity experiment only. The owning driver
            # applies real UAData to this worker, avoiding competing CDP clients.
            import os
            if os.environ.get('MIMICGATE_NATIVE_BROWSER_IDENTITY') == '1':
                from pathlib import Path
                if Path('/app/state/.mg-native-hints.json').is_file():
                    from src.mg_native_hint_settings import apply_to_page
                    client._standard_evidence = {}
                    hint_evidence = await apply_to_page(client.page)
                else:
                    hint_evidence = None
            else:
                hint_evidence = None
            from src.session_observer import emit, request_auth_snapshot
            auth = await request_auth_snapshot(client.page)
            client._standard_evidence = {'authentication': auth}
            if hint_evidence is not None:
                client._standard_evidence['native_hint_experiment'] = hint_evidence
            emit('request_auth_preflight', request_id=client._standard_request_id, **auth)
            if not auth['session_cookie_count']:
                raise StandardStateError('authentication_missing',
                    'ChatGPT session cookie is missing; no prompt was submitted')
            from src.cookie_capacity import ensure_cookie_headroom
            try:
                storage_capacity = await ensure_cookie_headroom(
                    client.page.context, Config.BROWSER_DATA_DIR,
                    allow_prune=get_concurrency_stats().get('in_flight', 1) <= 1)
            except RuntimeError:
                raise StandardStateError('cookie_capacity',
                    'ChatGPT cookie capacity is near its limit; submission was stopped to preserve the session') from None
            await client.prepare_standard_chat(request.model, request.reasoning_effort)
            # Main-world evaluation may enable Runtime in the browser driver.
            # Keep optional fingerprint inspection out of the submission path.
            client._standard_evidence['browser_environment_observation'] = 'skipped_before_submission'
            if hint_evidence is not None:
                client._standard_evidence['native_hint_experiment'] = hint_evidence
            client._standard_evidence['authentication'] = auth
            client._standard_evidence['storage_capacity'] = storage_capacity
            await capture_probe_evidence(client, 'prepared')
            response = await client.send_message(request.messages[0].content,
                                                 model=request.model, reasoning_effort=request.reasoning_effort)
            validation = {'nonempty': bool(response.message),
                          'transient_text': is_incomplete_response_text(response.message),
                          'generation_active': await page_has_stop_button(client.page),
                          'response_characters': len(response.message or '')}
            validation['page_response_error'] = await read_response_error(client.page)
            client._standard_evidence['response_validation'] = validation
            if (not validation['nonempty'] or validation['transient_text'] or validation['generation_active']
                    or validation['page_response_error']['error']):
                raise StandardStateError("incomplete_response", "The browser has not produced a complete final answer")
            response_completed_at = time.time()
            screenshot_evidence = await capture_probe_evidence(client, 'response')
            # A stream error may appear while the last text is being copied or
            # the conclusion is being mounted for the screenshot.
            validation['post_capture_page_response_error'] = await read_response_error(client.page)
            if validation['post_capture_page_response_error']['error']:
                raise StandardStateError('incomplete_response', 'ChatGPT displayed a response error after extraction')
            diagnostics = dict(client._standard_evidence)
            if screenshot_evidence is not None:
                diagnostics['screenshot_evidence'] = screenshot_evidence
            diagnostics.update({"prompt_submitted": True, "response_complete": True,
                                "completion_guard_version": "response-fix-v1",
                                "elapsed_seconds": round(time.monotonic() - started, 3),
                                "thread_id": response.thread_id or None,
                                "conversation_restore": False,
                                "request_id": client._standard_request_id,
                                "worker_page_id": id(client.page),
                                "queue_seconds": round(client._standard_evidence['preparation_started_at'] - (time.time() - (time.monotonic() - started)), 3),
                                "completed_at": response_completed_at,
                                "concurrency": get_concurrency_stats(),
                                "post_response": {"temporary_url_flag": "temporary-chat=true" in client.page.url,
                                                  "state_evidence_stage": "immediately_before_submission",
                                                  "controls_may_disappear_after_send": True}})
            return JSONResponse(content={"id": "chatcmpl-" + uuid.uuid4().hex[:24],
                "object": "chat.completion", "created": int(time.time()), "model": request.model,
                "choices": [{"index": 0, "message": {"role": "assistant", "content": response.message},
                             "finish_reason": "stop"}], "mimicgate_diagnostics": diagnostics})
        except Exception as exc:
            kind = classify_error(exc)
            partial = None
            if getattr(client, '_standard_evidence', {}).get('submitted_at'):
                try:
                    state = await read_response_error(client.page)
                    client._standard_evidence['failure_page_response_error'] = state
                    snapshot = await _latest_assistant_turn_snapshot(client.page)
                    text = response.message if response is not None else snapshot.get('text', '')
                    if isinstance(text, str) and text.strip() and not is_incomplete_response_text(text):
                        partial = {'content': text, 'complete': False,
                                   'characters': len(text), 'source': 'current_request_assistant_turn'}
                except Exception:
                    # Preserve an already extracted answer even if the failed
                    # page can no longer be inspected. Never expose user input.
                    if response is not None and isinstance(response.message, str) and response.message.strip():
                        partial = {'content': response.message, 'complete': False,
                                   'characters': len(response.message), 'source': 'current_request_extracted_response'}
            from src.session_observer import emit
            frames = []
            tb = exc.__traceback__
            while tb is not None:
                code = tb.tb_frame.f_code
                frames.append({'file': code.co_filename.rsplit('/',1)[-1],
                               'function': code.co_name, 'line': tb.tb_lineno})
                tb = tb.tb_next
            emit('standard_request_failed', request_id=client._standard_request_id,
                 error_type=kind, exception_class=type(exc).__name__,
                 fault_locations=frames[-12:],
                 protocol_error_tags=safe_protocol_error_tags(exc),
                 prompt_submitted=bool(getattr(client, '_standard_evidence', {}).get('submitted_at')))
            if not client._standard_ui_lock_held:
                await browser_ui_lock.acquire()
                client._standard_ui_lock_held = True
            screenshot_evidence = await capture_probe_evidence(client, 'failure')
            # Stop only this request's page before the worker returns to the pool.
            client._standard_evidence['cleanup_stop_attempted'] = False
            try:
                if kind == "busy":
                    # This generation predates our request; leave it alone.
                    raise StandardStateError("busy", "Existing generation belongs to another turn")
                stop = await client._visible_control([
                    client.page.get_by_role("button", name=re.compile(
                        r"^(Stop generating|Stop answering|Stop responding|Stop|停止生成|停止回答)$", re.I)),
                    client.page.locator('button[data-testid="stop-button"]:visible'),
                ])
                client._standard_evidence['generation_active_before_cleanup'] = await page_has_stop_button(client.page)
                if stop is not None:
                    client._standard_evidence['cleanup_stop_attempted'] = True
                    await stop.click(timeout=3000)
                    for _ in range(30):
                        if not await page_has_stop_button(client.page):
                            break
                        await asyncio.sleep(.1)
                inactive = not await page_has_stop_button(client.page)
                client._standard_evidence['generation_inactive_after_cleanup'] = inactive
                client._standard_evidence['generation_stop_verified'] = inactive
                client._standard_evidence['generation_stop_verified_scope'] = 'after_exception_cleanup_not_natural_completion'
            except Exception:
                pass
            diagnostics = dict(getattr(client, "_standard_evidence", {}))
            if hint_evidence is not None:
                diagnostics['native_hint_experiment'] = hint_evidence
            if screenshot_evidence is not None:
                diagnostics['screenshot_evidence'] = screenshot_evidence
            if auth is not None:
                diagnostics['authentication'] = auth
            diagnostics.update({"elapsed_seconds": round(time.monotonic() - started, 3),
                                "completion_guard_version": "response-fix-v1",
                                "request_id": client._standard_request_id,
                                "protocol_error_tags": safe_protocol_error_tags(exc),
                                "response_complete": False, "exception_class": type(exc).__name__})
            # Only known static policy errors are returned; arbitrary Playwright
            # traces/headers/URLs are never passed through to the CLI logs.
            message = str(exc) if isinstance(exc, StandardStateError) else "Browser automation failed at " + kind
            content = {"error": {"type": kind, "message": message}, "mimicgate_diagnostics": diagnostics}
            if partial is not None:
                content['partial_response'] = partial
            return JSONResponse(status_code=401 if kind == 'authentication_missing' else 504 if kind == "timeout" else 502,
                content=content)
        finally:
            if client._standard_ui_lock_held:
                client._standard_ui_lock_held = False
                browser_ui_lock.release()
            base_client._model_selection_state_by_page_id.pop(id(client.page), None)
