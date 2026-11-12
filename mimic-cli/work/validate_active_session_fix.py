"""One normal standard request while the investigation guard still holds callers."""
import importlib.util
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
out=Path(r'C:\Users\zuoyi\Documents\Codex\2026-10-03\new-chat\outputs\20261005登录态调查')
spec=importlib.util.spec_from_file_location('mg',root/'cli/mg.py')
mg=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mg)
token=mg.read_auth()
record={'success':False,'guard_held':True}
try:
    _,pool=mg.http_json('/v1/mimic-cli/concurrency',token)
    assert pool['in_flight']==0 and pool['waiting']==0
    status,result=mg.http_json('/v1/chat/completions',token,
        {'model':mg.MODEL,'reasoning_effort':'xhigh','messages':[{'role':'user','content':'Reply with exactly TEST_OK. No other text.'}],
         'stream':False},timeout=300,standard=True)
    result=mg.safe_object(result,token)
    diag=result.get('mimicgate_diagnostics',{})
    answer=result['choices'][0]['message']['content']
    passed=(answer.strip()=='TEST_OK' and diag.get('temporary_chat',{}).get('verified') is True and
            diag.get('non_personalized',{}).get('verified') is True and mg.verified_effort(diag.get('model',{})) and
            diag.get('response_complete') is True and diag.get('authentication',{}).get('session_cookie_count',0)>0 and
            diag.get('submission_pacing',{}).get('minimum_interval_seconds')==5 and
            diag.get('submission_pacing',{}).get('send_attempt_at',0)>0)
    record={'http_status':status,'success':passed,'response':answer,'diagnostics':diag,'guard_held':True}
except mg.CLIError as error:
    record={'success':False,'error_type':error.kind,'error_message':str(error),'diagnostics':error.diagnostics,'guard_held':True}
finally:
    token=''
    (out/'已生效保护的标准调用验证.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'success':record['success'],'response':record.get('response'),
      'authentication':record.get('diagnostics',{}).get('authentication'),
      'submission_pacing':record.get('diagnostics',{}).get('submission_pacing'),
      'error_type':record.get('error_type')},ensure_ascii=False))
raise SystemExit(0 if record['success'] else 1)
