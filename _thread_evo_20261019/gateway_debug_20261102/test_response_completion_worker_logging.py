import asyncio
from contextlib import asynccontextmanager, ExitStack
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from src.api import standard_completion as api
from src.chatgpt import detector
from src.chatgpt.completion_guard import raise_on_response_error, read_response_error
from src.chatgpt.standard_mode import StandardStateError


class GuardTests(unittest.IsolatedAsyncioTestCase):
    async def test_visible_error_never_becomes_success(self):
        page=SimpleNamespace(evaluate=AsyncMock(return_value={'checked':True,'error':'message_stream_error'}))
        with self.assertRaises(StandardStateError) as caught:await raise_on_response_error(page)
        self.assertEqual(caught.exception.kind,'incomplete_response')

    async def test_error_check_failure_is_not_silent_success(self):
        page=SimpleNamespace(evaluate=AsyncMock(side_effect=RuntimeError('disconnected')))
        with self.assertRaises(StandardStateError) as caught:await read_response_error(page)
        self.assertEqual(caught.exception.kind,'completion_state')

    async def test_bad_snapshot_is_rejected(self):
        page=SimpleNamespace(evaluate=AsyncMock(return_value=None))
        with self.assertRaises(StandardStateError):await read_response_error(page)

    async def test_copy_ready_does_not_override_stream_error(self):
        with patch.object(detector,'raise_on_response_error',AsyncMock(side_effect=StandardStateError('incomplete_response','stream'))), \
             patch.object(detector,'_latest_assistant_turn_snapshot',AsyncMock(return_value={'signature':'new','hasCopyButton':True,'hasStopButton':False})) as snapshot:
            with self.assertRaises(StandardStateError):await detector._wait_for_copy_button_or_image(object(),0,100)
            snapshot.assert_not_awaited()

    async def test_stop_disappearing_does_not_override_error(self):
        with patch.object(detector,'raise_on_response_error',AsyncMock(side_effect=StandardStateError('incomplete_response','stream'))), \
             patch.object(detector,'page_has_stop_button',AsyncMock(return_value=True)):
            with self.assertRaises(StandardStateError):await detector._wait_via_stop_button(object(),100)

    async def test_text_stability_does_not_override_error(self):
        with patch.object(detector,'raise_on_response_error',AsyncMock(side_effect=StandardStateError('incomplete_response','stream'))):
            with self.assertRaises(StandardStateError):await detector._wait_via_text_stability(object(),100)


class StandardRouteTests(unittest.IsolatedAsyncioTestCase):
    async def execute(self, errors, *, send_error=None, active=False):
        page=MagicMock();page.url='https://chatgpt.com/?temporary-chat=true'
        state={'active':active};stop=SimpleNamespace(click=AsyncMock(side_effect=lambda **kw:state.update(active=False)))
        client=SimpleNamespace(_recent_backend_events=[],page=page,_visible_control=AsyncMock(return_value=stop if active else None))
        async def prepare(*args):
            client._standard_evidence.update(preparation_started_at=1.0,submitted_at=2.0)
        client.prepare_standard_chat=prepare
        client.send_message=AsyncMock(side_effect=send_error,return_value=SimpleNamespace(message='{"done":true}',thread_id='test-thread'))
        base=MagicMock(spec=api.ChatGPTClient);base._model_selection_state_by_page_id={}
        @asynccontextmanager
        async def acquire():yield SimpleNamespace(page=page)
        request=SimpleNamespace(model='gpt-6',reasoning_effort='high',stream=False,thread_id=None,conversation_id=None,
            tools=None,read_aloud=False,n=1,reasoning=None,messages=[SimpleNamespace(role='user',content='return JSON')])
        with ExitStack() as stack:
            stack.enter_context(patch.object(api,'acquire_browser_page',acquire))
            stack.enter_context(patch.object(api,'browser_ui_lock',asyncio.Lock()))
            stack.enter_context(patch.object(api.copy,'copy',return_value=client))
            stack.enter_context(patch.object(api,'get_concurrency_stats',return_value={'in_flight':1}))
            stack.enter_context(patch('src.session_observer.request_auth_snapshot',AsyncMock(return_value={'session_cookie_count':2})))
            stack.enter_context(patch('src.session_observer.emit'))
            stack.enter_context(patch('src.cookie_capacity.ensure_cookie_headroom',AsyncMock(return_value={})))
            stack.enter_context(patch.object(api,'capture_probe_evidence',AsyncMock(return_value=None)))
            stack.enter_context(patch.object(api,'read_response_error',AsyncMock(side_effect=errors)))
            stack.enter_context(patch.object(api,'page_has_stop_button',AsyncMock(side_effect=lambda *args:state['active'])))
            stack.enter_context(patch.object(api,'_latest_assistant_turn_snapshot',AsyncMock(return_value={'text':'partial draft'})))
            response=await api._execute_standard_completion(request,base)
        return response,json.loads(response.body),client

    async def test_complete_answer_is_returned_once(self):
        response,body,client=await self.execute([{'checked':True,'error':None}]*2)
        self.assertEqual(response.status_code,200);self.assertEqual(body['choices'][0]['message']['content'],'{"done":true}')
        self.assertTrue(body['mimicgate_diagnostics']['response_complete']);client.send_message.assert_awaited_once()

    async def test_nonempty_text_plus_error_is_failure_with_partial(self):
        response,body,client=await self.execute([{'checked':True,'error':'message_stream_error'}]*2)
        self.assertEqual(response.status_code,502);self.assertNotIn('choices',body)
        self.assertEqual(body['partial_response']['content'],'{"done":true}')
        self.assertFalse(body['partial_response']['complete']);self.assertFalse(body['mimicgate_diagnostics']['response_complete'])
        client.send_message.assert_awaited_once()

    async def test_error_arriving_during_capture_is_rejected(self):
        response,body,_=await self.execute([{'checked':True,'error':None}]+[{'checked':True,'error':'message_stream_error'}]*2)
        self.assertEqual(response.status_code,502);self.assertNotIn('choices',body)
        self.assertIn('partial_response',body)

    async def test_wait_failure_preserves_dom_partial_without_resend(self):
        response,body,client=await self.execute([{'checked':True,'error':'message_stream_error'}],
            send_error=StandardStateError('incomplete_response','stream'))
        self.assertEqual(response.status_code,502);self.assertEqual(body['partial_response']['content'],'partial draft')
        client.send_message.assert_awaited_once()

    async def test_cleanup_stop_is_distinguished_from_natural_stop(self):
        response,body,_=await self.execute([{'checked':True,'error':'message_stream_error'}],
            send_error=StandardStateError('incomplete_response','stream'),active=True)
        d=body['mimicgate_diagnostics'];self.assertTrue(d['generation_active_before_cleanup'])
        self.assertTrue(d['cleanup_stop_attempted']);self.assertTrue(d['generation_inactive_after_cleanup'])
        self.assertEqual(d['generation_stop_verified_scope'],'after_exception_cleanup_not_natural_completion')


if __name__=='__main__':unittest.main()
