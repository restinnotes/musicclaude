"""Export selected non-secret session observations for this experiment only."""
from pathlib import Path
from collections import Counter
import json
import subprocess
import sys

here=Path(__file__).resolve().parent
profile,container,batch=sys.argv[1:4]
since=json.loads((Path(batch)/'state.json').read_text())['started_utc']
script="""from pathlib import Path
import json,sys
p=Path('/app/state/yi-session-observer.jsonl')
keys={'utc','event','source','status','host','path_category','deletion_directive','empty_value','max_age','session_cookie_count','request_id','exception_type','pid'}
selected=[]
if p.exists():
    for line in p.read_text().splitlines():
        try:
            event=json.loads(line)
        except ValueError:
            continue
        if event.get('utc','')>=sys.argv[1]:
            selected.append({k:v for k,v in event.items() if k in keys})
print(json.dumps(selected))
"""
proc=subprocess.run(['docker','exec',container,'python','-c',script,since],
    capture_output=True,text=True,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
events=json.loads(proc.stdout)
record={'profile':profile,'container':container,'since_utc':since,
        'event_counts':dict(Counter(e['event'] for e in events)),
        'auth_cookie_deletion_observations':sum(e.get('deletion_directive') is True for e in events),
        'request_auth_preflights':[e for e in events if e['event']=='request_auth_preflight'],
        'http_auth_or_access_errors':[e for e in events if e['event']=='http_auth_or_access_error'],
        'note':'Metadata only; absence of observations does not prove every network response was captured.'}
(here/(profile+'-auth-summary.json')).write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps({k:record[k] for k in ['profile','event_counts','auth_cookie_deletion_observations']}))
