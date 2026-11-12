import json
from pathlib import Path
from unittest.mock import patch
from unittest.mock import Mock
from types import SimpleNamespace
import src.request_observer as observer


def test_focus_is_explicit_bounded_numeric_prefixes(tmp_path):
    file=tmp_path/'focus.json';file.write_text(json.dumps(['7078','646436']))
    with patch.object(observer,'Path',return_value=file):
        assert observer._asset_prefix_filter()==frozenset(('7078','646436'))


def test_missing_invalid_or_oversized_marker_preserves_default(tmp_path):
    file=tmp_path/'focus.json'
    with patch.object(observer,'Path',return_value=file):
        assert not observer._asset_prefix_filter()
        for value in ({'token':'PRIVATE'},['7078','bad/path'],['7078']*17):
            file.write_text(json.dumps(value));assert not observer._asset_prefix_filter()
        file.write_text(' '*257);assert not observer._asset_prefix_filter()


def test_unrelated_scripts_do_not_consume_critical_asset_budget():
    budget=observer._AssetBudget();budget.kick=Mock()
    page=object()
    request=SimpleNamespace(method='GET',frame=SimpleNamespace(page=page))
    with patch.object(observer,'_asset_prefix_filter',return_value=frozenset(['7078','646436'])):
        collector=observer._ForensicAssets(Mock(),Mock(),budget)
    collector.on_response(SimpleNamespace(url='https://chatgpt.com/cdn/assets/155568.abcd1234.js',
        request=request,status=200))
    assert budget.records==0 and not budget.pending
    collector.on_response(SimpleNamespace(url='https://chatgpt.com/cdn/assets/7078.abcd1234.js',
        request=request,status=200))
    assert budget.records==1 and len(budget.pending)==1
    assert budget.remaining==observer.ASSET_PROCESS_BYTES
