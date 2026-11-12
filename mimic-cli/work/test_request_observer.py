import json
import math
import unittest
from unittest.mock import AsyncMock
from types import SimpleNamespace

from src.request_observer import attach_generation_audit, attach_page_stream_audit, generation_endpoint, request_metadata, response_metadata, StreamMetadata, wire_cookie_metadata, network_terminal_fields, GenerationCookieSequence


class CookieSequenceBindingTests(unittest.IsolatedAsyncioTestCase):
    async def test_early_extra_info_and_second_worker_share_passive_sequence(self):
        class Session:
            def __init__(self):
                self.handlers = {}
                self.send = AsyncMock(return_value={})
            def on(self, name, handler):
                self.handlers[name] = handler
        sessions = [Session(), Session()]
        context = SimpleNamespace(new_cdp_session=AsyncMock(side_effect=sessions))
        emitted = []
        def emit(event, **fields):
            emitted.append({'event':event, **fields})
        for index, value in enumerate(['SECRET_ONE', 'SECRET_TWO']):
            await attach_page_stream_audit(context, object(), emit)
            session = sessions[index]
            request_id = str(index)
            # An unrelated resource's ExtraInfo must not advance the baseline.
            session.handlers['Network.requestWillBeSentExtraInfo']({
                'requestId':'unrelated-'+request_id, 'associatedCookies':[{'cookie':{
                    'name':'_account','domain':'.chatgpt.com','path':'/','value':'RESOURCE_SECRET'},
                    'blockedReasons':[]}]})
            session.handlers['Network.requestWillBeSent']({'requestId':'unrelated-'+request_id,
                'wallTime':99.+index, 'timestamp':9.+index,
                'request':{'method':'GET','url':'https://chatgpt.com/example'}})
            session.handlers['Network.requestWillBeSentExtraInfo']({
                'requestId':request_id, 'associatedCookies':[{'cookie':{
                    'name':'__Secure-oai-is','domain':'.chatgpt.com','path':'/','value':value},
                    'blockedReasons':[]}]})
            session.handlers['Network.requestWillBeSent']({'requestId':request_id,
                'wallTime':100.+index, 'timestamp':10.+index,
                'request':{'method':'POST','url':'https://chatgpt.com/backend-api/f/conversation',
                    'postData':json.dumps({'model':'gpt-5-6-thinking','thinking_effort':'max'})}})
            self.assertEqual(session.send.await_args_list[0].args[0], 'Network.enable')
            self.assertEqual(session.send.await_count, 1)
        cookies = [x['session_context_cookie_sequence'] for x in emitted
                   if x['event']=='generation_wire_cookie_metadata']
        self.assertEqual(len(cookies), 2)
        self.assertFalse(cookies[0]['comparison_performed'])
        self.assertEqual(cookies[0]['revision'], 1)
        self.assertEqual(cookies[1]['revision'], 2)
        self.assertEqual(cookies[1]['changed_names'], ['__Secure-oai-is'])
        self.assertNotIn('SECRET', json.dumps(emitted))


class GenerationAuditTests(unittest.TestCase):
    def test_cookie_sequence_tracks_rotation_removal_and_conflict_without_saving_values(self):
        def state(value, domain='.chatgpt.com'):
            return GenerationCookieSequence.fingerprints({'associatedCookies': [
                {'cookie': {'name': '__Secure-oai-is', 'domain':domain, 'path':'/', 'value':value}, 'blockedReasons':[]},
                {'cookie': {'name':'UNKNOWN_SECRET_NAME', 'value':'PRIVATE'}, 'blockedReasons':[]},
                {'cookie': {'name':'_account', 'value':'BLOCKED'}, 'blockedReasons':['SecureOnly']}]})
        tracker = GenerationCookieSequence()
        first = tracker.observe(state('PRIVATE_ONE'), 100.)
        self.assertFalse(first['comparison_performed'])
        self.assertEqual(first['added_names'], ['__Secure-oai-is'])
        same = tracker.observe(state('PRIVATE_ONE'), 101.)
        self.assertEqual(same['revision'], 1)
        self.assertEqual(same['changed_names'], [])
        rotated = tracker.observe(state('PRIVATE_TWO'), 102.)
        self.assertEqual(rotated['changed_names'], ['__Secure-oai-is'])
        identity = tracker.observe(state('PRIVATE_TWO', 'chatgpt.com'), 103.)
        self.assertEqual(identity['changed_names'], ['__Secure-oai-is'])
        removed = tracker.observe({}, 104.)
        self.assertEqual(removed['removed_names'], ['__Secure-oai-is'])
        serialized = json.dumps([first, same, rotated, identity, removed])
        for secret in ['PRIVATE', 'BLOCKED', 'UNKNOWN_SECRET_NAME']:
            self.assertNotIn(secret, serialized)
        self.assertFalse(first['values_or_fingerprints_saved'])

    def test_missing_or_out_of_order_cookie_metadata_cannot_reset_baseline(self):
        tracker = GenerationCookieSequence()
        original = {'_account': frozenset([b'RAM_ONLY_1'])}
        newer = {'_account': frozenset([b'RAM_ONLY_2'])}
        tracker.observe(original, 100.)
        self.assertFalse(tracker.observe(None, 101.)['available'])
        self.assertFalse(tracker.observe(newer, 99.)['comparison_performed'])
        self.assertFalse(tracker.observe(newer, float('nan'))['comparison_performed'])
        self.assertEqual(tracker.observe(original, 102.)['changed_names'], [])
        self.assertEqual(tracker.observe(newer, 103.)['changed_names'], ['_account'])
        self.assertIsNone(GenerationCookieSequence.fingerprints({}))
        self.assertIsNone(GenerationCookieSequence.fingerprints({'associatedCookies':[{}]*513}))

    def test_explicit_server_error_envelope_preserves_presence_without_private_details(self):
        data = {'error': {'code': 'rate_limit_exceeded', 'message': 'PRIVATE DETAIL', 'token': 'SECRET'}}
        self.assertEqual(response_metadata(json.dumps(data)), {'metadata_records': [
            {'server_error_frame': True, 'server_error_code': 'rate_limit_exceeded'}]})
        data['error']['code'] = 'SECRET'
        result = response_metadata(json.dumps(data))
        self.assertEqual(result['metadata_records'][0]['server_error_code'], 'unknown')
        self.assertNotIn('SECRET', json.dumps(result))
        for wrapped in [{'content': data}, {'p': '/message/content/parts/0', 'v': data}]:
            self.assertEqual(response_metadata(json.dumps(wrapped)), {'metadata_records': []})

    def test_network_abort_retains_safe_code_and_distinguishes_active_from_idle_stream(self):
        entry = {'request_timestamp': 100., 'last_data_timestamp': 695., 'data_event_count': 42}
        result = network_terminal_fields({'timestamp': 703., 'errorText': 'net::ERR_ABORTED'}, entry)
        self.assertEqual(result, {'network_error': 'net::ERR_ABORTED', 'wire_duration_seconds': 603.,
            'last_network_data_seconds_after_request': 595., 'network_idle_seconds_at_finish': 8.,
            'network_data_event_count': 42})
        result = network_terminal_fields({'timestamp': float('nan'), 'errorText': 'SECRET URL',
            'blockedReason': 'PRIVATE'}, entry)
        self.assertEqual(result['network_error'], 'unknown')
        self.assertEqual(result['network_blocked_reason'], 'unknown')
        self.assertNotIn('wire_duration_seconds', result)
        self.assertNotIn('SECRET', json.dumps(result))
        self.assertNotIn('PRIVATE', json.dumps(result))

    def test_session_context_presence_has_no_values_and_excludes_blocked_cookies(self):
        result = wire_cookie_metadata({'associatedCookies': [
            {'cookie': {'name': '__Secure-oai-is', 'value': 'SECRET'}, 'blockedReasons': []},
            {'cookie': {'name': 'oai-client-auth-info', 'value': 'SECRET'}, 'blockedReasons': ['SecureOnly']},
            {'cookie': {'name': 'UNKNOWN_SECRET_NAME', 'value': 'SECRET'}, 'blockedReasons': []}]})
        self.assertEqual(result['sent_context_cookie_names'], ['__Secure-oai-is'])
        self.assertNotIn('SECRET', json.dumps(result))

    def test_actual_sent_cookie_audit_redacts_secrets_and_ignores_blocked_cookies(self):
        result = wire_cookie_metadata({'headers': {'Cookie': 'SECRET', 'Authorization': 'Bearer SECRET',
            'originator': 'Codex Browser', 'oai-language': 'zh-CN', 'user-agent': 'SECRET'},
            'associatedCookies': [{'cookie': {'name': '__Secure-next-auth.session-token', 'value': 'SECRET'}, 'blockedReasons': []},
                {'cookie': {'name': 'oai-did', 'value': 'DEVICESECRET'}, 'blockedReasons': []},
                {'cookie': {'name': '__Secure-next-auth.session-token.1', 'value': 'SECRET'}, 'blockedReasons': ['SecureOnly']}]})
        self.assertEqual(result['sent_cookie_count'], 2)
        self.assertEqual(result['sent_auth_cookie_count'], 1)
        self.assertEqual(result['client_header_context']['originator'], 'Codex Browser')
        self.assertNotIn('SECRET', json.dumps(result))
    def test_chunked_utf8_stream_drops_content_and_finds_metadata(self):
        parser = StreamMetadata()
        wire = ('data: ' + json.dumps({'message': {'content': {'parts': ['隐私SECRET']},
                'metadata': {'model_slug': 'gpt-5-6-thinking', 'thinking_effort': 'max'}}}, ensure_ascii=False)
                + '\n\ndata: [DONE]\n').encode()
        for byte in wire:
            parser.feed(bytes([byte]))
        self.assertTrue(parser.done)
        self.assertEqual(parser.pending, b'')
        self.assertEqual(parser.records, [{'model_slug': 'gpt-5-6-thinking', 'thinking_effort': 'max'}])
        self.assertNotIn('SECRET', json.dumps(parser.records))

    def test_stream_memory_is_bounded_and_oversized_line_does_not_fake_metadata(self):
        parser = StreamMetadata(max_bytes=300, max_line=50)
        parser.feed(b'data: ' + b'x' * 100)
        self.assertEqual(parser.pending, b'')
        parser.feed(b'\ndata: [DONE]\n')
        self.assertTrue(parser.done)
        parser.feed(b'x' * 300)
        self.assertTrue(parser.truncated)
        self.assertEqual(parser.pending, b'')

    def test_real_native_shape_and_private_fields_are_dropped(self):
        body = {'model': 'gpt-5-6-thinking', 'thinking_effort': 'max',
                'history_and_training_disabled': True, 'is_do_not_remember': False,
                'temporary_chat_requests_personalization': False,
                'client_prepare_state': {'token': 'SECRET'}, 'authorization': 'SECRET',
                'messages': [{'content': {'content_type': 'text', 'parts': ['PRIVATE PROMPT']}}]}
        result = request_metadata(json.dumps(body))
        self.assertEqual(result['model'], 'gpt-5-6-thinking')
        self.assertEqual(result['thinking_effort'], 'max')
        self.assertFalse(result['temporary_chat_requests_personalization'])
        self.assertEqual(result['text_characters'], 14)
        self.assertNotIn('SECRET', json.dumps(result))
        self.assertNotIn('PRIVATE PROMPT', json.dumps(result))

    def test_model_metadata_sse_and_patch_without_content(self):
        body = '\n'.join(['data: ' + json.dumps({'message': {
            'content': {'model_slug': 'gpt-secret', 'parts': ['PRIVATE']},
            'metadata': {'model_slug': 'gpt-5-6-thinking', 'thinking_effort': 'max'}}}),
            'data: ' + json.dumps({'p': '/message/content/parts', 'v': {'model_slug': 'gpt-secret'}}),
            'data: ' + json.dumps({'p': '/message/metadata/reasoning_time_ms', 'o': 'add', 'v': 700000}),
            'data: [DONE]'])
        result = response_metadata(body)
        self.assertIn({'model_slug': 'gpt-5-6-thinking', 'thinking_effort': 'max'}, result['metadata_records'])
        self.assertIn({'reasoning_time_ms': 700000}, result['metadata_records'])
        self.assertNotIn('PRIVATE', json.dumps(result))
        self.assertNotIn('gpt-secret', json.dumps(result))

    def test_untrusted_values_and_other_destinations_rejected(self):
        result = request_metadata(json.dumps({'model': 'Bearer SECRET', 'thinking_effort': 'SECRET'}))
        self.assertEqual(result, {})
        self.assertIsNone(generation_endpoint('https://example.com/backend-api/conversation'))
        self.assertIsNone(generation_endpoint('https://chatgpt.com/backend-api/auth/session'))
        self.assertEqual(generation_endpoint('https://chatgpt.com/backend-api/f/conversation'), '/backend-api/f/conversation')
        self.assertEqual(generation_endpoint('https://chatgpt.com/backend-api/f/conversation/prepare?x=PRIVATE'),
                         '/backend-api/f/conversation/prepare')
        self.assertEqual(generation_endpoint('https://chatgpt.com/backend-api/conversation/prepare'),
                         '/backend-api/conversation/prepare')
        self.assertIsNone(generation_endpoint('https://example.com/backend-api/f/conversation/prepare'))

    def test_message_and_reasoning_terminal_metadata_without_text_or_identity(self):
        body = {'message': {'id': 'PRIVATE-ID', 'author': {'role': 'tool', 'name': 'python'},
            'recipient': 'all', 'channel': 'analysis', 'status': 'finished_failed', 'end_turn': False,
            'content': {'parts': ['PRIVATE TRACEBACK AND THINKING'], 'model_slug': 'gpt-secret'},
            'metadata': {'reasoning_status': 'error', 'finished_duration_sec': 106.25,
                'finish_details': {'type': 'stop', 'stop_tokens': ['PRIVATE STOP TOKEN']},
                'force_login': False, 'authorization': 'PRIVATE AUTH', 'conversation_id': 'PRIVATE CID'}}}
        result = response_metadata(json.dumps(body))
        self.assertIn({'message_author_role': 'tool', 'message_author_name': 'python',
            'message_author_name_present': True, 'message_recipient': 'all',
            'message_channel': 'analysis', 'message_status': 'finished_failed',
            'message_end_turn': False, 'message_author_tool_family': 'python',
            'message_author_tool_namespaced': False}, result['metadata_records'])
        self.assertIn({'reasoning_status': 'error', 'finished_duration_sec': 106.25,
            'force_login': False, 'finish_details': {'type': 'stop', 'stop_tokens_type': 'list'}},
            result['metadata_records'])
        self.assertNotIn('PRIVATE', json.dumps(result))
        self.assertNotIn('gpt-secret', json.dumps(result))

    def test_known_message_leaf_patches_and_finish_shape_never_walk_secret_leaf_objects(self):
        patches = [
            {'p': '/message/author/role', 'v': 'assistant'},
            {'path': '/message/recipient', 'value': 'python'},
            {'p': '/message/channel', 'v': 'analysis'},
            {'p': '/message/status', 'v': 'finished_successfully'},
            {'p': '/message/end_turn', 'v': True},
            {'p': '/message/metadata/reasoning_status', 'v': 'completed'},
            {'p': '/message/metadata/finished_duration_sec', 'v': 10},
            {'p': '/message/metadata/finish_details/type', 'v': 'stop'},
            {'p': '/message/metadata/finish_details/stop_tokens',
             'v': {'model_slug': 'gpt-secret', 'thinking_effort': 'max', 'token': 'PRIVATE'}},
            {'p': '/message/metadata/finish_details/stop_tokens/metadata/model_slug', 'v': 'gpt-secret'},
            {'p': '/message/content/parts/0', 'v': {'model_slug': 'gpt-secret'}},
            {'p': '/message/id', 'v': {'model_slug': 'gpt-secret'}}]
        result = response_metadata('\n'.join('data: ' + json.dumps(p) for p in patches))
        for item in ({'message_author_role': 'assistant'},
                     {'message_channel': 'analysis'}, {'message_status': 'finished_successfully'},
                     {'message_end_turn': True}, {'reasoning_status': 'completed'},
                     {'finished_duration_sec': 10}, {'finish_details': {'type': 'stop'}},
                     {'finish_details': {'stop_tokens_type': 'dict'}}):
            self.assertIn(item, result['metadata_records'])
        self.assertIn({'message_recipient': 'python', 'message_recipient_tool_family': 'python',
                       'message_recipient_tool_namespaced': False}, result['metadata_records'])
        self.assertNotIn('PRIVATE', json.dumps(result))
        self.assertNotIn('gpt-secret', json.dumps(result))

    def test_unknown_status_tools_and_finish_types_are_fixed_unknown_not_strings_or_hashes(self):
        value = 'PRIVATE TOOL OR STATUS'
        body = {'message': {'author': {'role': value, 'name': value},
            'recipient': value, 'channel': value, 'status': value,
            'metadata': {'reasoning_status': value, 'finish_details': {'type': value,
                'stop_tokens': value}}}}
        result = response_metadata(json.dumps(body))
        self.assertNotIn(value, json.dumps(result))
        self.assertNotIn('sha256', json.dumps(result))
        self.assertIn({'reasoning_status': 'unknown',
            'finish_details': {'type': 'unknown', 'stop_tokens_type': 'str'}}, result['metadata_records'])
        self.assertTrue(any(record.get('message_author_name') == 'unknown'
                            for record in result['metadata_records']))

    def test_duration_is_finite_nonnegative_bounded_and_not_bool(self):
        for value in (-1, 86401, True, False, math.inf, -math.inf, math.nan, 'PRIVATE', {'token': 'PRIVATE'}):
            with self.subTest(value=value):
                result = response_metadata(json.dumps({'metadata': {'finished_duration_sec': value}}))
                self.assertEqual(result['metadata_records'], [])
        for value in (0, 0.125, 86400):
            with self.subTest(value=value):
                self.assertEqual(response_metadata(json.dumps({'metadata': {'finished_duration_sec': value}})),
                                 {'metadata_records': [{'finished_duration_sec': value}]})

    def test_declared_tools_and_reasoning_content_do_not_become_execution_observations(self):
        result = response_metadata(json.dumps({'local_function_names': ['python'],
            'available_tools': [{'name': 'python', 'status': 'error'}],
            'content': {'author': {'role': 'tool', 'name': 'python'}, 'status': 'error',
                        'metadata': {'reasoning_status': 'error'}},
            'headers': {'authorization': 'PRIVATE'}, 'conversation_id': 'PRIVATE'}))
        self.assertEqual(result, {'metadata_records': []})

    def test_observed_reasoning_ended_and_builtin_recipient_are_known_but_declarations_are_not_calls(self):
        result = response_metadata(json.dumps({'message': {
            'author': {'role': 'assistant', 'name': 'local.continue_in_work'},
            'recipient': 'local.continue_in_work',
            'metadata': {'reasoning_status': 'reasoning_ended'},
            'content': {'parts': ['PRIVATE']}}}))
        self.assertIn({'reasoning_status': 'reasoning_ended'}, result['metadata_records'])
        self.assertTrue(any(record.get('message_recipient') == 'local.continue_in_work'
            and record.get('message_author_name') == 'local.continue_in_work'
            for record in result['metadata_records']))
        declared = response_metadata(json.dumps({'local_function_names': ['local.continue_in_work'],
            'available_tools': [{'name': 'local.continue_in_work'}]}))
        self.assertEqual(declared, {'metadata_records': []})
        self.assertNotIn('PRIVATE', json.dumps(result))

    def test_chunked_stream_preserves_new_enum_and_terminal_metadata_without_secret(self):
        parser = StreamMetadata()
        wire = ('data: ' + json.dumps({'message': {'author': {'role': 'assistant'},
            'status': 'finished_successfully', 'channel': 'final', 'end_turn': True,
            'content': {'parts': ['PRIVATE']}, 'metadata': {'reasoning_status': 'completed',
                'finished_duration_sec': 89, 'finish_details': {'type': 'stop', 'stop_tokens': [999]}}}})
            + '\n\ndata: [DONE]\n').encode()
        for index in range(0, len(wire), 7):
            parser.feed(wire[index:index + 7])
        self.assertTrue(parser.done)
        self.assertTrue(any(record.get('message_end_turn') is True for record in parser.records))
        self.assertTrue(any(record.get('reasoning_status') == 'completed' for record in parser.records))
        self.assertNotIn('PRIVATE', json.dumps(parser.records))
        self.assertNotIn('999', json.dumps(parser.records))

    def test_bare_work_continuation_return_is_known_but_declaring_it_is_not_activity(self):
        result = response_metadata(json.dumps({'message': {
            'author': {'role': 'tool', 'name': 'continue_in_work'}, 'recipient': 'all',
            'status': 'finished_successfully', 'content': {'content_type': 'text', 'parts': ['PRIVATE']}}}))
        record = result['metadata_records'][0]
        self.assertEqual(record['message_author_name'], 'continue_in_work')
        self.assertEqual(record['tool_content_type'], 'text')
        self.assertNotIn('tool_aggregate_status', record)
        self.assertNotIn('PRIVATE', json.dumps(result))
        self.assertEqual(response_metadata(json.dumps({'local_function_names': ['continue_in_work'],
            'available_tools': [{'name': 'python.exec', 'aggregate_result': {'status': 'success'}}]})),
            {'metadata_records': []})

    def test_fixed_python_families_classify_suffix_without_retaining_it(self):
        families = ('python', 'python_user_visible', 'python_caas',
                    'python_caas_user_visible', 'python_caas_cot')
        for family in families:
            for suffix in ('', '.exec', '.PRIVATE_SECRET'):
                with self.subTest(family=family, suffix=suffix):
                    result = response_metadata(json.dumps({'message': {
                        'author': {'role': 'tool', 'name': family + suffix},
                        'recipient': family + suffix}}))
                    record = result['metadata_records'][0]
                    for prefix in ('message_author', 'message_recipient'):
                        self.assertEqual(record[prefix + '_tool_family'], family)
                        self.assertEqual(record[prefix + '_tool_namespaced'], bool(suffix))
                    self.assertEqual(record['message_author_name'], 'unknown' if suffix else family)
                    self.assertNotIn('PRIVATE_SECRET', json.dumps(result))
                    self.assertNotIn('exec', json.dumps(result))
        for value in ('python..exec', 'python. PRIVATE', 'python.秘密', 'python.' + 'a' * 130,
                      'pythonish.exec', '', None):
            with self.subTest(value=value):
                record = response_metadata(json.dumps({'message': {
                    'author': {'role': 'tool', 'name': value}}}))['metadata_records'][0]
                self.assertNotIn('message_author_tool_family', record)
        missing = response_metadata(json.dumps({'message': {'author': {'role': 'tool'}}}))
        self.assertNotIn('message_author_name', missing['metadata_records'][0])

    def test_actual_tool_results_keep_safe_state_and_exception_presence_only(self):
        for status, expected in (('success', 'success'), ('failed_PRIVATE', 'failed'),
                                 ('cancelled', 'cancelled'), ('running', 'running'),
                                 ('PRIVATE', 'unknown'), ('failed PRIVATE', 'unknown')):
            with self.subTest(status=status):
                result = response_metadata(json.dumps({'message': {
                    'author': {'role': 'tool', 'name': 'python.exec'},
                    'status': 'finished_successfully',
                    'metadata': {'is_error': False, 'aggregate_result': {
                        'status': status, 'code': 'PRIVATE CODE',
                        'messages': [{'text': 'PRIVATE STDOUT'}],
                        'final_expression_output': 'PRIVATE RESULT',
                        'in_kernel_exception': {'name': 'PRIVATE ERROR', 'traceback': ['PRIVATE TRACEBACK']},
                        'system_exception': None}},
                    'content': {'content_type': 'error', 'traceback': 'PRIVATE TRACEBACK'}}}))
                record = result['metadata_records'][0]
                self.assertEqual(record['tool_aggregate_status'], expected)
                self.assertTrue(record['tool_in_kernel_exception_present'])
                self.assertFalse(record['tool_system_exception_present'])
                self.assertFalse(record['tool_is_error'])
                self.assertEqual(record['tool_content_type'], 'error')
                self.assertNotIn('PRIVATE', json.dumps(result))
                self.assertNotIn('sha256', json.dumps(result))
        result = response_metadata(json.dumps({'message': {'author': {'role': 'tool'},
            'metadata': {'is_error': True, 'aggregate_result': {}},
            'content': {'content_type': 'system_error'}}}))['metadata_records'][0]
        self.assertTrue(result['tool_is_error'])
        self.assertEqual(result['tool_content_type'], 'system_error')
        self.assertNotIn('tool_aggregate_status', result)
        self.assertNotIn('tool_system_exception_present', result)

    def test_unknown_tool_result_types_are_safe_and_message_completion_is_not_execution_success(self):
        result = response_metadata(json.dumps({'message': {'author': {'role': 'tool'},
            'status': 'finished_successfully', 'content': {'content_type': 'PRIVATE TYPE'},
            'metadata': {'is_error': 'PRIVATE', 'aggregate_result': {'status': {'secret': 'PRIVATE'}}}}}))
        record = result['metadata_records'][0]
        self.assertEqual(record['tool_content_type'], 'unknown')
        self.assertNotIn('tool_aggregate_status', record)
        self.assertNotIn('tool_is_error', record)
        self.assertNotIn('PRIVATE', json.dumps(result))

    def test_tool_results_require_same_message_role_not_scalar_patch_inference(self):
        metadata = {'aggregate_result': {'status': 'success', 'system_exception': {'secret': 'PRIVATE'}},
                    'is_error': True}
        bodies = [{'message': {'author': {'role': role}, 'metadata': metadata,
                               'content': {'content_type': 'error'}}}
                  for role in ('assistant', 'user', 'system', 'PRIVATE')]
        bodies += [{'message': {'metadata': metadata}}, {'metadata': metadata},
                   {'p': '/message/metadata', 'v': metadata},
                   {'p': '/message/metadata/aggregate_result/status', 'v': 'success'},
                   {'p': '/message/metadata/is_error', 'v': True},
                   {'p': '/message/content/content_type', 'v': 'error'}]
        for body in bodies:
            with self.subTest(body=body):
                result = response_metadata(json.dumps(body))
                self.assertFalse(any(key.startswith('tool_') for record in result['metadata_records']
                                     for key in record))
        stream = '\n'.join('data: ' + json.dumps(patch) for patch in (
            {'p': '/message/author/role', 'v': 'tool'},
            {'p': '/message/metadata', 'v': metadata}))
        self.assertFalse(any(key.startswith('tool_')
            for record in response_metadata(stream)['metadata_records'] for key in record))
        full_patch = response_metadata(json.dumps({'p': '/message', 'v': {
            'author': {'role': 'tool'}, 'metadata': metadata}}))
        self.assertTrue(any(record.get('tool_aggregate_status') == 'success'
                            for record in full_patch['metadata_records']))
        self.assertNotIn('PRIVATE', json.dumps(full_patch))

    def test_actual_server_ste_metadata_preserves_control_comparison_without_secrets(self):
        for metadata in (
            {'tool_name': None, 'tool_invoked': False, 'turn_use_case': 'thinking',
             'conduit_prewarmed': True, 'warmup_state': 'warm'},
            {'tool_name': 'ContainerTool', 'tool_invoked': True, 'turn_use_case': 'coding',
             'conduit_prewarmed': False, 'warmup_state': 'rewarm'},
            {'tool_name': 'ApiToolWrapper', 'tool_invoked': True}):
            with self.subTest(metadata=metadata):
                frame = {'type': 'server_ste_metadata', 'metadata': {
                    **metadata, 'code': 'PRIVATE', 'tool_output': 'PRIVATE',
                    'authorization': 'PRIVATE', 'conversation_id': 'PRIVATE'}}
                result = response_metadata('data: ' + json.dumps(frame))
                expected = {**metadata, 'tool_name': metadata['tool_name'] or 'unknown'}
                self.assertEqual(result, {'metadata_records': [{'server_ste_metadata': expected}]})
                self.assertNotIn('PRIVATE', json.dumps(result))
                self.assertFalse(any(key.startswith('tool_')
                    for record in result['metadata_records'] for key in record))

    def test_server_ste_unknown_and_missing_remain_distinct_and_booleans_are_strict(self):
        metadata = {'tool_name': 'PRIVATE_TOOL', 'turn_use_case': 'PRIVATE_CASE',
                    'warmup_state': 'PRIVATE_STATE', 'tool_invoked': 'true',
                    'conduit_prewarmed': 1}
        result = response_metadata(json.dumps({'type': 'server_ste_metadata', 'metadata': metadata}))
        self.assertEqual(result, {'metadata_records': [{'server_ste_metadata': {
            'tool_name': 'unknown', 'turn_use_case': 'unknown', 'warmup_state': 'unknown'}}]})
        self.assertNotIn('PRIVATE', json.dumps(result))
        self.assertNotIn('sha256', json.dumps(result))
        for metadata in ({}, None, [], 'PRIVATE'):
            with self.subTest(metadata=metadata):
                self.assertEqual(response_metadata(json.dumps({
                    'type': 'server_ste_metadata', 'metadata': metadata})), {'metadata_records': []})
        for value in (None, [], {}, 123, True):
            with self.subTest(value=value):
                result = response_metadata(json.dumps({'type': 'server_ste_metadata',
                    'metadata': {'tool_name': value}}))
                self.assertEqual(result['metadata_records'], [
                    {'server_ste_metadata': {'tool_name': 'unknown'}}])

    def test_server_ste_fields_require_actual_frame_not_tool_declaration_or_scalar_patch(self):
        metadata = {'tool_name': 'python', 'tool_invoked': True, 'turn_use_case': 'coding',
                    'conduit_prewarmed': False, 'warmup_state': 'rewarm'}
        bodies = [{'metadata': metadata}, {'message': {'metadata': metadata}},
                  {'type': 'OTHER', 'metadata': metadata},
                  {'available_tools': [{'type': 'server_ste_metadata', 'metadata': metadata}]},
                  {'content': {'type': 'server_ste_metadata', 'metadata': metadata}},
                  {'p': '/message/metadata', 'v': metadata},
                  {'p': '/message/metadata/tool_invoked', 'v': True}]
        for body in bodies:
            with self.subTest(body=body):
                self.assertEqual(response_metadata(json.dumps(body)), {'metadata_records': []})
        known = response_metadata(json.dumps({'type': 'server_ste_metadata', 'metadata': metadata}))
        self.assertEqual(known['metadata_records'], [{'server_ste_metadata': metadata}])
        parser = StreamMetadata()
        wire = ('data: ' + json.dumps({'type': 'server_ste_metadata', 'metadata': metadata})
                + '\n\ndata: [DONE]\n').encode()
        for index in range(0, len(wire), 5):
            parser.feed(wire[index:index + 5])
        self.assertTrue(parser.done)
        self.assertEqual(parser.records, [{'server_ste_metadata': metadata}])


class GenerationResponseAuditTests(unittest.IsolatedAsyncioTestCase):
    async def test_frontend_prepare_observation_records_policy_without_sending_anything(self):
        class Context:
            def __init__(self):
                self.listeners = {}
            def on(self, name, callback):
                self.listeners[name] = callback
        class Frame:
            page = object()
        class Request:
            method = 'POST'
            frame = Frame()
            url = 'https://chatgpt.com/backend-api/f/conversation/prepare'
            headers = {'authorization': 'PRIVATE AUTH'}
            post_data = json.dumps({'model': 'gpt-5-6-thinking', 'thinking_effort': 'max'})
        class Response:
            url = Request.url
            status = 200
            request = Request()
            body = AsyncMock(return_value=json.dumps({'force_login': True,
                'token': 'PRIVATE', 'headers': {'authorization': 'PRIVATE'}}).encode())
        context, events = Context(), []
        attach_generation_audit(context, lambda event, **fields: events.append({'event': event, **fields}))
        context.listeners['request'](Request())
        await context.listeners['response'](Response())
        observed = next(item for item in events if item['event'] == 'generation_response_metadata')
        self.assertEqual(observed['endpoint'], Request.url.removeprefix('https://chatgpt.com'))
        self.assertEqual(observed['endpoint_kind'], 'prepare')
        self.assertEqual(observed['metadata_records'], [{'force_login': True}])
        self.assertNotIn('PRIVATE', json.dumps(events))
        # This fake context has no route/send/post/retry API. Observation only
        # registers callbacks and reads this already-existing response.
        self.assertEqual(set(context.listeners), {'request', 'response'})

    async def test_missing_sse_body_keeps_status_and_page_correlation(self):
        class Context:
            def __init__(self):
                self.listeners = {}
            def on(self, name, callback):
                self.listeners[name] = callback
        class Frame:
            page = object()
        class Request:
            method = 'POST'
            frame = Frame()
        class Response:
            url = 'https://chatgpt.com/backend-api/f/conversation'
            status = 200
            request = Request()
            body = AsyncMock(side_effect=RuntimeError('SECRET body failure detail'))
        context = Context()
        events = []
        attach_generation_audit(context, lambda event, **fields: events.append({'event': event, **fields}))
        await context.listeners['response'](Response())
        started, failed = events[-2:]
        self.assertEqual(started['event'], 'generation_response_started')
        self.assertEqual(started['status'], 200)
        self.assertEqual(started['request_observer_id'], failed['request_observer_id'])
        self.assertEqual(started['page_object_id'], id(Frame.page))
        self.assertFalse(failed['body_available'])
        self.assertNotIn('SECRET', json.dumps(events))


if __name__ == '__main__':
    unittest.main()
