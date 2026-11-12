"""Final four-run verification, including the failed repeat and rollback."""
from datetime import datetime,timezone
import hashlib
import json
from build_mg_storage_pair import OUT,SOURCE,docker
from run_mg_storage_probe import container_memory_snapshot


def main():
    manifest=json.loads((OUT/'matched-pair.json').read_text())
    source=json.loads(docker('inspect',SOURCE))[0]['State']
    assert not source['Running'] and source['FinishedAt']==manifest['source_finished_at']
    rows=[]
    for label in ['hintsbaseline005','hintshigh002','hintshigh003','hintsrollback006']:
        folder=OUT/('cup-native_identity-'+label)
        file=folder/'diagnostics.json';data=json.loads(file.read_text())
        assert data['probe_assessment'] and data['local_screenshot_evidence']['complete']
        rows.append(dict(label=label,started_utc=data['timestamp'],finished_utc=data['finished_utc'],
            mode=data['requested_native_hint_mode'],answer=data['probe_assessment']['observed_answer'],
            total_seconds=data['elapsed_seconds'],
            ui_thinking_time=data['local_screenshot_evidence']['thinking_time_ui_labels'],
            actual_model=data.get('actual_model'),actual_effort=data.get('actual_reasoning_effort'),
            prompt_sha256=data['prompt_sha256'],native_hint_evidence=data['diagnostics']['native_hint_experiment'],
            memory=data['memory'],screenshots=data['local_screenshot_evidence'],
            diagnostic_file=str(file),diagnostic_sha256=hashlib.sha256(file.read_bytes()).hexdigest()))
    observer=max(OUT.glob('observer-native_identity-*.json'),key=lambda p:p.stat().st_mtime)
    events=json.loads(observer.read_text())
    start=rows[0]['started_utc'];end=rows[-1]['finished_utc']
    requests=[e for e in events if e['event']=='generation_wire_request' and start<=e['utc']<=end]
    headers=[e for e in events if e['event']=='generation_wire_cookie_metadata' and start<=e['utc']<=end]
    assert len(requests)==4 and len(headers)==4
    for row,request,header in zip(rows,requests,headers):
        row['wire_metadata']=request['metadata']
        row['sent_hint_names']=sorted(k for k in header['header_names'] if k.startswith('sec-ch-ua'))
    a=rows[1];b=rows[2]
    assert a['wire_metadata']==b['wire_metadata']
    assert a['native_hint_evidence']['supplied_headers']==b['native_hint_evidence']['supplied_headers']
    memory=container_memory_snapshot('yi-mg-native-identity-20261007')
    assert memory['events']['oom_kill']==0
    report=dict(utc=datetime.now(timezone.utc).isoformat(),production_restored=False,
        verified_repeatable_header_fix=False,original_profile_modified_by_this_turn=False,
        original_container_state_unchanged=True,runs=rows,
        observer_file=str(observer),observer_sha256=hashlib.sha256(observer.read_bytes()).hexdigest(),
        final_container_memory=memory,
        valid_answers=[r['answer'] for r in rows],
        same_recorded_generation_metadata_in_high_hint_pair=True,
        same_actual_native_supplied_header_values_in_high_hint_pair=True,
        first_8_still_without_browser_context=True,
        caveats=['The 8 response was captured from completed UI output and native screenshots, but its independent CDP stream collector did not retain a complete DONE record.',
            'The baseline-to-first-high transition also changed notification permission metadata. The two high-hint trials have equal permission metadata.',
            'Cookie header length changed by five bytes between the high-hint trials; individual cookie value changes were not retained.',
            'High-hint trials observed the same frontend filenames, but the second did not retain both asset body hashes.',
            'Earlier failed preparation attempts are not model answers; some were accompanied by experimental-container OOM.',
            'Observed request summaries do not cover all dynamic server and client state.'],
        conclusion='Real high-entropy hints were sent, but the repeat returned 6. The hints alone are not a demonstrated stable restoration. Missing browser_context is also insufficient as a unique explanation.')
    file=OUT/'native-hint-verification-summary.json'
    with file.open('x',encoding='utf-8') as output:json.dump(report,output,ensure_ascii=False,indent=2)
    print(json.dumps(dict(report=str(file),answers=report['valid_answers'],
        seconds=[r['total_seconds'] for r in rows],ui_times=[r['ui_thinking_time'] for r in rows],
        restored=False,oom_kill=memory['events']['oom_kill'],original_untouched=True)))


if __name__=='__main__':main()
