"""Verify preserved trial artifacts without sending another model request."""
from pathlib import Path
from datetime import datetime, timezone
import json
import re
import subprocess

here=Path(__file__).resolve().parent
result=json.loads((here/'results.json').read_text(encoding='utf-8'))
rows=result['trials']
assert len(rows)==6
assert sorted((r['profile'],r['sequence']) for r in rows)==[(p,n) for p in ['yi','yi-camoufox'] for n in range(1,4)]
assert all(r['response_complete'] and r['transport_success'] for r in rows)
assert all(r['actual_model']=='gpt-5.6-sol' and r['actual_effort']=='xhigh' for r in rows)
assert all(r['temporary_verified'] and r['unpersonalized_verified'] for r in rows)
assert len({r['prompt_sha256'] for r in rows})==1
assert all(r['screenshots_hash_verified'] for r in rows)
for row in rows:
    text=(Path(row['run_path'])/'response.txt').read_text(encoding='utf-8')
    assert re.search(r'x\s*=\s*6|答案是\s*6',text), row['run_id']
assert all(r['answer']==6 for r in rows)
auth={p:json.loads((here/(p+'-auth-summary.json')).read_text()) for p in ['yi','yi-camoufox']}
assert all(len(a['request_auth_preflights'])==3 for a in auth.values())
assert all(all(e['session_cookie_count']>0 for e in a['request_auth_preflights']) for a in auth.values())
containers=[]
for name in ['yi-mimicgate-20261002','yi-camoufox-20261006','shiyan-mimicgate-20261002','shiyan-camoufox-20261006']:
    proc=subprocess.run(['docker','inspect',name,'--format','{{json .State}}'],capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
    assert proc.returncode==0, name
    state=json.loads(proc.stdout)
    containers.append({'container':name,'status':state['Status'],'running':state['Running'],'oom_killed':state['OOMKilled']})
assert all(not c['running'] and not c['oom_killed'] for c in containers)
record={'verified_at_utc':datetime.now(timezone.utc).isoformat(),'formal_trials':6,
        'same_prompt_sha256':rows[0]['prompt_sha256'],'all_actual_effort_xhigh':True,
        'all_complete_final_answers':True,'all_final_answer_6':True,'all_screenshot_hashes_match':True,
        'auth_preflights_with_cookie':6,'auth_cookie_deletion_observations':sum(a['auth_cookie_deletion_observations'] for a in auth.values()),
        'http_auth_or_access_error_observations':sum(len(a['http_auth_or_access_errors']) for a in auth.values()),
        'containers':containers}
(here/'verification.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(record))
