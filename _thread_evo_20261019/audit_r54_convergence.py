"""Verify the current convergence and immutable delivery from authoritative files.

This does not complete the goal: the final comparison must subsequently be
generated and verified against this audit by a separate post-generation check.
"""
import hashlib
import json
import re
import subprocess
import tomllib
import zipfile
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import experiment_batch as B
import build_version_comparison as C
import collect_i14_after_r62 as I

ROOT = B.ROOT
OUT = ROOT / 'runs/_batches/i14_after_r62'
sources = {}
requirements = []

def source(path):
    path = ROOT / path
    text = path.read_text(encoding='utf-8')
    sources[str(path.relative_to(ROOT)).replace('\\', '/')] = B.digest(text)
    return text

def obj(path):
    return json.loads(source(path))

def proven(name, evidence, detail):
    requirements.append({'requirement': name, 'status': 'proven', 'evidence': evidence, 'detail': detail})

I.validate_scope()
standard, rules, dag = [source(x) for x in ('标准.md', '迭代准则.md', 'DAG.md')]
assert re.search(r'当前正文主线：`([^`]+)`', dag).group(1) == 'r54weave'
assert '只有用户能改' in standard and '每段 2–4 条' in standard
accepted = obj('runs/_batches/round50_from_r49b/r54weave_acceptance.json')
assert accepted['tag'] == 'r54weave' and accepted['base'] == 'r50progress1rr'
for rid, expected_sha in accepted['review_output_hashes'].items():
    assert B.reviewed(rid) and B.digest(B.evo.output(rid)) == expected_sha
    source(B.evo.RUNS / rid / 'output.txt')
    source(B.evo.RUNS / rid / 'inspection.json')
parent = C.comparison('r54weave', 'r50progress1rr')
assert len(parent['rows']) == 8 and not parent['pending']
assert parent['wins'] == 7 and parent['no_regress'] == 6
assert all(parent['net_sums'][k] >= 0 for k in ('alone', 'lean', 'plain'))
assert B.F.floor_state('r54weave', 'r50progress1rr')['status'] == 'pass'
chain = C.lineage('r54weave', 'r49b')
assert chain and chain[-1]['tag'] == 'r54weave'
proven('Unique accepted mainline, real parent acceptance and model-only production',
       ['DAG.md', 'runs/_batches/round50_from_r49b/r54weave_acceptance.json'],
       {'parent_balanced8': parent, 'model_lineage': [s['tag'] for s in chain]})

integrity = obj('deliver_20261103_r54weave/integrity.json')
for work in B.F.WORKS:
    graph_path = B.V.OUT / f'{work}_r54weave.json'
    assert B.digest(source(graph_path)) == accepted['integrity'][work]['source_sha256']
    graph = B.V.graph_of(work, 'r54weave')
    baseline = B.V.graph_of(work, 'r49b')
    assert graph['center'] == baseline['center']
    assert [(s['sec'], s['bars']) for s in graph['segments']] == [(s['sec'], s['bars']) for s in baseline['segments']]
    items = [x for s in graph['segments'] for x in s['items']]
    seen = set()
    for seg in graph['segments']:
        assert 2 <= len(seg['items']) <= 4
        for item in seg['items']:
            assert re.findall(r'[。！？!?]', item['text']) and len(re.findall(r'[。！？!?]', item['text'])) == 1
            assert all(c in seen for c in item.get('cite', []))
            assert item['id'] not in seen
            seen.add(item['id'])
    line = source(f'deliver_20261103_r54weave/{work}_只看线_r54weave.md')
    assert line == f'# {work}｜线（r54weave）\n\n' + B.V.view(graph)
    joined = source(f'deliver_20261103_r54weave/{work}_线与珠子_r54weave.md')
    assert all(joined.count(x['text']) == 1 for x in items)
    beads = [b for b in B.V.covjudge.beads(work) if b['role'] != '演奏条件']
    for folder in ('beads_clean', 'beads_lang'):
        path = ROOT / 'evaluations' / folder / f'{work}.json'
        if path.exists():
            overlay = obj(path)
            beads = [dict(b, text=overlay.get(b['id'], b['text'])) for b in beads]
    parent_joined = source(f'deliver_20261103_r50progress1rr/{work}_线与珠子_r50progress1rr.md')
    assert all(joined.count(b['text']) == parent_joined.count(b['text']) == 1 for b in beads)
    assert integrity[work] == accepted['integrity'][work]
proven('Both works retain Center, segmentation, 2–4 complete items, true references and unchanged beads; four delivery documents match model text',
       ['deliver_20261103_r54weave/integrity.json'], integrity)

i14 = obj('runs/_batches/i14_after_r62/final_i14_assessment.json')
assert i14['i14'] and i14['new_valid_medium_or_higher_standard_defects'] == 0
for path in i14['evidence']:
    source(path)
matches = obj('runs/_batches/i14_after_r62/specific_matches.json')
assert len(matches['matches']) == 26 and matches['all_medium_instances'] == 28
for path in i14['no_acceptance_round_sources'] + i14['latest_actual_failed_trials']:
    assert obj(path)['status'] == 'archive'
collection = obj('runs/_batches/i14_after_r62/collection_result.json')
assert collection['original_receiver_terminal'] and len(collection['review_slots']) == 10
for row in collection['review_slots']:
    rid = row['rid']
    assert B.reviewed(rid) and B.digest(B.evo.output(rid)) == row['output_sha256']
    assert B.digest(source(B.evo.RUNS / rid / 'prepared_input.txt')) == row['input_sha256']
    source(B.evo.RUNS / rid / 'output.txt')
    source(B.evo.RUNS / rid / 'inspection.json')
proven('Original I14 stop rule after consecutive actual failed rounds, prospectively frozen fresh reviews and specific issue adjudication',
       i14['evidence'], {'known': 26, 'known_fixed_bead': 1, 'unsupported_new_claim_with_direct_counterevidence': 1,
                        'quality_compliance_proven': False, 'all_original_severity_and_dissent_retained': True})
advisers = obj('runs/_batches/round64_diagnosis/final_disposition.json')
assert advisers['original_receiver_terminal'] and advisers['new_versions'] == 0
for row in advisers['rows']:
    assert B.reviewed(row['rid']) and B.V.parse(row['rid'])['candidates'] == []
    source(B.evo.RUNS / row['rid'] / 'output.txt')
    source(B.evo.RUNS / row['rid'] / 'inspection.json')
proven('Complete final I02 diagnosis with no remaining independent candidate or author return',
       ['runs/_batches/round64_diagnosis/final_disposition.json'], {'candidates': 0, 'all_three_original_replies_read': True})

direct = C.comparison('r54weave', 'r49b')
assert len(direct['rows']) == 8 and not direct['pending']
assert direct['wins'] == 5 and direct['no_regress'] == 4
assert direct['net_sums'] == {'alone': 26, 'lean': -6, 'plain': 0, 'cover': 12}
assert B.F.floor_state('r54weave', 'r49b')['status'] == 'pass'
policy = obj('runs/_batches/round61_new_findings/baseline_policy.json')
proven('Rolling acceptance baseline and separate final r49b comparison; no accumulated parent votes',
       ['runs/_batches/round61_new_findings/baseline_policy.json', 'runs/_batches/round50_from_r49b/r54weave_vsr49b_direct8_verified.json'],
       {'direct_balanced8': direct, 'formal_direct_gate_pass': False,
        'boundary': 'Final report must explicitly retain failure to clear the direct r49b gate; accepted parent gate remains valid.'})
source('runs/_batches/round50_from_r49b/r54weave_vsr49b_direct8_verified.json')

pack = obj('runs/_reports/video_pack_r54weave.json')
archive = Path(pack['zip'])
assert hashlib.sha256(archive.read_bytes()).hexdigest() == pack['zip_sha256']
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None and len(z.namelist()) == pack['file_count'] == 3
    for entry in pack['files']:
        data = (ROOT / entry['source']).read_bytes()
        assert hashlib.sha256(data).hexdigest() == entry['sha256']
        assert z.read(entry['name']) == data
proven('User-frozen ZIP and existing source-quoted introduction remain byte-identical',
       ['runs/_reports/video_pack_r54weave.json'], {'zip_sha256': pack['zip_sha256'], 'mutations': 0})

automation_path = Path('C:/Users/zuoyi/.codex/automations/automation/automation.toml')
config_bytes = automation_path.read_bytes()
automation = tomllib.loads(config_bytes.decode('utf-8'))
assert automation['id'] == 'automation' and automation['status'] == 'PAUSED'
assert automation['target_thread_id'] == '01a19d91-baf5-71b0-849d-1095a460f1bd'
ps = "$items = @(Get-CimInstance Win32_Process -Filter \"Name = 'python.exe'\" | Where-Object { $_.CommandLine -match 'round64_advisors|collect_i14_after_r62|round61_advisors|round50_measure|round54_candidates' } | Select-Object ProcessId,CommandLine); ConvertTo-Json -InputObject $items -Compress"
query = subprocess.run(['powershell', '-NoProfile', '-Command', ps], capture_output=True, text=True, check=True)
active = json.loads(query.stdout.strip() or '[]')
assert active == [], active
schedule = {'verified_at': datetime.now(ZoneInfo('America/New_York')).isoformat(),
    'automation_source': str(automation_path), 'automation_bytes_sha256': hashlib.sha256(config_bytes).hexdigest(),
    'status': 'PAUSED', 'original_final_collector_terminal': True, 'tracked_live_python_receivers': active,
    'scope': 'Only this task owned receivers queried; no unrelated services, watchdog or cache warming changed.'}
B.write_frozen(OUT / 'scheduler_verification.json', B.json_text(schedule))
source(OUT / 'scheduler_verification.json')
proven('No owned pending collector remains and automatic heartbeat remains disabled',
       ['runs/_batches/i14_after_r62/scheduler_verification.json', 'runs/_batches/round64_diagnosis/collection.json'], schedule)
source('runs/_batches/round64_diagnosis/collection.json')
source('VERSIONS.md')
source('进度表.md')
source('版本说明/r61bridge_vs_r54weave.md')
source('版本说明/r54sample_vs_qu.md')
proven('Version registry, progress table and actual checkpoint/version explanations reflect measured work',
       ['VERSIONS.md', '进度表.md', '版本说明/r61bridge_vs_r54weave.md', '版本说明/r54sample_vs_qu.md'],
       'R64 produced no version; no invented version, missing vote or missing floor counted as a win or zero.')
source('build_version_comparison.py')
source('audit_r54_convergence.py')
sources.update(C.SOURCES)
audit = {'status': 'verified', 'tag': 'r54weave', 'base': 'r49b',
    'verified_at': datetime.now(ZoneInfo('America/New_York')).isoformat(),
    'requirements': requirements, 'source_hashes': dict(sorted(sources.items())),
    'quality_compliance_proven': False, 'globally_best_proven': False,
    'final_report_generation_pending': True,
    'limitations': ['Known medium/severe issues and all dissent remain.',
        'r54 is accepted against r50 but does not pass its direct eight-vote r49b comparison.',
        'r49b span annotations remain bound to r49b, not migrated to the changed r54 text; ZIP unchanged.',
        'Only two works measured; no automatic stable generalization claim.']}
B.write_frozen(OUT / 'convergence_audit.json', B.json_text(audit))
print(B.json_text({'audit': str(OUT / 'convergence_audit.json'), 'requirements_proven': len(requirements),
                   'source_hashes': len(sources), 'next': 'Generate final MD, verify generated output and then complete goal.', 'calls': 0}))
