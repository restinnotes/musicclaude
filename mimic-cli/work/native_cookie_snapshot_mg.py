"""Read-only native-cookie snapshot for MG clones; encrypted on Windows.

RSA/AES envelope is accepted once. Decrypted cookies exist only in RAM and
Windows-user DPAPI storage. No browser identity is guessed or overridden.
"""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import secrets
import sys
import time

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from mg_private_cookie import dpapi_json, validate_capture


def main(args):
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    nonce = secrets.token_hex(24)
    (out / 'public.json').write_text(json.dumps(dict(nonce=nonce,
        public_key_pem=private.public_key().public_bytes(serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo).decode())), encoding='utf-8')
    print(json.dumps(dict(waiting=True, public_file=str(out / 'public.json'))), flush=True)
    began = time.monotonic()
    sealed = out / 'sealed.json'
    while not sealed.exists():
        if time.monotonic() - began > 600:
            raise RuntimeError('Encrypted capture expired')
        time.sleep(.25)
    if sealed.stat().st_size > 10 * 1024 * 1024:
        raise RuntimeError('Envelope exceeded bound')
    try:
        envelope = json.loads(sealed.read_text())
    finally:
        sealed.unlink(missing_ok=True)
    decode = lambda name: base64.b64decode(envelope[name], validate=True)
    aes = private.decrypt(decode('wrapped_key'), padding.OAEP(
        mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
    assert len(aes) == 32
    payload = json.loads(AESGCM(aes).decrypt(decode('iv'),
        decode('ciphertext_and_tag'), nonce.encode()))
    cookies = validate_capture(payload, nonce=nonce, now=time.time())
    assert any(c['name'].startswith('__Secure-next-auth.session-token') for c in cookies)
    captured = payload['captured_epoch_seconds']
    del payload, private, aes, envelope
    file = out / 'native-cookies.dpapi.json'
    file.write_text(json.dumps(dict(format='mimicgate-native-cookie-dpapi-v1',
        payload=dpapi_json(dict(schema=1, cookies=cookies,
            captured_epoch_seconds=captured)))), encoding='utf-8')
    result = dict(utc=datetime.now(timezone.utc).isoformat(), captured_epoch_seconds=captured,
        cookie_count=len(cookies), authentication_cookie_present=True,
        device_matches_authorized_yi=True, native_cookie_attributes_preserved=True,
        encrypted=True, source_modified=False, native_browser_modified=False,
        native_browser_identity_overridden=False, cookie_file=str(file),
        cookie_file_sha256=hashlib.sha256(file.read_bytes()).hexdigest(),
        validator_sha256=hashlib.sha256(Path(__file__).with_name('mg_private_cookie.py').read_bytes()).hexdigest())
    (out / 'import-report.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        main(args)
    except Exception:
        print(json.dumps(dict(completed=False, error='Encrypted native-cookie capture rejected; source unchanged')), flush=True)
        raise SystemExit(1) from None
