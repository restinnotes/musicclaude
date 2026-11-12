"""Inspect public app modules matching the bytes received by an MG trial."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'experiments/yi-rootcause/20261007T2135Z'


def main():
    observer = OUT / 'observer-native_identity-235244.json'
    rows = json.loads(observer.read_text())
    targets = {}
    for row in rows:
        if row.get('event') == 'forensic_frontend_asset' and row.get('observation_complete') is True:
            name = row['basename']
            if re.fullmatch(r'(646436|7078)\.[a-z0-9]{10}\.js', name):
                targets[name] = row['body_sha256']
    folder = OUT / ('verified-context-source-' + datetime.now(timezone.utc).strftime('%H%M%S'))
    folder.mkdir(exist_ok=False)
    records = []
    for name, expected in targets.items():
        url = 'https://chatgpt.com/cdn/assets/' + name
        record = {'basename': name, 'public_url': url, 'account_cookies_sent': False,
                  'observed_body_sha256': expected}
        request = Request(url, headers={'Accept-Encoding': 'identity'})
        try:
            with urlopen(request, timeout=20) as response:
                if urlsplit(response.url).hostname != 'chatgpt.com':
                    raise ValueError('Unexpected public redirect')
                data = response.read(2 * 1024 * 1024 + 1)
            if len(data) > 2 * 1024 * 1024:
                raise ValueError('Public module exceeded the byte budget')
            actual = hashlib.sha256(data).hexdigest()
            record.update(downloaded_sha256=actual, matches_received_trial_body=(actual == expected))
            if actual == expected:
                (folder / name).write_bytes(data)
                source = data.decode('utf-8')
                snippets = {}
                for needle in ('browser_context={instance_id', 'browserContext?.instanceId',
                               'function E(){', 'source:"extension"', 'browser-side',
                               'data-browser', 'browser-context'):
                    occurrences = list(re.finditer(re.escape(needle), source))[:4]
                    if occurrences:
                        snippets[needle] = [source[max(0, m.start()-160):m.end()+350] for m in occurrences]
                record['bounded_source_snippets'] = snippets
        except Exception as error:
            record['error_class'] = type(error).__name__
        records.append(record)
    result = {'utc': datetime.now(timezone.utc).isoformat(), 'observer_source': str(observer),
              'account_profile_or_browser_accessed': False, 'model_request_sent': False,
              'assets': records, 'executed_bytecode_verified': False,
              'conclusion_scope': 'Public source matches received document modules; server interpretation of the field remains unknown.'}
    (folder / 'report.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({'folder': str(folder), 'assets': [{key: r.get(key) for key in
        ('basename', 'matches_received_trial_body', 'downloaded_sha256', 'error_class')} for r in records]}))


if __name__ == '__main__':
    main()
