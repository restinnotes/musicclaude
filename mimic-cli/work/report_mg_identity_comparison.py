"""Bind completed local MG evidence into a safe diagnostic report."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from build_mg_storage_pair import OUT, ROOT, SOURCE, docker


def read(file):
    return json.loads(file.read_text(encoding='utf-8'))


def digest(file):
    return dict(file=str(file), sha256=hashlib.sha256(file.read_bytes()).hexdigest())


def main():
    arms = [('control', '001', 'observer-control-220657.json'),
            ('native_identity', '001', 'observer-native_identity-221442.json'),
            ('local_storage', '002', 'observer-local_storage-221819.json')]
    findings = []
    inputs = []
    asset_sets = {}
    for condition, label, observer_file in arms:
        run = OUT / ('cup-' + condition + '-' + label)
        diagnostic = read(run / 'diagnostics.json')
        rows = read(OUT / observer_file)
        inputs += [digest(run / 'diagnostics.json'), digest(OUT / observer_file)]
        wire = [r for r in rows if r.get('event') == 'generation_wire_request']
        sent = [r for r in rows if r.get('event') == 'generation_wire_cookie_metadata']
        stream = [record for r in rows if r.get('event') == 'generation_stream_metadata'
                  for record in r.get('metadata_records', [])]
        document = [r for r in rows if r.get('event') == 'client_hint_negotiation_observed'
                    and r.get('document_response')]
        asset_sets[condition] = {(r['basename'], r['body_sha256']) for r in rows
            if r.get('event') == 'forensic_frontend_asset' and r.get('observation_complete')
            and r.get('body_sha256')}
        findings.append(dict(condition=condition, finished_utc=diagnostic['finished_utc'],
            actual_answer=diagnostic.get('probe_assessment', {}).get('observed_answer'),
            elapsed_seconds=diagnostic['elapsed_seconds'],
            ui_thinking_time=diagnostic.get('local_screenshot_evidence', {}).get('thinking_time_ui_labels'),
            actual_wire_generation_requests=len(wire),
            wire_model_effort=[{k:r.get('metadata', {}).get(k) for k in
                ('model','thinking_effort','browser_context_present')} for r in wire],
            actual_sent_hint_names=sorted({name for r in sent for name in r.get('header_names', [])
                if name.startswith('sec-ch-ua')}),
            document_responses_observed=len(document),
            document_responses_with_accept_ch=sum(bool(r.get('accept_ch_present')) for r in document),
            server_ste=[r['server_ste_metadata'] for r in stream if 'server_ste_metadata' in r],
            tool_role_messages_observed=sum(r.get('message_author_role') == 'tool' for r in stream),
            assistant_python_recipients_observed=sum(r.get('message_recipient') == 'python' for r in stream),
            error=diagnostic.get('error'), memory=diagnostic.get('memory'),
            screenshot_evidence=diagnostic.get('local_screenshot_evidence')))
    manifest = read(OUT / 'matched-pair.json')
    states = {condition:json.loads(docker('inspect', arm['container']))[0]['State']
              for condition,arm in manifest['clones'].items()}
    source = json.loads(docker('inspect', SOURCE))[0]
    assert not source['State']['Running']
    assert source['State']['FinishedAt'] == manifest['source_finished_at']
    assert all(not state['Running'] for state in states.values())
    report = dict(schema=1, generated_utc=datetime.now(timezone.utc).isoformat(),
        objective='Diagnose current yi MimicGate answer 8 to 6 regression',
        production_restored=False, original_container_candidate_patch_applied=False,
        experiment_browsers_running=0, source_state_unchanged=True,
        original_Chrome_auth_untouched=True, original_profile_mutated=False,
        native_identity_candidate=dict(file=digest(ROOT/'src/browser/stealth.py'),
            opt_in_env='MIMICGATE_NATIVE_BROWSER_IDENTITY=1', enabled_only_on_owned_clone=True,
            actual_identity=read(OUT/'identity-native_identity.json')['identity'],
            effect='Preserve native navigator platform, UA and UAData; no fabricated Windows hint headers',
            result='Actual identity consistency verified, answer still 6'),
        preparation=[read(OUT/('preparation-'+condition+'.json')) for condition in manifest['clones']],
        findings=findings,
        partially_observed_common_control_candidate_js_assets=len(asset_sets['control'] & asset_sets['native_identity']),
        partially_observed_control_only_js_assets=len(asset_sets['control']-asset_sets['native_identity']),
        partially_observed_candidate_only_js_assets=len(asset_sets['native_identity']-asset_sets['control']),
        interpretation=[
            'Current opt-in native identity correction is insufficient to restore the expected 8 answer.',
            'Missing browser_context is not a sufficient standalone explanation: historical successful MG also lacked it.',
            'High entropy UA headers have not been forced or fabricated; observed documents did not request them via Accept-CH.',
            'Current model wire policy remains gpt-5-6-thinking with max effort; CLI xhigh mapping was verified.',
            'Tool-use and coding metadata differ from prior successful native Chrome observations; correlation is not a proven root cause.',
            'The localStorage ablation is inconclusive: model picker was absent and no generation POST was sent.',
            'Failed localStorage run 001 occurred before service readiness; run 002 stopped before submission. Neither is an answer trial.',
            'JS observation is bounded and incomplete; common hashes do not prove complete frontend or executed bytecode equivalence.',
            'Browser native high entropy JS values and HTTP client-hint negotiation are separate mechanisms.',
            'Two single-trial answers of 6 do not exclude interaction effects, intermittent recovery, or server-side changes.'
        ],
        next_investigation=[
            'Trace the native browser_context instance lifecycle without inventing or replaying opaque identifiers.',
            'Identify which cleared localStorage setting removes the model picker before a narrower reversible clone-only ablation.',
            'Compare native and MG tool routing, account feature state, frontend assets and full client-hint negotiation.',
            'Require two normal cup results and ordinary MG calls before declaring production restored.'
        ],
        primary_protocol_reference='https://developer.chrome.com/docs/privacy-security/user-agent-client-hints',
        inputs=inputs)
    file=OUT/'identity-comparison-report.json'
    if file.exists():
        raise RuntimeError('Report already exists; do not overwrite evidence')
    file.write_text(json.dumps(report, ensure_ascii=False, indent=2),encoding='utf-8')
    print(json.dumps(dict(report=digest(file),production_restored=False,
        results=[{k:r[k] for k in ('condition','actual_answer','elapsed_seconds','actual_wire_generation_requests')}
            for r in findings],experiment_browsers_running=0)))


if __name__ == '__main__':
    main()
