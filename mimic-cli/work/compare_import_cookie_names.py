"""Compare cookie identities with the encrypted pre-import backup; never read values."""
from pathlib import Path
import json
import sys

sys.path.insert(0, 'work')
from clone_yi_no_stealth import docker
OUT = Path('experiments/yi-rootcause/20261006T1625Z')
native = json.loads((OUT / 'native-nonconversation-cookie-shape.json').read_text(encoding='utf-8'))
code = """import sqlite3,json
db=sqlite3.connect('file:/app/browser_data/.yi-diagnostics/cookies-before-retention-20261006T163416-50d0a35c.sqlite?mode=ro',uri=True)
rows=db.execute('select name,host_key,path from cookies').fetchall()
print(json.dumps([{'name':n,'domain':h,'path':p} for n,h,p in rows]))
"""
before = json.loads(docker('exec', 'yi-rca-capacity-20261006', '/opt/venv/bin/python', '-c', code))
identities = {(c['name'],c['domain'],c['path']) for c in before}
added = []
replaced = []
for c in native['cookies']:
    identity = {k:c[k] for k in ('name','domain','path')}
    (replaced if (c['name'],c['domain'],c['path']) in identities else added).append(identity)
record = {'source':'encrypted SQLite backup taken immediately before native-cookie import',
    'cookie_values_read':False,'new_cookie_identities':added,'existing_cookie_identities_imported':replaced,
    'note':'Identity overlap does not establish whether the value was equal or changed.'}
(OUT / 'native-import-cookie-identity-delta.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps({'new_cookie_names': [c['name'] for c in added],
    'existing_cookie_names_imported':[c['name'] for c in replaced]}))
