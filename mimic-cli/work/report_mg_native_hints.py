"""Summarize only terminal, explicitly named MG hint trials."""
from datetime import datetime,timezone
import hashlib
import json
from build_mg_storage_pair import OUT,SOURCE,docker


def main():
    records={}
    for mode,label in [('baseline','hintsbaseline005'),('high_entropy','hintshigh002')]:
        run=OUT/('cup-native_identity-'+label)
        path=run/'diagnostics.json'
        data=json.loads(path.read_text())
        assert data.get('finished_utc') and data.get('probe_assessment')
        records[mode]=dict(run=str(run),started_utc=data['timestamp'],
            finished_utc=data['finished_utc'],elapsed_seconds=data['elapsed_seconds'],
            answer=data['probe_assessment']['observed_answer'],
            prompt_sha256=data['prompt_sha256'],
            actual_model=data.get('actual_model'),
            actual_effort=data.get('actual_reasoning_effort'),
            native_hint_evidence=data['diagnostics'].get('native_hint_experiment'),
            screenshot_evidence=data['local_screenshot_evidence'],
            memory=data['memory'],diagnostics_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    first=records['baseline']['started_utc'];last=records['high_entropy']['finished_utc']
    name='yi-mg-native-identity-20261007'
    code='''import json
from pathlib import Path
rows=[]
for line in Path('/app/state/yi-session-observer.jsonl').open():
 try:r=json.loads(line)
 except ValueError:continue
 if FIRST<=r.get('utc','')<=LAST and r.get('event') in EVENTS:rows.append(r)
print(json.dumps(rows))
'''.replace('FIRST',repr(first)).replace('LAST',repr(last)).replace('EVENTS',repr([
        'generation_wire_request','generation_wire_cookie_metadata','generation_stream_finished',
        'forensic_frontend_asset']))
    rows=json.loads(docker('exec',name,'/opt/venv/bin/python','-c',code))
    requests=[r for r in rows if r['event']=='generation_wire_request']
    headers=[r for r in rows if r['event']=='generation_wire_cookie_metadata']
    assert len(requests)==2 and len(headers)==2
    for mode,request,header in zip(records,requests,headers):
        records[mode]['wire_metadata']=request.get('metadata')
        records[mode]['actual_sent_ua_hint_names']=sorted(n for n in header.get('header_names',[]) if n.startswith('sec-ch-ua'))
    state=json.loads(docker('inspect',SOURCE))[0]['State']
    manifest=json.loads((OUT/'matched-pair.json').read_text())
    assert not state['Running'] and state['FinishedAt']==manifest['source_finished_at']
    cgroup=docker('exec',name,'cat','/sys/fs/cgroup/memory.events')
    report=dict(utc=datetime.now(timezone.utc).isoformat(),production_restored=False,
        source_container_unchanged=True,source_browser_or_cookie_modified=False,
        same_browser_container_and_profile=True,single_request_at_a_time=True,
        unused_owned_control_page_parked_blank_in_both_trials=True,
        browser_hard_cap_bytes=1610612736,cgroup_memory_events_after_trials=cgroup,
        manually_supplied_hints_are_actual_native_linux_metadata=True,
        windows_chrome_identity_reproduction_claimed=False,
        records=records,received_frontend_asset_hashes=[r for r in rows if r['event']=='forensic_frontend_asset'],
        stream_results=[r for r in rows if r['event']=='generation_stream_finished'],
        caveats=['Two sequential trials do not establish a unique cause.',
            'Web-push permission metadata changed between trials; other natural browser state changes may also occur.',
            'The four tested high-entropy hints do not reproduce the entire native Windows Chrome environment.',
            'Earlier preparation failures without generation requests are excluded from answer comparison.',
            'Original last successful MG 8 request had no browser_context.'])
    path=OUT/'native-hint-comparison.json'
    with path.open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
    print(json.dumps(dict(report=str(path),answers={m:r['answer'] for m,r in records.items()},
        actual_sent_headers={m:r['actual_sent_ua_hint_names'] for m,r in records.items()},
        production_restored=False,source_unchanged=True)))


if __name__=='__main__':main()
