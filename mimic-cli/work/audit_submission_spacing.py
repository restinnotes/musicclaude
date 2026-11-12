from datetime import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo

root=Path(__file__).resolve().parents[1]
out=Path(r'C:\Users\zuoyi\Documents\Codex\2026-10-03\new-chat\outputs\20261005登录态调查')
timeline=json.loads((out/'CLI调用时间线.json').read_text(encoding='utf-8'))
rows=[]
for r in timeline:
    if not '2026-10-05T21:52'<=r['timestamp_utc']<'2026-10-05T22:34':
        continue
    p=root/'runs'/r['run_id']/'diagnostics.json'
    d=json.loads(p.read_text(encoding='utf-8'))
    diag=d.get('diagnostics') or {}
    submitted=diag.get('submitted_at')
    completed=diag.get('completed_at')
    rows.append({'run_id':r['run_id'],'request_started_utc':r['timestamp_utc'],
        'input_chars':r['input_chars'],'success':r['success'],'error_type':r['error_type'],
        'submitted_at_epoch':submitted,'submitted_new_york':datetime.fromtimestamp(submitted,ZoneInfo('America/New_York')).isoformat() if submitted else None,
        'completed_at_epoch':completed,'pool_at_completion':diag.get('concurrency')})
sends=sorted((r for r in rows if r['submitted_at_epoch']),key=lambda r:r['submitted_at_epoch'])
gaps=[{'gap_seconds':round(b['submitted_at_epoch']-a['submitted_at_epoch'],3),
       'first_send_new_york':a['submitted_new_york'],'second_send_new_york':b['submitted_new_york'],
       'first_run':a['run_id'],'second_run':b['run_id']} for a,b in zip(sends,sends[1:])]
report={'interval':'2026-10-05 17:52–18:34 America/New_York','total_cli_calls':len(rows),
        'calls_with_send_timestamps':len(sends),'smallest_recorded_send_gaps':sorted(gaps,key=lambda r:r['gap_seconds'])[:8],
        'send_pairs_less_than_1s':sum(g['gap_seconds']<1 for g in gaps),
        'send_pairs_less_than_5s':sum(g['gap_seconds']<5 for g in gaps),
        'explicit_minimum_submission_interval_in_existing_code':False,
        'warning':'Only calls with recorded submitted_at timestamps are included; no unrecorded action is inferred.',
        'calls':rows}
(out/'实际提交间隔.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='calls'},ensure_ascii=False))

