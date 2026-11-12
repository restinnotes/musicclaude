"""Archive public URLs already observed in finished reports; successful HTTP is not fact verification."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import urllib.error
import urllib.request

HERE = Path(__file__).resolve().parent
DEST = HERE / 'source-artifacts' / 'pages'
DEST.mkdir(parents=True, exist_ok=True)

class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hidden = 0
        self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'noscript'): self.hidden += 1
        if tag in ('p', 'div', 'br', 'tr', 'h1', 'h2', 'h3', 'li'): self.parts.append('\n')
    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'noscript'): self.hidden = max(0, self.hidden - 1)
    def handle_data(self, data):
        if not self.hidden: self.parts.append(data)

def fetch(url):
    identifier = hashlib.sha256(url.encode()).hexdigest()[:20]
    record_path = DEST / (identifier + '.json')
    if record_path.exists():
        return json.loads(record_path.read_text(encoding='utf-8'))
    record = {'url':url, 'retrieved_at':datetime.now(timezone.utc).isoformat(),
        'claim_support_verification':'UNVERIFIED', 'artifact_id':identifier}
    try:
        request = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0 (compatible; local-research-source-archive)'})
        with urllib.request.urlopen(request, timeout=15) as response:
            body = response.read(5 * 1024 * 1024 + 1)
            if len(body) > 5 * 1024 * 1024:
                raise ValueError('Source exceeds archive bound')
            record.update(http_status=response.status, final_url=response.url,
                content_type=response.headers.get('Content-Type'), bytes=len(body),
                sha256=hashlib.sha256(body).hexdigest(), last_modified=response.headers.get('Last-Modified'))
            (DEST / (identifier + '.body')).write_bytes(body)
            if 'html' in str(record['content_type']) or 'text/' in str(record['content_type']):
                parser = VisibleText()
                parser.feed(body.decode(response.headers.get_content_charset() or 'utf-8', errors='replace'))
                text = '\n'.join(line.strip() for line in ''.join(parser.parts).splitlines() if line.strip())
                (DEST / (identifier + '.txt')).write_text(text, encoding='utf-8')
                record['text_characters'] = len(text)
            record['access_state'] = 'downloaded_public_response_not_yet_semantically_reviewed'
    except Exception as error:
        record.update(access_state='fetch_failed', error_type=type(error).__name__)
        if isinstance(error, urllib.error.HTTPError): record['http_status'] = error.code
    record_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    return record

urls = set()
for folder in (HERE / 'jobs').iterdir():
    evidence = folder / 'evidence.json'
    if evidence.exists():
        for source in json.loads(evidence.read_text(encoding='utf-8')).get('sources', []):
            if isinstance(source, dict) and str(source.get('url', '')).startswith(('https://', 'http://')):
                urls.add(source['url'])
with ThreadPoolExecutor(max_workers=4) as pool:
    records = list(pool.map(fetch, sorted(urls)))
(HERE / 'source-archive-index.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'sources':len(records), 'downloaded':sum(row['access_state'].startswith('downloaded') for row in records),
    'failed':sum(row['access_state']=='fetch_failed' for row in records), 'fact_verification':'still requires reading/support check'}))
