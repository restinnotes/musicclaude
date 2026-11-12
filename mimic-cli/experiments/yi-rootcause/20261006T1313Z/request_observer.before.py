"""Passive, allowlisted generation metadata; never stores headers or prompt text."""
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
            emit('generation_request_metadata', source='backend', endpoint=endpoint,
                 request_observer_id=id(request), page_object_id=page_identifier(request), workspace_header_sha256=scope_hash,
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
    emit('generation_audit_attached', source='backend', content_saved=False, auth_headers_saved=False)
