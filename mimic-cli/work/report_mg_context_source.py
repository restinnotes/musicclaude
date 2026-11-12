"""Bind the offline storage and public frontend source findings."""
from datetime import datetime,timezone
import hashlib
import json
from build_mg_storage_pair import OUT,SOURCE,docker


def main():
    files=[OUT/'offline-settings-source-222551.json',OUT/'offline-settings-local_storage-222908.json',
        OUT/'verified-current-context-224053/report.json',OUT/'identity-comparison-report.json']
    source=json.loads(files[0].read_text());ablation=json.loads(files[1].read_text())
    public=json.loads(files[2].read_text())
    manifest=json.loads((OUT/'matched-pair.json').read_text())
    state=json.loads(docker('inspect',SOURCE))[0]['State']
    assert not state['Running'] and state['FinishedAt']==manifest['source_finished_at']
    assert all(not json.loads(docker('inspect',arm['container']))[0]['State']['Running']
        for arm in manifest['clones'].values())
    model_keys=lambda data:{k:v for k,v in data.get('persisted_atom_state_shape',{}).get('fields',{}).items()
        if 'model' in k or 'personalization' in k}
    report=dict(utc=datetime.now(timezone.utc).isoformat(),goal_turn_classification='progress',
        production_restored=False,model_generation_requests_this_turn=0,
        original_profile_modified=False,owned_experiment_browsers_running=0,
        source_container_state_unchanged=True,
        storage_findings=dict(source_local_storage_count=source['local_storage_count'],
            ablation_local_storage_count_after_normal_start=ablation['local_storage_count'],
            source_model_preference_records=model_keys(source),
            ablation_model_preference_records=model_keys(ablation),
            sanitized_model_preference_structure_equal=model_keys(source)==model_keys(ablation),
            source_theme_specific_model_visibility_rules=source.get('theme_model_visibility_rules'),
            max_actual_offline_memory_peak_bytes=max(source['memory_peak_bytes'],ablation['memory_peak_bytes']),
            offline_browser_hard_cap_bytes=512*1024**2,
            conclusion='Model list, last-selected model, and temporary personalization preferences survived the localStorage ablation in IndexedDB. The missing picker cannot be attributed to deletion of those preferences.'),
        frontend_findings=dict(
            public_asset_names_observed_in_actual_MG_trial=[a['basename'] for a in public['assets']],
            public_source_sha256={a['basename']:a.get('actual_sha256') for a in public['assets']},
            request_builder_module='c5U in 7078.903b5a88c7.js',
            context_getter_module='mRs in 646436.0f89f34edd.js',
            source_path=['Request builder calls mRs exported j getter when ordinary page context applies',
                'Getter reads browserContext.instanceId from extension-status data parsed from the document root attribute',
                'Only a nonempty validated string results in browser_context.instance_id being included'],
            cookie_or_local_storage_fallback_in_inspected_getter=False,
            side_chat_path_also_uses_extension_context=True,
            interpretation='This field is extension-supplied browser context, not an independently mandatory cookie/login identifier. Missing it in standalone MG is consistent with the inspected optional getter.',
            causal_regression_proven=False,
            native_Chrome_DOM_declaration_observation='Read-only attempt timed out before dispatch; presence or absence was not established',
            execution_equivalence_limit='Actual trial recorded these asset basenames, but its bounded collector did not retain their body hashes. Public source content was fetched and hashed separately; exact received or executed bytes at trial time remain unverified.'),
        remaining=dict(high_entropy_hint_causal_effect_unverified=True,
            server_tool_route_difference_causal_effect_unverified=True,
            local_storage_picker_failure_cause_unresolved=True,
            last_successful_MG_trial_had_no_browser_context=True,
            expected_answer_8_recovery_unverified=True),
        next_actions=['Focus passive body hashing on the two context modules during the next owned standard call so their exact received content is captured within the existing memory budget.',
            'Check native extension DOM declaration when the existing browser connection is responsive, without navigation or identity injection.',
            'Investigate the model-picker readiness failure while preserving cookies and persisted model preferences.',
            'Continue matching frontend, client-hint negotiation and tool-use behavior; require repeated actual 8 results before restoring production.'],
        inputs=[dict(file=str(f),sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in files])
    path=OUT/'context-source-and-storage-findings.json'
    assert not path.exists()
    path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(dict(report=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        production_restored=False,model_preferences_survived_ablation=True,
        browser_context_source='optional extension-status browserContext.instanceId getter',
        model_requests_this_turn=0,owned_experiment_browsers_running=0)))


if __name__=='__main__':main()
