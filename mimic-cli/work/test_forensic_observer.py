"""Pure fake-response/CDP tests; no real browser, network or container."""
import asyncio
import hashlib
import json
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock,patch

import src.request_observer as observer


class Context:
    def __init__(self):self.listeners={}
    def on(self,name,callback):self.listeners.setdefault(name,[]).append(callback)


class Response:
    def __init__(self,data=b'public JavaScript code',*,page=None,url=None,status=200,headers=None):
        self.url=url or 'https://cdn.oaistatic.com/assets/123456.abcdef1234.js?private=SECRET'
        self.status=status
        self.headers={'content-type':'application/javascript',**(headers or {})}
        self.from_service_worker=False
        self.request=SimpleNamespace(method='GET',frame=SimpleNamespace(page=page))
        self.body=AsyncMock(return_value=data)


class ForensicAssetsTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.context,self.events,self.page=Context(),[],object()
        self.budget=observer._AssetBudget()
        self.collector=observer._ForensicAssets(self.context,
            lambda event,**fields:self.events.append({'event':event,**fields}),self.budget)

    async def drain(self):
        while self.budget.tasks:
            await asyncio.gather(*list(self.budget.tasks),return_exceptions=True)
            await asyncio.sleep(0)

    def assets(self):return [row for row in self.events if row['event']=='forensic_frontend_asset']

    async def test_received_js_hashed_without_query_or_body_and_without_blocking_callback(self):
        response=Response(b'PRIVATE AUTH COOKIE thought code',page=self.page)
        self.collector.on_response(response)
        self.assertFalse(response.body.called)
        await self.drain()
        row=self.assets()[0]
        self.assertEqual(row['basename'],'123456.abcdef1234.js')
        self.assertEqual(row['body_sha256'],hashlib.sha256(b'PRIVATE AUTH COOKIE thought code').hexdigest())
        self.assertTrue(row['observation_complete'])
        self.assertFalse(row['executed_bytecode_verified'])
        self.assertFalse(row['from_service_worker'])
        self.assertNotIn('from_disk_cache',row)
        self.assertNotIn('PRIVATE',json.dumps(self.events));self.assertNotIn('SECRET',json.dumps(self.events))
        self.assertEqual(response.body.await_count,1)

    async def test_wrong_host_path_method_or_untrusted_basename_ignored(self):
        for url in ('https://evil.example/assets/123456.abcdef1234.js',
                    'http://cdn.oaistatic.com/assets/123456.abcdef1234.js',
                    'https://chatgpt.com/backend-api/assets/123456.abcdef1234.js',
                    'https://chatgpt.com/assets/private/123456.abcdef1234.js',
                    'https://chatgpt.com/assets/SECRET_PRIVATE.js',
                    'https://auth:secret@chatgpt.com/assets/123456.abcdef1234.js'):
            response=Response(page=self.page,url=url)
            self.collector.on_response(response);self.assertFalse(response.body.called)
        response=Response(page=self.page);response.request.method='POST'
        self.collector.on_response(response)
        self.assertEqual(self.assets(),[])
        self.assertFalse(self.budget.tasks)

    async def test_http_errors_unknown_page_and_non_js_type_not_hashable(self):
        responses=[Response(page=self.page,status=403),Response(page=None),
            Response(page=self.page,headers={'content-type':'text/html'})]
        for response in responses:self.collector.on_response(response)
        await self.drain()
        self.assertEqual({row['error_code'] for row in self.assets()},
            {'response_not_200','page_unattributed','javascript_type_unverified'})
        self.assertTrue(all(row['body_sha256'] is None for row in self.assets()))
        self.assertTrue(all(not response.body.called for response in responses))

    async def test_page_budget_and_oversized_response_remain_unknown(self):
        with patch.object(observer,'ASSET_PAGE_BYTES',8):
            first=Response(b'12345678',page=self.page)
            second=Response(b'X',page=self.page)
            self.collector.on_response(first);self.collector.on_response(second)
            await self.drain()
        self.assertEqual(self.assets()[0]['body_bytes'],8)
        self.assertEqual(self.assets()[1]['error_code'],'body_budget_exhausted')
        self.assertFalse(second.body.called)
        other=Response(b'123456789',page=object())
        with patch.object(observer,'ASSET_PAGE_BYTES',8):
            self.collector.on_response(other);await self.drain()
        self.assertEqual(self.assets()[-1]['error_code'],'decoded_body_over_budget')
        self.assertIsNone(self.assets()[-1]['body_bytes'])

    async def test_global_budget_applies_across_distinct_pages(self):
        self.budget.remaining=8
        with patch.object(observer,'ASSET_PAGE_BYTES',8):
            first=Response(b'12345678',page=self.page);second=Response(b'X',page=object())
            self.collector.on_response(first);await self.drain()
            self.collector.on_response(second);await self.drain()
        self.assertEqual(self.budget.remaining,0)
        self.assertEqual(self.assets()[-1]['error_code'],'body_budget_exhausted')
        self.assertFalse(second.body.called)

    async def test_declared_oversize_skips_body_and_read_failure_is_safe_unknown(self):
        first=Response(page=self.page,headers={'content-length':str(observer.ASSET_PAGE_BYTES+1)})
        second=Response(page=self.page);second.body.side_effect=RuntimeError('SECRET AUTH COOKIE')
        self.collector.on_response(first);self.collector.on_response(second);await self.drain()
        self.assertFalse(first.body.called)
        self.assertEqual({row['error_code'] for row in self.assets()},
            {'declared_body_over_budget','body_read_unavailable'})
        self.assertNotIn('SECRET',json.dumps(self.events))

    async def test_record_and_queue_limits_prevent_task_growth(self):
        with patch.object(observer,'ASSET_MAX_PENDING',2),patch.object(observer,'ASSET_PAGE_RECORDS',4):
            for _ in range(20):self.collector.on_response(Response(page=self.page))
            self.assertLessEqual(len(self.budget.pending),2)
            self.assertLessEqual(len(self.budget.tasks),2)
            await self.drain()
        self.assertLessEqual(len(self.assets()),4)
        self.assertTrue(any(row.get('error_code')=='page_record_limit' for row in self.events))
        self.assertTrue(any(row.get('error_code')=='pending_limit' for row in self.assets()))

    async def test_process_record_limit_cannot_be_bypassed_with_new_pages(self):
        with patch.object(observer,'ASSET_PROCESS_RECORDS',3):
            for _ in range(10):self.collector.on_response(Response(page=object()))
            await self.drain()
        self.assertEqual(self.budget.records,3)
        self.assertEqual(len(self.assets()),3)
        self.assertTrue(any(row.get('error_code')=='process_record_limit' for row in self.events))

    async def test_context_close_cancels_and_settles_active_tasks(self):
        started=asyncio.Event()
        async def waiting():started.set();await asyncio.Event().wait()
        response=Response(page=self.page);response.body.side_effect=waiting
        self.collector.on_response(response);await started.wait()
        self.collector.close();await self.drain()
        self.assertFalse(self.budget.tasks)
        self.assertFalse(self.budget.pending)
        self.assertTrue(any(row.get('error_code')=='body_read_cancelled' for row in self.assets()))
        self.collector.on_response(Response(page=self.page));self.assertFalse(self.budget.tasks)

    async def test_body_timeout_does_not_retry_or_leak_exception(self):
        response=Response(page=self.page)
        async def waiting():await asyncio.Event().wait()
        response.body.side_effect=waiting
        with patch.object(observer,'ASSET_BODY_TIMEOUT',0.01):
            self.collector.on_response(response);await self.drain()
        self.assertEqual(response.body.await_count,1)
        self.assertEqual(self.assets()[0]['error_code'],'body_read_unavailable')

    async def test_context_close_does_not_report_complete_after_prior_unknown(self):
        self.collector.on_response(Response(page=self.page,status=403))
        self.collector.close();self.collector.close()
        closed=[row for row in self.events if row['event']=='forensic_asset_collector_closed']
        self.assertEqual(len(closed),1)
        self.assertFalse(closed[0]['observation_complete'])

    async def test_actual_body_reads_remain_bounded_across_pages(self):
        release=asyncio.Event();started=asyncio.Event();active=0;maximum=0
        async def waiting():
            nonlocal active,maximum
            active+=1;maximum=max(maximum,active)
            if active==2:started.set()
            try:await release.wait();return b'JS'
            finally:active-=1
        pages=[object() for _ in range(6)]
        for page in pages:
            response=Response(page=page);response.body.side_effect=waiting
            self.collector.on_response(response)
        await asyncio.wait_for(started.wait(),timeout=1)
        self.assertEqual(maximum,2)
        release.set();await self.drain()
        self.assertEqual(len(self.assets()),6)
        self.assertEqual(maximum,2)

    async def test_opt_in_only_installs_asset_response_callback(self):
        with patch.dict('os.environ',{},clear=True):
            context=Context();observer.attach_generation_audit(context,lambda *a,**k:None)
        self.assertEqual(set(context.listeners),{'request','response'})
        self.assertEqual(len(context.listeners['response']),1)
        with patch.dict('os.environ',{'MIMICGATE_FORENSIC_ASSETS':'1'}),patch.object(observer,'_asset_budget',observer._AssetBudget()):
            context=Context();observer.attach_generation_audit(context,lambda *a,**k:None)
        self.assertEqual(len(context.listeners['response']),2)
        self.assertEqual(len(context.listeners['close']),1)


class CompletenessAndDeviceTests(unittest.TestCase):
    def test_oversized_line_can_continue_parsing_but_completeness_is_false(self):
        parser=observer.StreamMetadata(max_line=40)
        parser.feed(b'data: '+b'x'*80+b'\ndata: [DONE]\n')
        self.assertTrue(parser.done)
        self.assertEqual(parser.completeness_fields()['oversized_lines_dropped'],1)
        self.assertTrue(parser.completeness_fields()['truncated'])
        self.assertFalse(parser.completeness_fields()['metadata_observation_complete'])

    def test_unique_record_limit_is_visible_without_discarding_prior_metadata(self):
        parser=observer.StreamMetadata()
        for value in range(129):
            parser.feed(('data: '+json.dumps({'thinking_time_ms':value})+'\n').encode())
        parser.feed(b'data: [DONE]\n')
        self.assertEqual(len(parser.records),128)
        self.assertTrue(parser.completeness_fields()['metadata_record_limit_reached'])
        self.assertFalse(parser.completeness_fields()['metadata_observation_complete'])

    def test_complete_and_incomplete_or_failed_stream_remain_distinct(self):
        parser=observer.StreamMetadata();parser.feed(b'data: [DONE]\n')
        self.assertTrue(parser.completeness_fields()['metadata_observation_complete'])
        parser.early_buffer_limit_reached=True
        self.assertFalse(parser.completeness_fields()['metadata_observation_complete'])
        parser.early_buffer_limit_reached=False;parser.observation_error=True
        self.assertFalse(parser.completeness_fields()['metadata_observation_complete'])
        self.assertFalse(observer.StreamMetadata().completeness_fields()['metadata_observation_complete'])

    def test_canonical_device_cookie_comparison_is_safe_and_conflicts_not_collapsed(self):
        def event(values):return {'headers':{'OAI-DID':'PRIVATE DEVICE'},'associatedCookies':[
            {'cookie':{'name':'oai-did','value':value},'blockedReasons':[]} for value in values]}
        matched=observer.wire_cookie_metadata(event(['PRIVATE DEVICE']))
        self.assertTrue(matched['oai_did_header_matches_sent_device_cookie'])
        self.assertEqual(matched['actual_oai_did_header_sha256'],hashlib.sha256(b'PRIVATE DEVICE').hexdigest())
        mismatch=observer.wire_cookie_metadata(event(['OTHER']))
        self.assertFalse(mismatch['oai_did_header_matches_sent_device_cookie'])
        conflict=observer.wire_cookie_metadata(event(['PRIVATE DEVICE','OTHER']))
        self.assertTrue(conflict['sent_device_cookie_conflict'])
        self.assertIsNone(conflict['oai_did_header_matches_sent_device_cookie'])
        self.assertNotIn('PRIVATE',json.dumps([matched,mismatch,conflict]))


class StreamCDPTests(unittest.IsolatedAsyncioTestCase):
    async def test_early_buffer_loss_and_stream_enable_error_visible_at_finish(self):
        session=Context()
        async def send(method,params):
            if method=='Network.streamResourceContent':raise RuntimeError('SECRET')
            return {}
        session.send=send
        context=SimpleNamespace(new_cdp_session=AsyncMock(return_value=session))
        events=[]
        await observer.attach_page_stream_audit(context,object(),lambda event,**fields:events.append({'event':event,**fields}))
        request={'requestId':'private-CDP-ID','request':{'method':'POST','url':'https://chatgpt.com/backend-api/f/conversation','postData':'{}'}}
        session.listeners['Network.requestWillBeSent'][0](request)
        import base64
        session.listeners['Network.dataReceived'][0]({'requestId':request['requestId'],'data':base64.b64encode(b'x'*(256*1024+1)).decode()})
        await session.listeners['Network.responseReceived'][0]({'requestId':request['requestId'],'response':{'status':200}})
        session.listeners['Network.loadingFinished'][0]({'requestId':request['requestId']})
        final=events[-1]
        self.assertTrue(final['early_buffer_limit_reached'])
        self.assertTrue(final['truncated'])
        self.assertFalse(final['metadata_observation_complete'])
        self.assertNotIn('SECRET',json.dumps(events))


if __name__=='__main__':unittest.main()
