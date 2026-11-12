"""Read only the existing allowlisted MG observer; no browser or model action."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from build_mg_storage_pair import OUT, docker

EVENTS = ['generation_wire_request','generation_wire_cookie_metadata',
    'generation_response_started','generation_stream_metadata','generation_stream_finished',
    'client_hint_negotiation_observed','forensic_frontend_asset',
    'forensic_asset_observation_limit','generation_observation_error']


def capture(condition,after):
    manifest=json.loads((OUT/'matched-pair.json').read_text())
    name=manifest['clones'][condition]['container']
    code='''import json
from pathlib import Path
rows=[]
for line in Path('/app/state/yi-session-observer.jsonl').open():
 try:row=json.loads(line)
 except ValueError:continue
 if row.get('utc','')>=AFTER and row.get('event') in EVENTS:rows.append(row)
print(json.dumps(rows))
'''.replace('AFTER',repr(after)).replace('EVENTS',repr(EVENTS))
    rows=json.loads(docker('exec',name,'/opt/venv/bin/python','-c',code))
    file=OUT/('observer-'+condition+'-'+datetime.now(timezone.utc).strftime('%H%M%S')+'.json')
    file.write_text(json.dumps(rows,indent=2),encoding='utf-8')
    requests=[r for r in rows if r['event']=='generation_wire_request']
    headers=[r for r in rows if r['event']=='generation_wire_cookie_metadata']
    streams=[r for r in rows if r['event']=='generation_stream_metadata']
    negotiations=[r for r in rows if r['event']=='client_hint_negotiation_observed']
    print(json.dumps(dict(file=str(file),sha256=hashlib.sha256(file.read_bytes()).hexdigest(),
        event_counts={event:sum(r['event']==event for r in rows) for event in EVENTS},
        request_metadata=[r.get('metadata') for r in requests][-4:],
        actual_sent_hint_headers=sorted({name for r in headers for name in r.get('header_names',[])
            if name.startswith('sec-ch-ua')}),
        client_hint_negotiations=negotiations[-4:],latest_stream=streams[-1:])),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('condition',choices=['control','local_storage','native_identity'])
    parser.add_argument('--after',required=True)
    args=parser.parse_args()
    capture(args.condition,args.after)
