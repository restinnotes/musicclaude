"""Passive allowlisted metadata; never stores credentials or prompt text."""
import asyncio
import base64
import hashlib
import json
import re
from urllib.parse import urlsplit

EFFORTS = {'none', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max',
           'ultra', 'standard', 'extended', 'extra_high', 'extra-high', 'pro'}
MODEL_FIELDS = ('model', 'model_slug', 'default_model_slug')
EFFORT_FIELDS = ('thinking_effort', 'reasoning_effort', 'effort')
BOOLEAN_FIELDS = ('history_and_training_disabled', 'is_do_not_remember',
                  'temporary_chat_requests_personalization', 'force_paragen')
SESSION_CONTEXT_COOKIE_NAMES = frozenset(('__Secure-oai-is', 'oai-client-auth-info',
    'oai-client-session-epoch', '__oailb', '_account'))

def wire_cookie_metadata(event):
    """Inspect actual sent cookies and client context without persisting values."""
    headers = {k.lower(): v for k, v in event.get('headers', {}).items() if isinstance(k, str)}
    accepted = [item.get('cookie', {}) for item in event.get('associatedCookies', [])
                if not item.get('blockedReasons')]
    device = next((c.get('value') for c in accepted if c.get('name') == 'oai-did'), None)
    cookie_header = headers.get('cookie', '')
    result = {'sent_cookie_count': len(accepted),
        'sent_auth_cookie_count': sum(c.get('name', '').startswith('__Secure-next-auth.session-token') for c in accepted),
        'sent_device_cookie_sha256': hashlib.sha256(device.encode()).hexdigest() if isinstance(device, str) else None,
        'cookie_header_bytes': len(cookie_header.encode()) if isinstance(cookie_header, str) else None,
        'sent_context_cookie_names': sorted({c.get('name') for c in accepted
            if c.get('name') in SESSION_CONTEXT_COOKIE_NAMES}),
        'header_names': sorted(k for k in headers if re.fullmatch(r'[a-z0-9:_-]{1,80}', k))[:128]}
    allowed = ('originator', 'x-openai-codex-window-type', 'x-openai-web-frontend',
        'x-oai-mcp-form-version', 'oai-language', 'accept-language', 'sec-ch-ua-platform',
        'sec-ch-ua-platform-version', 'sec-ch-ua', 'user-agent')
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

    def visit(node, depth=0):
        if depth > 12:
            return
        if isinstance(node, list):
            for item in node:
                visit(item, depth + 1)
        elif isinstance(node, dict):
            path = node.get('p', node.get('path', ''))
            if isinstance(path, str) and re.search(r'/content(?:/|$)', path):
                return
            fields = selected_fields(node)
            if isinstance(path, str) and '/metadata/' in path:
                leaf = path.rsplit('/', 1)[-1]
                fields.update(selected_fields({leaf: node.get('v', node.get('value'))}))
            if fields and fields not in found:
                found.append(fields)
            for key in ('message', 'metadata', 'v', 'value', 'data', 'response'):
                child = node.get(key)
                if isinstance(child, (dict, list)):
                    visit(child, depth + 1)

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


def generation_endpoint(url):
    parsed = urlsplit(url)
    if parsed.hostname != 'chatgpt.com':
        return None
    if parsed.path in {'/backend-api/conversation', '/backend-api/f/conversation',
                       '/backend-api/conversation/init', '/backend-api/conversation/prepare'}:
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
                else:
                    self.pending += segment
            if ended:
                if not self.dropping_line:
                    line = self.pending.decode('utf-8', errors='replace').strip()
                    if line == 'data: [DONE]':
                        self.done = True
                    for record in response_metadata(line)['metadata_records']:
                        if record not in self.records and len(self.records) < 128:
                            self.records.append(record)
                            new.append(record)
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
            except (ValueError, TypeError):
                pass

        def on_finish(event):
            early_cookie_metadata.pop(event.get('requestId'), None)
            entry = tracked.pop(event.get('requestId'), None)
            if entry:
                parser = entry['parser']
                emit('generation_stream_finished', **entry['envelope'], bytes_observed=parser.bytes_seen,
                     metadata_records=parser.records, sse_done=parser.done, truncated=parser.truncated,
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
        endpoint = generation_endpoint(response.url)
        if endpoint not in {'/backend-api/conversation', '/backend-api/f/conversation'} or response.request.method != 'POST':
            return
        envelope = {'source': 'backend', 'endpoint': endpoint, 'status': response.status,
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
            emit('generation_response_metadata', source='backend', endpoint=endpoint,
                 status=response.status, request_observer_id=id(response.request), page_object_id=page_identifier(response.request), **metadata)
        except Exception as error:
            emit('generation_observation_error', **envelope, phase='response',
                 body_available=False, exception_type=type(error).__name__)

    context.on('request', on_request)
    context.on('response', on_response)
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
