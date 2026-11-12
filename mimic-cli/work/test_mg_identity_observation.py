"""No network or browser; observed identities and negotiated headers stay bounded."""
import json
import asyncio
from types import SimpleNamespace
from src import request_observer as observer


def test_browser_instance_presence_is_explicit_without_identifier_value():
    absent=observer.request_metadata('{"model":"gpt-5-6-thinking"}')
    assert absent['browser_context_present'] is False
    present=observer.request_metadata(json.dumps({'browser_context':{'instance_id':'PRIVATE-INSTANCE'}}))
    assert present['browser_context_present'] and present['browser_context_is_object']
    assert present['browser_context_instance_id_present']
    assert present['browser_context_instance_id_nonempty_string']
    assert 'PRIVATE' not in json.dumps(present)


def test_high_entropy_headers_observed_as_hashes_not_raw_identity():
    value='PRIVATE-ARCH'
    result=observer.wire_cookie_metadata({'headers':{'Sec-CH-UA-Arch':value,
        'Sec-CH-UA-Full-Version-List':'PRIVATE-VERSION'},'associatedCookies':[]})
    assert 'sec-ch-ua-arch' in result['header_names']
    assert result['client_header_context']['sec-ch-ua-arch']['characters']==len(value)
    assert 'PRIVATE' not in json.dumps(result)


def test_accept_ch_is_passive_and_filters_unknown_fields(monkeypatch):
    events=[]
    class Context:
        pages=[]
        def __init__(self):self.callbacks={}
        def on(self,name,callback):self.callbacks.setdefault(name,[]).append(callback)
    context=Context()
    monkeypatch.delenv('MIMICGATE_FORENSIC_ASSETS',raising=False)
    observer.attach_generation_audit(context,lambda event,**fields:events.append({'event':event,**fields}))
    request=SimpleNamespace(resource_type='document',frame=SimpleNamespace(page=object()),method='GET')
    response=SimpleNamespace(url='https://chatgpt.com/',request=request,status=200,
        headers={'Accept-CH':'Sec-CH-UA-Arch, Sec-CH-UA-Bitness, PRIVATE-SECRET',
                 'Critical-CH':'Sec-CH-UA-Arch', 'Set-Cookie':'PRIVATE-AUTH'})
    # This existing response handler reads headers without issuing a request.
    asyncio.run(context.callbacks['response'][0](response))
    row=events[-1]
    assert row['event']=='client_hint_negotiation_observed'
    assert row['requested_ua_hint_headers']==['sec-ch-ua-arch','sec-ch-ua-bitness']
    assert row['critical_ua_hint_headers']==['sec-ch-ua-arch']
    assert 'PRIVATE' not in json.dumps(events)
    response.headers={}
    asyncio.run(context.callbacks['response'][0](response))
    assert events[-1]['accept_ch_present'] is False
