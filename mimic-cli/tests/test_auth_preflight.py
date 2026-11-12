"""Run inside the container; no browser, real cookies, HTTP or prompt sends."""
import contextlib
import json
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

from src.api.openai_schemas import ChatCompletionRequest, ChatMessage
import src.api.standard_completion as completion
from src.chatgpt.client import ChatGPTClient
from src.chatgpt.standard_mode import StandardStateError

class FakeClient(ChatGPTClient):
    def __init__(self, cookies):
        self._page=SimpleNamespace(context=SimpleNamespace(cookies=AsyncMock(return_value=cookies)))
        self._standard_evidence={}
        self._model_selection_state_by_page_id={}
        self.prepare_standard_chat=AsyncMock(side_effect=StandardStateError('ui_selector','Synthetic fixture stop'))
        self.send_message=AsyncMock()
        self._visible_control=AsyncMock(return_value=None)

class AuthPreflightTests(unittest.IsolatedAsyncioTestCase):
    async def run_request(self, cookies):
        client=FakeClient(cookies)
        @contextlib.asynccontextmanager
        async def lease():
            yield SimpleNamespace(page=client.page)
        request=ChatCompletionRequest(model='gpt-5.6-sol',reasoning_effort='xhigh',
              messages=[ChatMessage(role='user',content='NEVER SENT')],stream=False)
        events=[]
        with patch.object(completion,'acquire_browser_page',lease), \
             patch.object(completion,'page_has_stop_button',AsyncMock(return_value=False)), \
             patch('src.session_observer.emit',side_effect=lambda event,**fields: events.append({'event':event,**fields})):
            response=await completion.execute_standard_completion(request,client)
        return client,response,json.loads(response.body),events

    async def test_missing_auth_stops_before_any_ui_or_send(self):
        client,response,body,events=await self.run_request([])
        self.assertEqual(response.status_code,401)
        self.assertEqual(body['error']['type'],'authentication_missing')
        client.prepare_standard_chat.assert_not_awaited()
        client.send_message.assert_not_awaited()
        self.assertEqual(body['mimicgate_diagnostics']['authentication']['session_cookie_count'],0)
        self.assertEqual(events[-1]['error_type'],'authentication_missing')
        self.assertFalse(events[-1]['prompt_submitted'])

    async def test_cookie_values_never_enter_diagnostics(self):
        client,response,body,events=await self.run_request([
             {'name':'__Secure-next-auth.session-token','value':'SYNTHETIC_SECRET','expires':9999999999}])
        self.assertEqual(response.status_code,502)
        client.prepare_standard_chat.assert_awaited_once()
        client.send_message.assert_not_awaited()
        self.assertEqual(body['mimicgate_diagnostics']['authentication']['session_cookie_count'],1)
        self.assertNotIn('SYNTHETIC_SECRET',json.dumps(body)+json.dumps(events))

if __name__=='__main__':
    unittest.main()
