from pathlib import Path

root=Path(__file__).resolve().parents[1]
original=(root/'backups/incident-20261005/startapp.sh').read_text(encoding='utf-8')
marker='exec /opt/venv/bin/python -m src.api.server'
assert original.count(marker)==1
patched=original.replace(marker,
    '# Passive session evidence persists across container starts. No credentials are logged.\n'
    '/opt/venv/bin/python -m src.session_observer </dev/null >/dev/null 2>&1 &\n'+marker)
(root/'work/startapp-session-audit.sh').write_text(patched,encoding='utf-8',newline='\n')
print('startup audit hook prepared; no container restart requested')
