import hashlib,json,sys
from pathlib import Path

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
import evo
folder=Path(__file__).parent
result=json.loads((folder/'actual_result.json').read_text(encoding='utf-8'))
body=result['body']
dg=body['mimicgate_diagnostics']
answer=body['choices'][0]['message']['content']
parsed=evo.parse_json(answer)
record={
    'run_id':'v6b2_op60_g6_r26g3_vsqu','remote_id':'f0788484fbb8678d4ed2',
    'http_status':result['http_status'],'receiver_seconds':result['seconds'],
    'response_complete':dg['response_complete'],'answer_characters':len(answer),
    'sections':len(parsed['sections']),
    'model':dg['model']['model'],'effort':dg['model']['selected_effort'],
    'temporary_verified':dg['temporary_chat']['verified'],
    'unpersonalized_verified':dg['non_personalized']['verified'],
    'prompt_verified':dg['prompt_content_verified'],
    'response_validation':dg.get('response_validation'),
    'reader_sha256':hashlib.sha256((folder/'detector.fixed.py').read_bytes()).hexdigest(),
    'tests':{'reader_and_warning_classification':13,'existing_completion_guards':11,'cross_process_schedule':13},
}
assert record['http_status']==200 and record['response_complete'] is True
assert record['sections']==14 and record['model']=='gpt-6' and record['effort']=='high'
assert record['temporary_verified'] and record['unpersonalized_verified'] and record['prompt_verified']
(folder/'validation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
