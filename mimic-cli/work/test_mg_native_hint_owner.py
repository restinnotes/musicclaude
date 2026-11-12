import asyncio
import json
from unittest.mock import AsyncMock
import mg_native_hint_settings as hints


def test_baseline_uses_owner_and_clears_worker_headers(tmp_path,monkeypatch):
    marker=tmp_path/'mode.json';marker.write_text(json.dumps({'mode':'baseline'}))
    monkeypatch.setattr(hints,'SETTING',marker)
    monkeypatch.setenv('MIMICGATE_NATIVE_BROWSER_IDENTITY','1')
    page=AsyncMock();page.evaluate.return_value={'platform':'Linux'}
    result=asyncio.run(hints.apply_to_page(page))
    page.set_extra_http_headers.assert_awaited_once_with({})
    page.evaluate.assert_not_awaited()
    assert result['applied_by_owning_driver'] is True


def test_missing_flag_cannot_change_page(tmp_path,monkeypatch):
    marker=tmp_path/'mode.json';marker.write_text(json.dumps({'mode':'high_entropy'}))
    monkeypatch.setattr(hints,'SETTING',marker)
    monkeypatch.delenv('MIMICGATE_NATIVE_BROWSER_IDENTITY',raising=False)
    page=AsyncMock()
    assert asyncio.run(hints.apply_to_page(page)) is None
    page.evaluate.assert_not_awaited()
    page.set_extra_http_headers.assert_not_awaited()
