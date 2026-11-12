"""Owned-clone diagnostic: expose only actual native UAData as HTTP hints."""
import argparse
import asyncio
import json
import os
import re
from pathlib import Path

SETTING = Path('/app/state/.mg-native-hints.json')


def quoted(value):
    if not isinstance(value,str) or len(value)>128 or not all(32<=ord(c)<=126 for c in value):
        raise ValueError('Invalid native structured string')
    return '"'+value.replace('\\','\\\\').replace('"','\\"')+'"'


def native_headers(value):
    if not isinstance(value,dict) or value.get('platform')!='Linux':
        raise ValueError('Diagnostic requires native Linux metadata')
    architecture=value.get('architecture');bitness=value.get('bitness')
    if architecture not in ('x86','arm') or bitness not in ('32','64'):
        raise ValueError('Native architecture not available')
    version=value.get('uaFullVersion')
    if not isinstance(version,str) or not re.fullmatch(r'153\.\d+\.\d+\.\d+',version):
        raise ValueError('Unexpected native browser version')
    brands=value.get('fullVersionList')
    if not isinstance(brands,list) or not 1<=len(brands)<=8:
        raise ValueError('Native full version list not available')
    fields=[]
    for item in brands:
        if (not isinstance(item,dict) or not isinstance(item.get('version'),str)
                or not re.fullmatch(r'\d+(?:\.\d+){0,3}',item['version'])):
            raise ValueError('Invalid native brand version')
        fields.append(quoted(item.get('brand'))+';v='+quoted(item['version']))
    return {'sec-ch-ua-arch':quoted(architecture),'sec-ch-ua-bitness':quoted(bitness),
        'sec-ch-ua-full-version-list':', '.join(fields),
        'sec-ch-ua-platform-version':quoted(value.get('platformVersion'))}


async def apply_to_page(page):
    """Called by the owning MG driver before UI preparation; no second driver."""
    if os.environ.get('MIMICGATE_NATIVE_BROWSER_IDENTITY')!='1' or not SETTING.is_file():
        return None
    if SETTING.is_symlink() or SETTING.stat().st_size>128:
        raise RuntimeError('Invalid diagnostic setting')
    mode=json.loads(SETTING.read_text())['mode']
    if mode not in ('baseline','high_entropy'):
        raise RuntimeError('Invalid diagnostic hint mode')
    metadata=None
    if mode=='high_entropy':
        metadata=await page.evaluate('''async () => {
            if (!navigator.userAgentData) return null;
            return await navigator.userAgentData.getHighEntropyValues(
                ['architecture','bitness','platformVersion','fullVersionList','uaFullVersion']);
        }''')
    headers=native_headers(metadata) if mode=='high_entropy' else {}
    await page.set_extra_http_headers(headers)
    return dict(mode=mode,actual_native_metadata=metadata,
        supplied_header_names=sorted(headers),supplied_headers=headers,
        original_native_low_entropy_headers_overridden=False,
        request_body_edited=False,opaque_instance_id_injected=False,
        cookie_or_login_changed=False,applied_by_owning_driver=True)


def configure(mode):
    if os.environ.get('MIMICGATE_NATIVE_BROWSER_IDENTITY')!='1':
        raise RuntimeError('Only the native identity diagnostic clone is eligible')
    SETTING.write_text(json.dumps({'mode':mode}))
    print(json.dumps(dict(mode=mode,setting_saved=True,
        browser_connected_by_helper=False,cookie_or_login_changed=False)),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('mode',choices=['baseline','high_entropy'])
    args=parser.parse_args()
    try:configure(args.mode)
    except Exception as error:
        print(json.dumps(dict(configured=False,error_class=type(error).__name__)),flush=True)
        raise SystemExit(1)
