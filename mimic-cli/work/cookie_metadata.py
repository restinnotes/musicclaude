"""Only cookie names, timestamps and presence flags; never credential values."""
import json
from pathlib import Path
import sqlite3
import time

path = Path('/app/browser_data/Default/Cookies')
connection = sqlite3.connect('file:' + str(path) + '?mode=ro', uri=True)
rows = connection.execute("select host_key,name,path,expires_utc,is_persistent,last_update_utc,length(value),length(encrypted_value) from cookies where host_key like '%chatgpt%' or host_key like '%openai%'").fetchall()
epoch_offset = 11644473600
print(json.dumps([{'domain': domain, 'name': name, 'path': cookie_path, 'expires_at': expires / 1000000 - epoch_offset,
    'persistent': bool(persistent), 'last_updated_at': updated / 1000000 - epoch_offset,
    'has_value': bool(plain_length or encrypted_length), 'expired': expires > 0 and expires / 1000000 - epoch_offset < time.time()}
    for domain, name, cookie_path, expires, persistent, updated, plain_length, encrypted_length in rows], indent=2))
