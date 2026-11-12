"""Explicit second channel, coordinated by main agent: one active Flash + one GPT job."""
from pathlib import Path
import json,hashlib
import run_calls as rc
R=Path(__file__).resolve().parents[1]
p=R/'inputs'/'S02_gpt_envelope.txt'
text='请完整读取附件 S02.txt，执行其中的编辑任务。附件就是另一模型收到的完整相同输入：包含编辑指令、完整原A、已冻结逐项原意账本。不要总结任务，直接交指定JSON。'
p.write_text(text,encoding='utf-8')
job=dict(job_id='S02_G6_relations_r1_attachment',channel='gpt2',model='gpt-6-thinking',prompt_file='inputs/S02_gpt_envelope.txt',prompt_sha256=rc.file_sha(p),attachments=[{'path':'inputs/S02.txt','sha256':rc.file_sha(R/'inputs'/'S02.txt')}],timeout_seconds=1800,min_response_chars=500,labels={'segment':'S02','method':'source_distinctions_relations','round':1,'input_content':'same full S02.txt as Flash; native attachment envelope differs'})
manifest=R/'jobs_gpt.json'
manifest.write_text(json.dumps({'schema_version':1,'max_workers':1,'output_dir':'scripts/call_results','jobs':[job]},ensure_ascii=False,indent=2),encoding='utf-8')
prepared=rc.validate_job(job,R)
result=rc.run_job(prepared,R/'scripts'/'call_results',rc.file_sha(manifest))
print(json.dumps(rc.safe(result),ensure_ascii=False))
