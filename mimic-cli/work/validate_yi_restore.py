"""One authorized recovery check while the incident guard blocks background jobs."""
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
OUT=Path(r'C:\Users\zuoyi\Documents\Codex\2026-10-03\new-chat\outputs')
spec=importlib.util.spec_from_file_location('mg',ROOT/'cli/mg.py')
mg=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mg)
token=mg.read_auth()
try:
    _,pool=mg.http_json('/v1/mimic-cli/concurrency',token)
    if pool['in_flight'] or pool['waiting']:
        raise RuntimeError('Recovery check requires an idle yi service')
    status,result=mg.http_json('/v1/chat/completions',token,
        {'model':mg.MODEL,'reasoning_effort':'xhigh','messages':[{'role':'user','content':'Reply with exactly TEST_OK. No other text.'}],
         'stream':False},timeout=300,standard=True)
    result=mg.safe_object(result,token)
    d=result.get('mimicgate_diagnostics',{})
    answer=result['choices'][0]['message']['content']
    passed=(answer.strip()=='TEST_OK' and d.get('temporary_chat',{}).get('verified') is True and
        d.get('non_personalized',{}).get('verified') is True and
        d.get('model',{}).get('model')==mg.MODEL and mg.verified_effort(d.get('model',{})) and
        d.get('verification_stage')=='immediately_before_submission' and d.get('response_complete') is True)
    record={'http_status':status,'success':passed,'response':answer,'diagnostics':d,
            'incident_guard_kept_during_recovery_check':True}
    OUT.joinpath('yi恢复后TEST_OK.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'success':passed,'response':answer,'actual_effort':d.get('model',{}).get('selected_effort')}))
    sys.exit(0 if passed else 1)
except mg.CLIError as error:
    record={'success':False,'error':{'type':error.kind,'message':str(error)},'diagnostics':error.diagnostics}
    OUT.joinpath('yi恢复后TEST_OK.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(record,ensure_ascii=False))
    sys.exit(1)
finally:
    token=''
