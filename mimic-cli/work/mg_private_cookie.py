"""Windows-user encrypted native cookies; no provider or browser operations."""
import base64
import ctypes
from ctypes import wintypes
import hashlib
import json
import math
import os
import secrets

EXPECTED_DEVICE_SHA256 = '957b26137da59e2250494d31109c3f507728d7173f9e2f1ab1571192783859c8'
EXPECTED_ACCOUNT_SHA256 = 'b3efb6361563c139233ed7b7ef61a7c9afe0bd48d4eb3525dbe31956b024d6da'


class Blob(ctypes.Structure):
    _fields_ = [('length', wintypes.DWORD), ('data', ctypes.POINTER(ctypes.c_ubyte))]


def dpapi_json(value, decrypt=False):
    if os.name != 'nt':
        raise RuntimeError('Native capture requires Windows-user DPAPI')
    raw = base64.b64decode(value, validate=True) if decrypt else json.dumps(value).encode()
    buffer = ctypes.create_string_buffer(raw)
    source = Blob(len(raw), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte)))
    result = Blob()
    library = ctypes.WinDLL('crypt32', use_last_error=True)
    operation = library.CryptUnprotectData if decrypt else library.CryptProtectData
    operation.argtypes = [ctypes.POINTER(Blob), ctypes.c_void_p, ctypes.c_void_p,
        ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(Blob)]
    operation.restype = wintypes.BOOL
    if not operation(ctypes.byref(source), None, None, None, None, 1, ctypes.byref(result)):
        raise RuntimeError('Native capture encryption unavailable')
    try:
        encoded = ctypes.string_at(result.data, result.length)
        return json.loads(encoded) if decrypt else base64.b64encode(encoded).decode()
    finally:
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.LocalFree.argtypes = [ctypes.c_void_p]
        kernel.LocalFree.restype = ctypes.c_void_p
        kernel.LocalFree(result.data)


def validate_capture(data, nonce, now):
    if not isinstance(data, dict) or not secrets.compare_digest(str(data.get('nonce', '')), nonce):
        raise ValueError('Native capture nonce mismatch')
    stamp = data.get('captured_epoch_seconds')
    if type(stamp) not in (int, float) or not math.isfinite(stamp) or not 0 <= now - stamp <= 90:
        raise ValueError('Native capture is not fresh')
    source = data.get('cookies')
    if not isinstance(source, list) or not 1 <= len(source) <= 5000:
        raise ValueError('Native capture cookie count invalid')
    cookies, identities = [], set()
    for item in source:
        if not isinstance(item, dict):
            raise ValueError('Native cookie structure invalid')
        if str(item.get('domain', '')).lstrip('.') != 'chatgpt.com':
            continue
        name, value = item.get('name'), item.get('value')
        if not isinstance(name, str) or not name or not isinstance(value, str):
            raise ValueError('Native cookie fields invalid')
        if name.startswith(('conv_key_', 'history_off_')):
            continue
        expiry = item.get('expires', -1)
        if type(expiry) not in (int, float) or not math.isfinite(expiry):
            raise ValueError('Native cookie expiry invalid')
        if expiry == 0 or (expiry > 0 and expiry <= now):
            continue
        partition = item.get('partitionKey')
        if item.get('partitionKeyOpaque') is True or (partition is not None and
                (not isinstance(partition, dict) or partition.get('topLevelSite') != 'https://chatgpt.com'
                    or partition.get('hasCrossSiteAncestor') is not False)):
            raise ValueError('Unsupported native cookie partition')
        identity = (item['domain'], item.get('path', '/'), name, json.dumps(partition, sort_keys=True))
        if identity in identities:
            raise ValueError('Duplicate native cookie identity')
        identities.add(identity)
        cookies.append(item.copy())
    for name, expected in [('oai-did', EXPECTED_DEVICE_SHA256), ('_account', EXPECTED_ACCOUNT_SHA256)]:
        values = {hashlib.sha256(c['value'].encode()).hexdigest() for c in cookies if c['name'] == name}
        if values != {expected}:
            raise ValueError('Native capture differs from authorized yi identity')
    if not any(c['name'].startswith('__Secure-next-auth.session-token') for c in cookies):
        raise ValueError('Native capture authentication absent')
    return cookies
