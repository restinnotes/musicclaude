"""Single isolated mg attachment request in original container/browser. Public evidence only."""
import hashlib,json,subprocess,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
CONTAINER='yi-mimicgate-20261002'
def run(cmd,timeout=30):
    return subprocess.run(cmd,capture_output=True,timeout=timeout,creationflags=subprocess.CREATE_NO_WINDOW)
def call(folder,prompt,attachments,mg,token):
    _,state=mg.http_json('/v1/mimic-cli/concurrency',token,timeout=10)
    if state.get('in_flight') or state.get('waiting'):raise mg.CLIError('busy','Shared gateway must be idle before isolated mg attachment request; no request sent')
    remote='/app/state/china-routing-20261006-attachments/'+folder.name
    r=run(['docker','exec',CONTAINER,'mkdir','-p',remote])
    if r.returncode:raise RuntimeError('Cannot prepare attachment directory')
    entries=[]
    files=[(HERE/'mg_attachment_adapter_container.py','adapter.py'),(folder/'submitted-prompt.txt','prompt.txt')]
    for a in attachments:
        p=HERE/a['relative_path'];raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
        if sha!=a['sha256']:raise RuntimeError('Immutable evidence attachment changed')
        files.append((p,a['filename']));entries.append({'path':remote+'/'+a['filename'],'sha256':sha})
    manifest={'prompt':remote+'/prompt.txt','files':entries,'result':remote+'/result.json'}
    local=folder/'adapter-manifest.json';local.write_text(json.dumps(manifest),encoding='utf-8');files.append((local,'manifest.json'))
    for p,name in files:
        if run(['docker','cp',str(p),CONTAINER+':'+remote+'/'+name]).returncode:raise RuntimeError('Evidence copy failed before browser submission')
    result=run(['docker','exec','-w','/app',CONTAINER,'/opt/venv/bin/python',remote+'/adapter.py',remote+'/manifest.json'],timeout=1950)
    (folder/'adapter-process.log').write_bytes(result.stdout+result.stderr)
    for name in ('upload-dom.json','attachment-before-send.png'):
        run(['docker','cp',CONTAINER+':'+remote+'/'+name,str(folder/name)])
    local_result=folder/'adapter-response.json'
    if run(['docker','cp',CONTAINER+':'+remote+'/result.json',str(local_result)]).returncode:raise RuntimeError('Adapter result missing; investigate original page before any retry')
    data=json.loads(local_result.read_text(encoding='utf-8'))
    if data['http_status']>=400:
        b=data['body'];e=b.get('error',{});raise mg.CLIError(e.get('type','attachment_transport'),e.get('message','Attachment request failed'),data['http_status'],b.get('mimicgate_diagnostics',{}))
    return data['http_status'],data['body']
