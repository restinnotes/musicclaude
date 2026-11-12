"""Passive allowlisted metadata; never stores credentials or prompt text."""
import asyncio
import base64
import hashlib
import json
import math
import os
import re
from collections import deque
from urllib.parse import urlsplit

EFFORTS = {'none', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max',
           'ultra', 'standard', 'extended', 'extra_high', 'extra-high', 'pro'}
MODEL_FIELDS = ('model', 'model_slug', 'default_model_slug')
EFFORT_FIELDS = ('thinking_effort', 'reasoning_effort', 'effort')
BOOLEAN_FIELDS = ('history_and_training_disabled', 'is_do_not_remember',
                  'temporary_chat_requests_personalization', 'force_paragen')
SESSION_CONTEXT_COOKIE_NAMES = frozenset(('__Secure-oai-is', 'oai-client-auth-info',
    'oai-client-session-epoch', '__oailb', '_account'))
REASONING_STATUSES = frozenset(('thinking', 'in_progress', 'running', 'done', 'completed',
    'finished', 'finished_successfully', 'finished_failed', 'error', 'paused',
    'stopped', 'cancelled', 'canceled', 'reasoning_ended'))
MESSAGE_STATUSES = frozenset(('in_progress', 'finished_successfully', 'finished_partial',
    'finished_failed', 'completed', 'error', 'paused', 'cancelled', 'canceled'))
MESSAGE_CHANNELS = frozenset(('analysis', 'final', 'commentary', 'summary'))
MESSAGE_ROLES = frozenset(('system', 'developer', 'user', 'assistant', 'tool'))
TOOL_NAMES = frozenset(('python', 'python_user_visible', 'browser', 'web', 'web.run',
    'file_search', 'api_tool', 'api_tool.call', 'computer', 'automations', 'image_gen',
    'local.continue_in_work', 'continue_in_work'))
PYTHON_TOOL_FAMILIES = frozenset(('python', 'python_user_visible', 'python_caas',
    'python_caas_user_visible', 'python_caas_cot'))
TOOL_NAMES |= PYTHON_TOOL_FAMILIES
TOOL_CONTENT_TYPES = frozenset(('text', 'error', 'system_error'))
STE_TOOL_NAMES = TOOL_NAMES | {'ContainerTool', 'ApiToolWrapper'}
STE_TURN_USE_CASES = frozenset(('thinking', 'coding'))
STE_WARMUP_STATES = frozenset(('warm', 'rewarm'))
UA_HINT_HEADERS = frozenset(('sec-ch-ua', 'sec-ch-ua-mobile', 'sec-ch-ua-platform',
    'sec-ch-ua-arch', 'sec-ch-ua-bitness', 'sec-ch-ua-full-version',
    'sec-ch-ua-full-version-list', 'sec-ch-ua-platform-version',
    'sec-ch-ua-model', 'sec-ch-ua-wow64', 'sec-ch-ua-form-factors'))
FINISH_TYPES = frozenset(('stop', 'max_tokens', 'length', 'interrupted', 'content_filter',
    'tool_calls', 'error', 'timeout', 'cancelled', 'canceled'))

def wire_cookie_metadata(event):
    """Inspect actual sent cookies and client context without persisting values."""
    headers = {k.lower(): v for k, v in event.get('headers', {}).items() if isinstance(k, str)}
    accepted = [item.get('cookie', {}) for item in event.get('associatedCookies', [])
                if not item.get('blockedReasons')]
    devices = {c.get('value') for c in accepted if c.get('name') == 'oai-did'
               and isinstance(c.get('value'), str)}
    device = next(iter(devices)) if len(devices) == 1 else None
    canonical_device = headers.get('oai-did')
    cookie_header = headers.get('cookie', '')
    result = {'sent_cookie_count': len(accepted),
        'sent_auth_cookie_count': sum(c.get('name', '').startswith('__Secure-next-auth.session-token') for c in accepted),
        'sent_device_cookie_sha256': hashlib.sha256(device.encode()).hexdigest() if isinstance(device, str) else None,
        'actual_oai_did_header_sha256': hashlib.sha256(canonical_device.encode()).hexdigest()
            if isinstance(canonical_device, str) and canonical_device else None,
        'oai_did_header_matches_sent_device_cookie': canonical_device == device
            if isinstance(canonical_device, str) and canonical_device and device is not None else None,
        'sent_device_cookie_conflict': len(devices) > 1,
        'cookie_header_bytes': len(cookie_header.encode()) if isinstance(cookie_header, str) else None,
        'sent_context_cookie_names': sorted({c.get('name') for c in accepted
            if c.get('name') in SESSION_CONTEXT_COOKIE_NAMES}),
        'header_names': sorted(k for k in headers if re.fullmatch(r'[a-z0-9:_-]{1,80}', k))[:128]}
    allowed = ('originator', 'x-openai-codex-window-type', 'x-openai-web-frontend',
        'x-oai-mcp-form-version', 'oai-language', 'accept-language', 'sec-ch-ua-platform',
        'sec-ch-ua-platform-version', 'sec-ch-ua', 'user-agent',
        'sec-ch-ua-arch', 'sec-ch-ua-bitness', 'sec-ch-ua-full-version',
        'sec-ch-ua-full-version-list', 'sec-ch-ua-model', 'sec-ch-ua-wow64',
        'sec-ch-ua-form-factors')
    recognized = {'Codex Browser', 'ChatGPT', 'chatgpt', 'codex_webview', 'browser',
        'zh-CN', 'en-US', '2', '"Windows"', '"Linux"', '"macOS"'}
    result['client_header_context'] = {k: v if v in recognized else
        {'characters': len(v), 'sha256': hashlib.sha256(v.encode()).hexdigest()}
        for k in allowed if isinstance((v := headers.get(k)), str) and len(v) <= 512}
    return result


def safe_model(value):
    if isinstance(value, str) and re.fullmatch(r'(?:gpt[-.][A-Za-z0-9._-]+|o[1-9][A-Za-z0-9._-]*|auto)', value) and len(value) <= 100:
        return value


def selected_fields(data):
    if not isinstance(data, dict):
        return {}
    result = {}
    for key in MODEL_FIELDS:
        value = safe_model(data.get(key))
        if value is not None:
            result[key] = value
    for key in EFFORT_FIELDS:
        value = data.get(key)
        if isinstance(value, str) and value in EFFORTS:
            result[key] = value
    for key in BOOLEAN_FIELDS:
        if isinstance(data.get(key), bool):
            result[key] = data[key]
    for key in ('reasoning_time_ms', 'thinking_time_ms'):
        value = data.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool) and 0 <= value <= 86400000:
            result[key] = value
    return result


def request_metadata(body):
    try:
        data = json.loads(body)
    except (ValueError, TypeError):
        return {'parse_error': True}
    if not isinstance(data, dict):
        return {'parse_error': True}
    result = selected_fields(data)
    browser_context = data.get('browser_context')
    if result or 'browser_context' in data:
        result['browser_context_present'] = 'browser_context' in data
        result['browser_context_is_object'] = isinstance(browser_context, dict)
        if isinstance(browser_context, dict):
            instance = browser_context.get('instance_id')
            result['browser_context_instance_id_present'] = 'instance_id' in browser_context
            result['browser_context_instance_id_nonempty_string'] = isinstance(instance, str) and bool(instance)
    # Browser context can explain differences even when model/effort match.
    # Store structure and bounded scalars only; arbitrary strings are hashed.
    def shape(value, depth=0):
        if depth > 5:
            return {'type': type(value).__name__}
        if isinstance(value, dict):
            return {key: shape(child, depth + 1) for key, child in list(value.items())[:64]
                    if isinstance(key, str) and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,79}', key)
                    and not re.search(r'(?i)token|secret|authorization|cookie|password|content|snapshot|(?:^|_)id$|time', key)}
        if isinstance(value, list):
            return {'count': len(value), 'items': [shape(child, depth + 1) for child in value[:16]]}
        if isinstance(value, bool) or value is None:
            return value
        if isinstance(value, (int, float)) and -1000000 <= value <= 1000000:
            return value
        if isinstance(value, str):
            return {'type': 'str', 'characters': len(value), 'sha256': hashlib.sha256(value.encode()).hexdigest()}
        return {'type': type(value).__name__}
    context_shape = {key: shape(data[key]) for key in ('browser_context', 'client_contextual_info',
                     'supported_encodings', 'local_function_names', 'turn_attribution') if key in data}
    if context_shape:
        result['context_shape'] = context_shape
    offset = data.get('timezone_offset_min')
    if isinstance(offset, (int, float)) and -840 <= offset <= 840:
        result['timezone_offset_min'] = offset
    zone = data.get('timezone')
    if isinstance(zone, str) and re.fullmatch(r'[A-Za-z_]+/[A-Za-z_]+(?:/[A-Za-z_]+)?', zone):
        result['timezone'] = zone
    default = data.get('requested_default_model')
    if isinstance(default, dict):
        result['requested_default_model'] = selected_fields(default)
    elif safe_model(default):
        result['requested_default_model'] = default
    if isinstance(data.get('conversation_mode'), dict):
        kind = data['conversation_mode'].get('kind')
        if kind in {'primary_assistant', 'temporary', 'default'}:
            result['conversation_mode_kind'] = kind
    messages = data.get('messages')
    if isinstance(messages, list):
        result['message_count'] = len(messages)
        texts = []
        for message in messages:
            if not isinstance(message, dict):
                continue
            content = message.get('content')
            if isinstance(content, dict) and content.get('content_type') == 'text':
                parts = content.get('parts')
                if isinstance(parts, list):
                    texts.extend(part for part in parts if isinstance(part, str))
        if texts:
            text = '\n'.join(texts)
            result['text_characters'] = len(text)
            result['text_sha256'] = hashlib.sha256(text.encode()).hexdigest()
    return result


def response_metadata(body):
    """Parse JSON/SSE metadata and JSON patches, skipping every content branch."""
    found = []

    def visit(node, depth=0, is_message=False):
        if depth > 12:
            return
        if isinstance(node, list):
            for item in node:
                visit(item, depth + 1)
        elif isinstance(node, dict):
            path = node.get('p', node.get('path', ''))
            if isinstance(path, str) and re.search(r'/content(?:/|$)', path):
                return
            if isinstance(path, str) and path.startswith('/'):
                value = node.get('v', node.get('value'))
                fields = patch_response_fields(path, value)
                if fields and fields not in found:
                    found.append(fields)
                # Only these structural patch containers may be walked. Scalar
                # leaf values (including stop_tokens) are never treated as JSON
                # envelopes or metadata, even if maliciously shaped as objects.
                if path == '/message':
                    visit(value, depth + 1, is_message=True)
                elif path == '/message/metadata':
                    visit(value, depth + 1)
                return
            fields = response_fields(node)
            if node.get('type') == 'server_ste_metadata':
                ste = server_ste_fields(node.get('metadata'))
                if ste:
                    fields['server_ste_metadata'] = ste
            if is_message or isinstance(node.get('author'), dict):
                fields.update(message_fields(node))
            if fields and fields not in found:
                found.append(fields)
            for key in ('message', 'metadata', 'v', 'value', 'data', 'response'):
                child = node.get(key)
                if isinstance(child, (dict, list)):
                    visit(child, depth + 1, is_message=key == 'message')

    try:
        visit(json.loads(body))
    except (ValueError, TypeError):
        for line in body.splitlines():
            if not line.startswith('data:'):
                continue
            try:
                visit(json.loads(line[5:].strip()))
            except ValueError:
                pass
    return {'metadata_records': found}


def finite_enum(value, allowed):
    # Unknown strings are represented by one literal, never logged or hashed.
    if isinstance(value, str):
        return value if value in allowed else 'unknown'


def server_ste_fields(metadata):
    """Server-declared state only; tool_invoked does not prove success."""
    if not isinstance(metadata, dict):
        return {}
    result = {}
    for key, allowed in (('tool_name', STE_TOOL_NAMES),
                         ('turn_use_case', STE_TURN_USE_CASES),
                         ('warmup_state', STE_WARMUP_STATES)):
        if key in metadata:
            result[key] = finite_enum(metadata[key], allowed) or 'unknown'
    for key in ('tool_invoked', 'conduit_prewarmed'):
        if isinstance(metadata.get(key), bool):
            result[key] = metadata[key]
    return result


def finish_fields(value):
    if not isinstance(value, dict):
        return {}
    result = {}
    kind = finite_enum(value.get('type'), FINISH_TYPES)
    if kind is not None:
        result['type'] = kind
    if 'stop_tokens' in value:
        tokens = value['stop_tokens']
        # No token values, lengths, hashes, or child traversal.
        result['stop_tokens_type'] = ('null' if tokens is None else
            type(tokens).__name__ if type(tokens) in (bool, int, float, str, list, dict) else 'unknown')
    return result


def response_fields(data):
    if not isinstance(data, dict):
        return {}
    result = selected_fields(data)
    status = finite_enum(data.get('reasoning_status'), REASONING_STATUSES)
    if status is not None:
        result['reasoning_status'] = status
    duration = data.get('finished_duration_sec')
    if (type(duration) in (int, float) and 0 <= duration <= 86400
            and math.isfinite(duration)):
        result['finished_duration_sec'] = duration
    if isinstance(data.get('force_login'), bool):
        result['force_login'] = data['force_login']
    finish = finish_fields(data.get('finish_details'))
    if finish:
        result['finish_details'] = finish
    return result


def message_fields(data):
    """Message observations, never proof that a declared tool was executed."""
    if not isinstance(data, dict):
        return {}
    result = {}
    author = data.get('author')
    if isinstance(author, dict):
        role = finite_enum(author.get('role'), MESSAGE_ROLES)
        if role is not None:
            result['message_author_role'] = role
        name = finite_enum(author.get('name'), TOOL_NAMES)
        if name is not None:
            result['message_author_name'] = name
            result['message_author_name_present'] = bool(author['name'])
        result.update(python_tool_fields(author.get('name'), 'message_author'))
    for key, allowed in (('recipient', TOOL_NAMES | {'all'}),
                         ('channel', MESSAGE_CHANNELS), ('status', MESSAGE_STATUSES)):
        value = finite_enum(data.get(key), allowed)
        if value is not None:
            result['message_' + key] = value
    result.update(python_tool_fields(data.get('recipient'), 'message_recipient'))
    if isinstance(data.get('end_turn'), bool):
        result['message_end_turn'] = data['end_turn']
    # Only a message carrying its own explicit tool role authorizes these
    # observations. Independent metadata/scalar patches cannot inherit a role.
    if isinstance(author, dict) and author.get('role') == 'tool':
        result.update(tool_result_fields(data))
    return result


def python_tool_fields(value, prefix):
    """Classify the five first-party roots, never retain namespace suffixes."""
    if (not isinstance(value, str) or len(value) > 128
            or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*', value)):
        return {}
    root = value.split('.', 1)[0]
    if root not in PYTHON_TOOL_FAMILIES:
        return {}
    return {prefix + '_tool_family': root, prefix + '_tool_namespaced': '.' in value}


def tool_result_fields(message):
    """Read only result state and presence; never code/output/exception text."""
    result = {}
    metadata = message.get('metadata')
    if isinstance(metadata, dict):
        if isinstance(metadata.get('is_error'), bool):
            result['tool_is_error'] = metadata['is_error']
        aggregate = metadata.get('aggregate_result')
        if isinstance(aggregate, dict):
            status = aggregate.get('status')
            if isinstance(status, str):
                category = status if status in {'success', 'running', 'cancelled'} else 'unknown'
                if (len(status) <= 64 and re.fullmatch(r'[A-Za-z0-9_.-]+', status)
                        and status.startswith('failed')):
                    category = 'failed'
                result['tool_aggregate_status'] = category
            for key in ('in_kernel_exception', 'system_exception'):
                if key in aggregate:
                    result['tool_' + key + '_present'] = aggregate[key] is not None
    content = message.get('content')
    if isinstance(content, dict):
        kind = finite_enum(content.get('content_type'), TOOL_CONTENT_TYPES)
        if kind is not None:
            result['tool_content_type'] = kind
    return result


def patch_response_fields(path, value):
    if '/stop_tokens/' in path:
        return {}  # Never inspect any descendant of a token container.
    if path == '/message':
        return message_fields(value)
    if path == '/message/author':
        return message_fields({'author': value})
    for leaf in ('role', 'name'):
        if path == '/message/author/' + leaf:
            return message_fields({'author': {leaf: value}})
    for leaf in ('recipient', 'channel', 'status', 'end_turn'):
        if path == '/message/' + leaf:
            return message_fields({leaf: value})
    if path == '/message/metadata':
        return response_fields(value)
    if path.endswith('/metadata/finish_details'):
        finish = finish_fields(value)
        return {'finish_details': finish} if finish else {}
    for leaf in ('type', 'stop_tokens'):
        if path.endswith('/metadata/finish_details/' + leaf):
            finish = finish_fields({leaf: value})
            return {'finish_details': finish} if finish else {}
    if '/metadata/' in path:
        leaf = path.rsplit('/', 1)[-1]
        return response_fields({leaf: value})
    return {}


def generation_endpoint(url):
    parsed = urlsplit(url)
    if parsed.hostname != 'chatgpt.com':
        return None
    if parsed.path in {'/backend-api/conversation', '/backend-api/f/conversation',
                       '/backend-api/conversation/init', '/backend-api/conversation/prepare',
                       '/backend-api/f/conversation/prepare'}:
        return parsed.path


class StreamMetadata:
    """Bounded SSE line parser; discards text immediately after allowlisting."""
    def __init__(self, max_bytes=8 * 1024 * 1024, max_line=128 * 1024):
        self.pending = b''
        self.bytes_seen = 0
        self.max_bytes, self.max_line = max_bytes, max_line
        self.records = []
        self.truncated = False
        self.dropping_line = False
        self.done = False
        self.oversized_lines_dropped = 0
        self.metadata_record_limit_reached = False
        self.early_buffer_limit_reached = False
        self.observation_error = False

    def completeness_fields(self):
        lost = (self.truncated or self.oversized_lines_dropped > 0
                or self.metadata_record_limit_reached or self.early_buffer_limit_reached
                or self.observation_error)
        return {'truncated': bool(lost), 'oversized_lines_dropped': self.oversized_lines_dropped,
            'metadata_record_limit_reached': self.metadata_record_limit_reached,
            'early_buffer_limit_reached': self.early_buffer_limit_reached,
            'metadata_observation_complete': self.done and not lost
                and not self.dropping_line and not self.pending.strip()}

    def feed(self, chunk):
        self.bytes_seen += len(chunk)
        if self.truncated:
            return []
        if self.bytes_seen > self.max_bytes:
            self.pending = b''
            self.truncated = True
            return []
        new = []
        for segment in chunk.splitlines(keepends=True):
            ended = segment.endswith(b'\n')
            if not self.dropping_line:
                if len(self.pending) + len(segment) > self.max_line:
                    self.pending = b''
                    self.dropping_line = True
                    self.oversized_lines_dropped += 1
                else:
                    self.pending += segment
            if ended:
                if not self.dropping_line:
                    line = self.pending.decode('utf-8', errors='replace').strip()
                    if line == 'data: [DONE]':
                        self.done = True
                    for record in response_metadata(line)['metadata_records']:
                        if record not in self.records:
                            if len(self.records) < 128:
                                self.records.append(record)
                                new.append(record)
                            else:
                                self.metadata_record_limit_reached = True
                self.pending = b''
                self.dropping_line = False
        return new


async def attach_page_stream_audit(context, page, emit):
    """CDP observes response chunks without intercepting or replaying traffic."""
    try:
        session = await context.new_cdp_session(page)
        tracked = {}
        early_cookie_metadata = {}

        def on_request(event):
            request = event.get('request', {})
            endpoint = generation_endpoint(request.get('url', ''))
            if request.get('method') == 'POST' and endpoint in {'/backend-api/conversation', '/backend-api/f/conversation'}:
                tracked[event['requestId']] = {'parser': StreamMetadata(), 'early': [], 'enabled': False,
                    'envelope': {'source': 'cdp', 'endpoint': endpoint, 'page_object_id': id(page),
                                 'cdp_request_id': event['requestId'], 'wire_epoch': event.get('wallTime'),
                                 'metadata': request_metadata(request.get('postData', '{}'))}}
                emit('generation_wire_request', **tracked[event['requestId']]['envelope'])
                cookie_metadata = early_cookie_metadata.pop(event['requestId'], None)
                if cookie_metadata is not None:
                    emit('generation_wire_cookie_metadata', **tracked[event['requestId']]['envelope'], **cookie_metadata)

        def on_extra_request(event):
            metadata = wire_cookie_metadata(event)
            entry = tracked.get(event.get('requestId'))
            if entry:
                emit('generation_wire_cookie_metadata', **entry['envelope'], **metadata)
            else:
                early_cookie_metadata[event.get('requestId')] = metadata
                while len(early_cookie_metadata) > 128:
                    early_cookie_metadata.pop(next(iter(early_cookie_metadata)))

        def consume(entry, data):
            new = entry['parser'].feed(data)
            if new:
                emit('generation_stream_metadata', **entry['envelope'], metadata_records=new)

        async def on_response(event):
            entry = tracked.get(event.get('requestId'))
            if entry is None:
                return
            response = event.get('response', {})
            entry['envelope']['status'] = response.get('status')
            entry['envelope']['protocol'] = response.get('protocol')
            try:
                result = await session.send('Network.streamResourceContent', {'requestId': event['requestId']})
                consume(entry, base64.b64decode(result.get('bufferedData', '')))
                entry['enabled'] = True
                for data in entry['early']:
                    consume(entry, data)
                entry['early'].clear()
                emit('generation_stream_enabled', **entry['envelope'])
            except Exception as error:
                entry['parser'].observation_error = True
                entry['early'].clear()
                emit('generation_stream_error', **entry['envelope'], exception_type=type(error).__name__)

        def on_data(event):
            entry = tracked.get(event.get('requestId'))
            data = event.get('data')
            if entry is None or not data:
                return
            try:
                chunk = base64.b64decode(data)
                if entry['enabled']:
                    consume(entry, chunk)
                elif sum(map(len, entry['early'])) + len(chunk) <= 256 * 1024:
                    entry['early'].append(chunk)
                else:
                    entry['parser'].early_buffer_limit_reached = True
            except (ValueError, TypeError):
                entry['parser'].observation_error = True

        def on_finish(event):
            early_cookie_metadata.pop(event.get('requestId'), None)
            entry = tracked.pop(event.get('requestId'), None)
            if entry:
                parser = entry['parser']
                emit('generation_stream_finished', **entry['envelope'], bytes_observed=parser.bytes_seen,
                     metadata_records=parser.records, sse_done=parser.done, **parser.completeness_fields(),
                     failed='errorText' in event and not parser.done,
                     canceled=bool(event.get('canceled', False)),
                     network_canceled_after_sse_done=parser.done and bool(event.get('canceled', False)))

        session.on('Network.requestWillBeSent', on_request)
        session.on('Network.requestWillBeSentExtraInfo', on_extra_request)
        session.on('Network.responseReceived', on_response)
        session.on('Network.dataReceived', on_data)
        session.on('Network.loadingFinished', on_finish)
        session.on('Network.loadingFailed', on_finish)
        await session.send('Network.enable', {'maxTotalBufferSize': 1024 * 1024, 'maxResourceBufferSize': 256 * 1024})
        emit('generation_stream_audit_attached', source='cdp', page_object_id=id(page))
    except Exception as error:
        emit('generation_stream_attach_error', source='cdp', page_object_id=id(page), exception_type=type(error).__name__)


ASSET_PAGE_BYTES = 8 * 1024 * 1024
ASSET_PROCESS_BYTES = 32 * 1024 * 1024
ASSET_PAGE_RECORDS = 64
ASSET_PROCESS_RECORDS = 256
ASSET_MAX_PAGES = 32
ASSET_MAX_PENDING = 64
ASSET_MAX_TASKS = 2
ASSET_BODY_TIMEOUT = 5
_ASSET_BASENAME = re.compile(r'(?:[0-9]{1,12}\.[A-Za-z0-9_-]{4,96}|(?:entry\.client|main|app|index|manifest)[.-][A-Za-z0-9_-]{4,96})\.js')


def _asset_basename(url):
    try:
        target = urlsplit(url)
        if (target.scheme != 'https' or target.hostname not in ('chatgpt.com','cdn.oaistatic.com')
                or target.username is not None or target.password is not None
                or target.port not in (None,443) or target.path.rsplit('/',1)[0] not in ('/assets','/cdn/assets')):
            return None
        name = target.path.rsplit('/',1)[-1]
        return name if _ASSET_BASENAME.fullmatch(name) else None
    except (TypeError,ValueError):
        return None


class _AssetBudget:
    """One process-wide bounded queue; at most two response.body() calls.

    Bounds apply to accepted/hashed decoded bytes. The driver body API returns
    one complete buffer before its length can be checked; no claim is made that
    an oversized driver's transient allocation was measured or stream-limited.
    """
    def __init__(self):
        self.remaining = ASSET_PROCESS_BYTES
        self.records = 0
        self.pages = {}
        self.pending = deque()
        self.tasks = set()
        self.owners = {}

    def kick(self):
        while self.pending and len(self.tasks) < ASSET_MAX_TASKS:
            task = asyncio.create_task(self.drain())
            self.tasks.add(task)
            task.add_done_callback(self.finished)

    def finished(self, task):
        self.tasks.discard(task)
        self.owners.pop(task,None)
        if not task.cancelled():
            try:task.exception()
            except Exception:pass
        if self.pending:
            self.kick()

    async def drain(self):
        while self.pending:
            collector,response,page_state,row = self.pending.popleft()
            if collector.closed:
                continue
            task = asyncio.current_task()
            self.owners[task] = collector
            try:
                await collector.read(response,page_state,row)
            finally:
                response = None
                self.owners.pop(task,None)


_asset_budget = _AssetBudget()


class _ForensicAssets:
    def __init__(self, context, emit, budget):
        self.emit,self.budget,self.closed = emit,budget,False
        self.limits_emitted = set()
        self.observation_lost = False
        context.on('response',self.on_response)
        context.on('close',self.close)
        self.record('forensic_asset_collector_attached',body_saved=False,
            per_page_byte_limit=ASSET_PAGE_BYTES,process_byte_limit=ASSET_PROCESS_BYTES,
            maximum_active_tasks=ASSET_MAX_TASKS,maximum_pending_responses=ASSET_MAX_PENDING,
            maximum_page_records=ASSET_PAGE_RECORDS,maximum_process_records=ASSET_PROCESS_RECORDS,
            hash_scope='received_decoded_response_body',executed_bytecode_verified=False,
            budget_scope='accepted_and_hashed_decoded_bytes')

    def record(self, event, **fields):
        if event in ('forensic_frontend_asset','forensic_asset_observation_limit') and fields.get('observation_complete') is False:
            self.observation_lost = True
        try:self.emit(event,**fields)
        except Exception:self.observation_lost = True  # Optional logging failure cannot affect the page.

    def limit(self, code):
        if code not in self.limits_emitted:
            self.limits_emitted.add(code)
            self.record('forensic_asset_observation_limit',error_code=code,
                        observation_complete=False,body_saved=False)

    def on_response(self, response):
        if self.closed:
            return
        try:
            name = _asset_basename(response.url)
            if name is None or response.request.method != 'GET':
                return
            if self.budget.records >= ASSET_PROCESS_RECORDS:
                self.limit('process_record_limit');return
            try:page = response.request.frame.page
            except Exception:page = None
            identifier = id(page) if page is not None else None
            row = {'basename':name,'page_object_id':identifier,
                'status':response.status if type(response.status) is int else None,
                'hash_scope':'received_decoded_response_body','body_saved':False,
                'executed_bytecode_verified':False,'body_sha256':None,'body_bytes':None,
                'body_observed':False,'observation_complete':False}
            for attribute,key in (('from_service_worker','from_service_worker'),('from_disk_cache','from_disk_cache')):
                value = getattr(response,attribute,None)
                if type(value) is bool:row[key]=value
            if identifier not in self.budget.pages:
                if len(self.budget.pages) >= ASSET_MAX_PAGES:
                    self.limit('page_limit');return
                self.budget.pages[identifier] = {'remaining':ASSET_PAGE_BYTES,'records':0,'lock':asyncio.Lock()}
            state = self.budget.pages[identifier]
            if state['records'] >= ASSET_PAGE_RECORDS:
                self.limit('page_record_limit');return
            state['records'] += 1
            self.budget.records += 1
            if page is None:
                self.record('forensic_frontend_asset',**row,error_code='page_unattributed');return
            if row['status'] != 200:
                self.record('forensic_frontend_asset',**row,error_code='response_not_200');return
            if len(self.budget.pending) >= ASSET_MAX_PENDING:
                self.record('forensic_frontend_asset',**row,error_code='pending_limit');return
            self.budget.pending.append((self,response,state,row))
            self.budget.kick()
        except Exception:
            self.limit('asset_observation_failed')

    async def read(self, response, state, row):
        raw = None
        quota = 0
        reserved = False
        charged = 0
        try:
            async with state['lock']:
                if self.closed:return
                quota = min(state['remaining'],self.budget.remaining)
                if quota <= 0:
                    self.record('forensic_frontend_asset',**row,error_code='body_budget_exhausted');return
                headers = getattr(response,'headers',{})
                content_type = next((value for key,value in headers.items() if key.lower() == 'content-type'),None)
                if not isinstance(content_type,str) or content_type.split(';',1)[0].strip().lower() not in (
                        'text/javascript','application/javascript','application/x-javascript'):
                    self.record('forensic_frontend_asset',**row,error_code='javascript_type_unverified');return
                length = next((value for key,value in headers.items() if key.lower() == 'content-length'),None)
                if isinstance(length,str) and length.isdigit() and len(length) <= 16 and int(length) > quota:
                    self.record('forensic_frontend_asset',**row,error_code='declared_body_over_budget');return
                state['remaining'] -= quota
                self.budget.remaining -= quota
                reserved = True
                raw = await asyncio.wait_for(response.body(),timeout=ASSET_BODY_TIMEOUT)
                if not isinstance(raw,bytes) or not raw:
                    self.record('forensic_frontend_asset',**row,error_code='body_unavailable');return
                if len(raw) > quota:
                    charged = quota
                    self.record('forensic_frontend_asset',**row,error_code='decoded_body_over_budget');return
                charged = len(raw)
                self.record('forensic_frontend_asset',**{**row,'body_sha256':hashlib.sha256(raw).hexdigest(),
                    'body_bytes':len(raw),'body_observed':True,'observation_complete':True})
        except asyncio.CancelledError:
            self.record('forensic_frontend_asset',**row,error_code='body_read_cancelled')
            raise
        except Exception:
            if not self.closed:
                self.record('forensic_frontend_asset',**row,error_code='body_read_unavailable')
        finally:
            if reserved:
                state['remaining'] += quota-charged
                self.budget.remaining += quota-charged
            raw = response = None

    def close(self, *unused):
        if self.closed:return
        self.closed = True
        unread = sum(item[0] is self for item in self.budget.pending)
        self.budget.pending = deque(item for item in self.budget.pending if item[0] is not self)
        active = 0
        for task,owner in list(self.budget.owners.items()):
            if owner is self:
                active += 1
                task.cancel()
        self.record('forensic_asset_collector_closed',unread_pending_responses=unread,
            active_tasks_cancelled=active,observation_complete=not self.observation_lost and unread == 0 and active == 0,
            body_saved=False)


def attach_generation_audit(context, emit):
    """Observe the website's existing traffic; never sends or changes a request."""
    def page_identifier(request):
        try:
            return id(request.frame.page)
        except Exception:
            return None

    def on_request(request):
        try:
            endpoint = generation_endpoint(request.url)
            if request.method != 'POST' or endpoint is None:
                return
            headers = request.headers
            scope = headers.get('chatgpt-account-id')
            scope_hash = hashlib.sha256(scope.encode()).hexdigest() if isinstance(scope, str) else None
            device = headers.get('oai-device-id')
            device_hash = hashlib.sha256(device.encode()).hexdigest() if isinstance(device, str) else None
            emit('generation_request_metadata', source='backend', endpoint=endpoint,
                 request_observer_id=id(request), page_object_id=page_identifier(request), workspace_header_sha256=scope_hash,
                 device_header_sha256=device_hash,
                 metadata=request_metadata(request.post_data or '{}'))
        except Exception as error:
            emit('generation_observation_error', source='backend', phase='request', exception_type=type(error).__name__)

    async def on_response(response):
        on_client_hint_response(response)
        endpoint = generation_endpoint(response.url)
        if endpoint is None or response.request.method != 'POST':
            return
        envelope = {'source': 'backend', 'endpoint': endpoint, 'status': response.status,
                    'endpoint_kind': ('prepare' if endpoint.endswith('/prepare') else
                                      'init' if endpoint.endswith('/init') else 'generation'),
                    'request_observer_id': id(response.request),
                    'page_object_id': page_identifier(response.request)}
        emit('generation_response_started', **envelope)
        try:
            body = await response.body()
            if len(body) > 8 * 1024 * 1024:
                emit('generation_response_metadata', source='backend', endpoint=endpoint,
                     status=response.status, request_observer_id=id(response.request), page_object_id=page_identifier(response.request), body_too_large=True)
                return
            metadata = response_metadata(body.decode('utf-8', errors='replace'))
            emit('generation_response_metadata', **envelope, **metadata)
        except Exception as error:
            emit('generation_observation_error', **envelope, phase='response',
                 body_available=False, exception_type=type(error).__name__)

    context.on('request', on_request)
    context.on('response', on_response)
    def on_client_hint_response(response):
        # Only headers already received by this browser; no re-fetch or mutation.
        try:
            parsed = urlsplit(response.url)
            if parsed.scheme != 'https' or parsed.hostname != 'chatgpt.com':
                return
            endpoint = generation_endpoint(response.url)
            if response.request.resource_type != 'document' and endpoint is None:
                return
            headers = {k.lower(): v for k,v in response.headers.items()}
            hints = lambda name: sorted({field.strip().lower() for field in
                str(headers.get(name, '')).split(',') if field.strip().lower() in UA_HINT_HEADERS})
            emit('client_hint_negotiation_observed', source='backend',
                page_object_id=page_identifier(response.request),
                document_response=response.request.resource_type == 'document',
                status=response.status, accept_ch_present='accept-ch' in headers,
                requested_ua_hint_headers=hints('accept-ch'),
                critical_ua_hint_headers=hints('critical-ch'),
                arbitrary_response_headers_saved=False)
        except Exception:
            emit('client_hint_observation_unavailable', source='backend')
    if os.environ.get('MIMICGATE_FORENSIC_ASSETS') == '1':
        _ForensicAssets(context,emit,_asset_budget)
    if hasattr(context, 'new_cdp_session'):
        tasks = set()
        def attach_page(page):
            task = asyncio.create_task(attach_page_stream_audit(context, page, emit))
            tasks.add(task)
            task.add_done_callback(tasks.discard)
        for page in context.pages:
            attach_page(page)
        context.on('page', attach_page)
    emit('generation_audit_attached', source='backend', content_saved=False, auth_headers_saved=False)
