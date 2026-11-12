import json
from pathlib import Path
import sqlite3
from datetime import datetime, timezone

root = Path('/app/browser_data')
report = {'captured_utc': datetime.now(timezone.utc).isoformat(), 'databases': []}
for path in root.glob('*/Cookies'):
    db = sqlite3.connect(f'file:{path}?mode=ro', uri=True)
    try:
        cols = [r[1] for r in db.execute('PRAGMA table_info(cookies)')]
        selected = [name for name in ('host_key','name','expires_utc','creation_utc','last_access_utc','last_update_utc','is_persistent') if name in cols]
        rows = db.execute('SELECT '+','.join(selected)+' FROM cookies WHERE name LIKE ?', ('__Secure-next-auth.session-token%',)).fetchall()
        report['databases'].append({'path':str(path),'auth_rows':[dict(zip(selected,row)) for row in rows],
          'total_rows':db.execute('SELECT count(*) FROM cookies').fetchone()[0],
          'journal_exists':Path(str(path)+'-journal').exists(),
          'wal_exists':Path(str(path)+'-wal').exists(),
          'size_bytes':path.stat().st_size})
    finally:
        db.close()
Path('/app/state/yi-incident-database-20261005.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report))
