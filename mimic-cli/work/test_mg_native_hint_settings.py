import copy
import pytest
from mg_native_hint_settings import native_headers


def native():
    return dict(platform='Linux',architecture='x86',bitness='64',platformVersion='',
        uaFullVersion='153.0.8010.12',fullVersionList=[
            dict(brand='Chromium',version='153.0.8010.12'),
            dict(brand='Not_A Brand',version='99.0.0.0')])


def test_headers_use_native_values_and_keep_platform_version_empty():
    headers=native_headers(native())
    assert headers['sec-ch-ua-arch']=='"x86"'
    assert headers['sec-ch-ua-bitness']=='"64"'
    assert headers['sec-ch-ua-platform-version']=='""'
    assert headers['sec-ch-ua-full-version-list']=='"Chromium";v="153.0.8010.12", "Not_A Brand";v="99.0.0.0"'
    assert 'sec-ch-ua' not in headers and 'user-agent' not in headers


@pytest.mark.parametrize('field,value',[('platform','Windows'),('bitness',None),
    ('uaFullVersion','154.1.2.3'),('fullVersionList',[]),('platformVersion','bad\r\nvalue')])
def test_rejects_missing_inconsistent_or_header_injection_metadata(field,value):
    info=native();info[field]=value
    with pytest.raises(ValueError):native_headers(info)


def test_structured_brand_strings_are_escaped_without_changing_identity():
    info=native();info['fullVersionList'][1]['brand']='Not "A\\ Brand'
    assert '"Not \\"A\\\\ Brand";v=' in native_headers(info)['sec-ch-ua-full-version-list']
