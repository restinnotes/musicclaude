import asyncio
import importlib.util
from pathlib import Path
from unittest.mock import AsyncMock

spec=importlib.util.spec_from_file_location('environment_evidence',Path(__file__).resolve().parents[1]/'src/browser/environment_evidence.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def test_worlds_are_explicit_and_distinct():
    page=AsyncMock();page.evaluate.side_effect=[{'platform':'Linux x86_64'},{'platform':'Win32'}]
    result=asyncio.run(module.observe_environment(page))
    assert [c.kwargs['isolated_context'] for c in page.evaluate.await_args_list]==[False,True]
    assert result['execution_worlds']['main']['properties']['platform']=='Linux x86_64'
    assert result['execution_worlds']['isolated']['properties']['platform']=='Win32'
    assert not result['request_body_or_headers_changed']


def test_unavailable_world_is_not_reported_as_observed():
    page=AsyncMock();page.evaluate.side_effect=[RuntimeError('private diagnostic'),{'platform':'Linux x86_64'}]
    result=asyncio.run(module.observe_environment(page))
    assert result['execution_worlds']['main']=={'available':False,'error_class':'RuntimeError'}
    assert 'private diagnostic' not in str(result)
