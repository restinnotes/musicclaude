"""Cookie capacity evidence without values, hashes, or credential-bearing headers."""
import json
import sqlite3
from pathlib import Path

db = sqlite3.connect('file:/app/browser_data/Default/Cookies?mode=ro', uri=True)
columns = [r[1] for r in db.execute('pragma table_info(cookies)')]
rows = db.execute('select host_key,name,path,length(value),length(encrypted_value),expires_utc,is_httponly,is_secure,priority from cookies where host_key like ?', ('%chatgpt.com',)).fetchall()
result = {'total_for_chatgpt': len(rows), 'by_domain': {}, 'cookies': []}
for host, name, path, plain, encrypted, expires, httponly, secure, priority in rows:
    result['by_domain'][host] = result['by_domain'].get(host, 0) + 1
    result['cookies'].append({'domain': host, 'name': name, 'path': path, 'plain_bytes': plain,
        'encrypted_bytes': encrypted, 'expires_utc': expires, 'httponly': bool(httponly),
        'secure': bool(secure), 'priority': priority})
print(json.dumps(result))
