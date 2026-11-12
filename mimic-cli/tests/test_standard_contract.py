"""Run in the existing container, with its installed MimicGate dependencies."""
import asyncio
import unittest

from src.api.openai_schemas import ChatCompletionRequest, ChatMessage
from src.api.standard_completion import execute_standard_completion
from src.chatgpt.standard_mode import StandardModeMixin


class MissingControl:
    async def count(self):
        return 0


class URLOnlyPage:
    url = "https://chatgpt.com/?temporary-chat=true"

    def get_by_role(self, *args, **kwargs):
        return MissingControl()

    def locator(self, *args, **kwargs):
        return MissingControl()


class URLOnlyClient(StandardModeMixin):
    _page = URLOnlyPage()


class StandardContractTests(unittest.IsolatedAsyncioTestCase):
    async def test_temporary_url_without_active_ui_is_rejected(self):
        state = await URLOnlyClient().temporary_chat_state()
        self.assertTrue(state["url_flag"])
        self.assertFalse(state["verified"])

    async def test_overrides_never_reach_browser(self):
        defaults = {"model": "gpt-5.6-sol", "reasoning_effort": "xhigh",
                    "messages": [ChatMessage(role="user", content="TEST")], "stream": False}
        overrides = [{"model": "gpt-5.5"}, {"reasoning_effort": "high"},
                     {"reasoning_effort": "extra-high"}, {"stream": True},
                     {"thread_id": "old-thread"}, {"conversation_id": "old-conversation"},
                     {"messages": [ChatMessage(role="system", content="TEST")]},
                     {"messages": [ChatMessage(role="user", content="")]},
                     {"n": 2}]
        for override in overrides:
            with self.subTest(override=override):
                request = ChatCompletionRequest(**(defaults | override))
                # Invalid inputs are rejected before checking provider or leasing
                # a browser. A sentinel object cannot accidentally send anything.
                response = await execute_standard_completion(request, object())
                self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
