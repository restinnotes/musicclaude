import asyncio
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from gpt2agent.backend import BackendClient
from gpt2agent.sse import ConversationClient, _build_payload


def backend(efforts):
    client = BackendClient.__new__(BackendClient)
    client._thinking_effort_catalogs = {}
    client.get = Mock(return_value={"models": [{
        "slug": "thinking-model",
        "thinking_efforts": [{"thinking_effort": effort} for effort in efforts],
    }]})
    return client


def test_current_account_rejects_max_before_sentinel_or_submit():
    client = backend(["standard", "extended"])
    client._reload_token_if_stale = lambda: None
    conv = ConversationClient(client)

    async def run():
        return [part async for part in conv.stream(
            "thinking-model", [{"role": "user", "content": "test"}], thinking_effort="max"
        )]

    with pytest.raises(ValueError, match="Unsupported Web thinking_effort 'max'"):
        asyncio.run(run())


def test_supported_effort_and_catalog_cached_per_chat_mode():
    client = backend(["standard", "extended"])
    for _ in range(2):
        client.validate_thinking_effort("thinking-model", "extended", True)
    assert client.get.call_count == 1
    client.validate_thinking_effort("thinking-model", "extended", False)
    assert client.get.call_count == 2
    payload = _build_payload("thinking-model", [], thinking_effort="extended")
    assert payload["thinking_effort"] == "extended"


def test_another_account_can_advertise_max_without_global_ban():
    client = backend(["standard", "extended", "max"])
    client.validate_thinking_effort("thinking-model", "max", True)


def test_no_explicit_effort_does_not_add_catalog_request():
    client = backend([])
    client.validate_thinking_effort("auto", None, True)
    client.get.assert_not_called()


def test_unavailable_model_cannot_silently_fall_back():
    client = backend(["extended"])
    with pytest.raises(ValueError, match="not available"):
        client.validate_thinking_effort("old-model", "extended", True)


def test_init_model_cap_never_chooses_suggested_fallback():
    client = backend(["extended"])
    client.post = Mock(return_value={"default_model_slug": "other-model", "model_limits": [
        {"model_slug": "thinking-model", "resets_after": "2099-01-01T00:00:00Z"},
    ]})
    with pytest.raises(RuntimeError, match="model usage limit"):
        client.check_conversation_model("thinking-model")


def test_init_cached_and_unusual_activity_backs_off():
    client = backend(["extended"])
    client.post = Mock(return_value={"model_limits": []})
    client.check_conversation_model("thinking-model")
    client.check_conversation_model("thinking-model")
    assert client.post.call_count == 1
    client._conversation_init_cache = None
    client._runtime = SimpleNamespace(backoff=Mock())
    client.post.return_value = {"banner_info": {"type": "unusual_activity"}}
    with pytest.raises(RuntimeError, match="unusual activity"):
        client.check_conversation_model("thinking-model")
    client._runtime.backoff.assert_called_once()
