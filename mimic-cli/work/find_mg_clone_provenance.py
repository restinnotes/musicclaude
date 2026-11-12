"""Read this task's tool-call records; emit only clone ownership evidence."""
import hashlib
import json
from pathlib import Path
import re
from build_mg_storage_pair import OUT


def main():
    root=Path('C:/Users/zuoyi/.codex/sessions')
    files=list(root.glob('2026/10/*/*01a103ca-311e-7172-bc29-918cd09c6cb5*.jsonl'))
    matches=[]
    for file in files:
        with file.open('rb') as stream:
            while True:
                line=stream.readline(2*1024*1024)
                if not line:break
                if not line.endswith(b'\n'):
                    while line and not line.endswith(b'\n'):line=stream.readline(2*1024*1024)
                    continue
                if b'yi-mg-clone-20261007' not in line:continue
                try:row=json.loads(line)
                except ValueError:continue
                stamp=row.get('timestamp','')
                if not '2026-10-07T21:00'<=stamp<='2026-10-07T21:36:30':continue
                payload=row.get('payload',{})
                if payload.get('type') not in ('function_call','custom_tool_call'):continue
                arguments=payload.get('arguments') or payload.get('input','')
                if not isinstance(arguments,str):arguments=json.dumps(arguments)
                matches.append(dict(timestamp=stamp,task_session_file=file.name,
                    tool_name=payload.get('name'),call_id=payload.get('call_id'),
                    arguments_sha256=hashlib.sha256(arguments.encode()).hexdigest(),
                    contains_clone_name=True,contains_name_argument='--name' in arguments,
                    contains_create_operation=bool(re.search(r'\b(create|commit)\b',arguments)),
                    contains_start_operation=bool(re.search(r'\bstart\b',arguments)),
                    contains_label='codex.task=yi-mg-clone-20261007' in arguments))
    file=OUT/'other-clone-tool-call-provenance-v2.json'
    if file.exists():raise RuntimeError('Ownership evidence already exists')
    file.write_text(json.dumps(dict(source='This task session tool calls only',
        raw_arguments_or_auth_logged=False,matches=matches),indent=2),encoding='utf-8')
    print(json.dumps(dict(report=str(file),matches=matches)))


if __name__=='__main__':main()
