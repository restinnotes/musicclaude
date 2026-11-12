"""Standard CLI completion inside the existing MimicGate browser service."""
from __future__ import annotations

import asyncio
import copy
import re
import time
import uuid

from fastapi.responses import JSONResponse
from src.api.browser_gate import acquire_browser_page, browser_ui_lock, BrowserBusyError, get_concurrency_stats
from src.chatgpt.client import ChatGPTClient
from src.chatgpt.standard_mode import StandardStateError
from src.chatgpt.detector import is_incomplete_response_text, page_has_stop_button


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


async def execute_standard_completion(request, base_client):
    try:
        return await _execute_standard_completion(request, base_client)
    except Exception as exc:
        # Includes page-lease failures before a client can be bound.
        kind = classify_error(exc)
        return JSONResponse(status_code=429 if kind == 'busy' else 502, content={"error": {
            "type": kind, "message": "MimicGate browser request failed before completion"},
            "mimicgate_diagnostics": {"response_complete": False,
                                      "exception_class": type(exc).__name__}})


async def _execute_standard_completion(request, base_client):
    if (request.model != "gpt-5.6-sol" or request.reasoning_effort != "xhigh"
            or request.stream or request.thread_id or request.conversation_id
            or request.tools or request.read_aloud or request.n not in {None, 1}
            or request.reasoning or len(request.messages) != 1
            or request.messages[0].role != "user"
            or not isinstance(request.messages[0].content, str)
            or not request.messages[0].content.strip()):
        return JSONResponse(status_code=400, content={"error": {
            "type": "standard_contract", "message": "Requires one text user prompt, gpt-5.6-sol, xhigh, non-streaming one-shot"}})
    if not isinstance(base_client, ChatGPTClient):
        return JSONResponse(status_code=503, content={"error": {
            "type": "provider_state", "message": "The existing ChatGPT browser client is unavailable"}})
    started = time.monotonic()
    # Each one-shot owns a separate worker page in the existing browser profile.
    async with acquire_browser_page() as lease:
        client = copy.copy(base_client.bind_page(lease.page))
        client._standard_request_id = uuid.uuid4().hex
        client._standard_ui_lock_held = False
        client._recent_backend_events = []
        try:
            await browser_ui_lock.acquire()
            client._standard_ui_lock_held = True
            await client.prepare_standard_chat()
            from src.api.probe_evidence import capture_probe_evidence
            await capture_probe_evidence(client, 'prepared')
            response = await client.send_message(request.messages[0].content,
                                                 model="gpt-5.6-sol", reasoning_effort="xhigh")
            validation = {'nonempty': bool(response.message),
                          'transient_text': is_incomplete_response_text(response.message),
                          'generation_active': await page_has_stop_button(client.page),
                          'response_characters': len(response.message or '')}
            client._standard_evidence['response_validation'] = validation
            if (not validation['nonempty'] or validation['transient_text'] or validation['generation_active']):
                raise StandardStateError("incomplete_response", "The browser has not produced a complete final answer")
            response_completed_at = time.time()
            screenshot_evidence = await capture_probe_evidence(client, 'response')
            diagnostics = dict(client._standard_evidence)
            diagnostics['screenshot_evidence'] = screenshot_evidence
            diagnostics.update({"prompt_submitted": True, "response_complete": True,
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
                "object": "chat.completion", "created": int(time.time()), "model": "gpt-5.6-sol",
                "choices": [{"index": 0, "message": {"role": "assistant", "content": response.message},
                             "finish_reason": "stop"}], "mimicgate_diagnostics": diagnostics})
        except Exception as exc:
            kind = classify_error(exc)
            if not client._standard_ui_lock_held:
                await browser_ui_lock.acquire()
                client._standard_ui_lock_held = True
            # Stop only this request's page before the worker returns to the pool.
            try:
                if kind == "busy":
                    # This generation predates our request; leave it alone.
                    raise StandardStateError("busy", "Existing generation belongs to another turn")
                stop = await client._visible_control([
                    client.page.get_by_role("button", name=re.compile(
                        r"^(Stop generating|Stop answering|Stop responding|Stop|停止生成|停止回答)$", re.I)),
                    client.page.locator('button[data-testid="stop-button"]:visible'),
                ])
                if stop is not None:
                    await stop.click(timeout=3000)
                    for _ in range(30):
                        if not await page_has_stop_button(client.page):
                            break
                        await asyncio.sleep(.1)
                client._standard_evidence["generation_stop_verified"] = not await page_has_stop_button(client.page)
            except Exception:
                pass
            diagnostics = dict(getattr(client, "_standard_evidence", {}))
            diagnostics.update({"elapsed_seconds": round(time.monotonic() - started, 3),
                                "response_complete": False, "exception_class": type(exc).__name__})
            # Only known static policy errors are returned; arbitrary Playwright
            # traces/headers/URLs are never passed through to the CLI logs.
            message = str(exc) if isinstance(exc, StandardStateError) else "Browser automation failed at " + kind
            return JSONResponse(status_code=504 if kind == "timeout" else 502,
                content={"error": {"type": kind, "message": message}, "mimicgate_diagnostics": diagnostics})
        finally:
            if client._standard_ui_lock_held:
                client._standard_ui_lock_held = False
                browser_ui_lock.release()
            base_client._model_selection_state_by_page_id.pop(id(client.page), None)
