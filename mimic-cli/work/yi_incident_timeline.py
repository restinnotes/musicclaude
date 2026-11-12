import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

root = Path(__file__).resolve().parents[1]
out = Path(r'C:\Users\zuoyi\Documents\Codex\2026-10-03\new-chat\outputs\20261005登录态调查')
out.mkdir(exist_ok=True)
records=[]
for path in (root/'runs').glob('*/diagnostics.json'):
    try:
        d=json.loads(path.read_text(encoding='utf-8'))
        if d.get('profile','yi')!='yi' or not str(d.get('timestamp','')).startswith(('2026-10-05','2026-10-06')):
            continue
        error=d.get('error') or {}
        records.append({'timestamp_utc':d.get('timestamp'),'success':d.get('success'),
          'elapsed_seconds':d.get('elapsed_seconds'),'command':d.get('command'),
          'input_chars':len(d.get('prompt') or ''),'output_chars':len(d.get('response') or ''),
          'error_type':error.get('type'),'error_message':str(error.get('message',''))[:250],
          'run_id':d.get('run_id')})
    except (ValueError, OSError):
        pass
records.sort(key=lambda d:d['timestamp_utc'] or '')
for row in records:
    try:
        row['timestamp_new_york']=datetime.fromisoformat(row['timestamp_utc']).astimezone(ZoneInfo('America/New_York')).isoformat()
    except ValueError:
        pass
(out/'CLI调用时间线.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
success=[r for r in records if r['success']]
temporary_errors=[r for r in records if 'Temporary Chat activation' in r['error_message']]
print(json.dumps({'total_calls':len(records),'successes':len(success),'temporary_errors':len(temporary_errors),
 'last_successes':success[-4:],'first_recent_temporary_errors':[r for r in temporary_errors if (r['timestamp_utc'] or '')>'2026-10-05T21:00'][:4],
 'last_calls':records[-5:]},ensure_ascii=False))
