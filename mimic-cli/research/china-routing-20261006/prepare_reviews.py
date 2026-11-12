"""Prepare identical raw evidence inputs for four independent mg judges, then a synthesizer."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from completed_reports import completed_files

HERE = Path(__file__).resolve().parent
ROLES = {
    'J1-methodology': 'Only audit selection/survivorship/sample-leakage bias, variant/price mismatches, login-state bias, stale prices, coupon contamination, freight/tariff errors. Identify exact affected job:claim or sku_id, consequence and repair. Do not replace data with guesses.',
    'J2-economic': 'Only audit demand weighting, overlapping GMV/category definitions, relevance, unit economics, logistics scaling and marketplace economics. Distinguish actual negotiated rates from hypothetical rates and commercial order aggregation from physical bulk import.',
    'J3-bear': 'Make the strongest evidence-supported case that this idea lacks a sufficiently large market. Use the same evidence as the bull. Quote evidence IDs, confront the strongest contrary evidence, and distinguish unproven from disproven.',
    'J4-bull': 'Make the strongest evidence-supported case for an overlooked global price-discovery failure. Use the same evidence as the bear. Quote evidence IDs, confront the strongest contrary evidence, and do not present missing observations as opportunity.',
}

def digest(text): return hashlib.sha256(text.encode('utf-8')).hexdigest()

def completed_report(job):
    try:
        _, report = completed_files(job)
    except ValueError as error:
        raise SystemExit(str(error))
    return report.read_text(encoding='utf-8')

def prepare_judges():
    audit = HERE / 'coordinator-source-audit.json'
    if not audit.exists():
        raise SystemExit('Coordinator source/claim audit has not been recorded')
    audit_data = json.loads(audit.read_text(encoding='utf-8'))
    if audit_data.get('review_performed') is not True:
        raise SystemExit('No actual coordinator review attestation; evidence pack is not ready')
    jobs = ['W' + str(number) + '-' + replicate for number in range(1, 9) for replicate in 'ABC']
    sections = []
    inputs = []
    for job in jobs:
        report = completed_report(job)
        _, original_path = completed_files(job)
        inputs.append({'job_id': job, 'response_sha256': digest(report), 'original_file_byte_sha256': hashlib.sha256(original_path.read_bytes()).hexdigest(), 'hash_representation': 'response_sha256 hashes UTF-8 text normalized to LF exactly as included in attached pack; original_file_byte_sha256 hashes the preserved original file', 'characters': len(report)})
        sections.append('\n=== RAW INDEPENDENT REPORT ' + job + '; SHA256 ' + digest(report) + ' ===\n' + report)
    frozen = (HERE / 'sample-freeze-v1.json').read_text(encoding='utf-8')
    raw_audits = (HERE/'mg-source-audits-untruncated.txt').read_text(encoding='utf-8')
    denominator_checks = (HERE/'audited-denominator-checks.json').read_text(encoding='utf-8')
    identity_note=(HERE/'prefreeze-identity-validation-note.json').read_text(encoding='utf-8')
    pack = '\n=== PREFREEZE IDENTITY VALIDATION LIMITATIONS ===\n'+identity_note+'\n=== FROZEN SAMPLE ===\n' + frozen + '\n=== MECHANICAL DENOMINATOR CHECKS, NOT ESTIMATED WEIGHTS ===\n' + denominator_checks + '\n=== MG SOURCE AUDIT INDEX ===\n' + audit.read_text(encoding='utf-8') + ''.join(sections) + '\n=== UNTRUNCATED INDEPENDENT MG SOURCE AUDITS ===\n' + raw_audits
    (HERE / 'judge-evidence-pack.txt').write_text(pack, encoding='utf-8', newline='\n')
    metadata = {'created_utc': datetime.now(timezone.utc).isoformat(), 'evidence_pack_sha256': digest(pack),
        'characters': len(pack), 'raw_reports': inputs, 'truncated': False,
        'input_capacity_check': 'Required against actual mg composer/context; no silent truncation permitted'}
    (HERE / 'judge-evidence-pack.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    for job, role in ROLES.items():
        folder = HERE / 'jobs' / job
        folder.mkdir(exist_ok=True)
        prompt = ('You are independent judge ' + job + '. You receive the same immutable evidence pack as the other three judges. '
            'You cannot see their outputs. Do not conduct new fact-gathering or invent new facts; the evidence base is closed. '
            'An agent claim is not a verified fact; use the coordinator audit grades. '
            'Do not vote, average incompatible prices, or count repeated citations as independent observations. '
            'Write in Chinese. Give decisive findings with exact job:claim / source IDs and sku_ids, '
            'contrary evidence, confidence, unresolved facts and the minimum repair/change-of-mind evidence. '
            'Your role: ' + role + '\nEvidence pack SHA256: ' + digest(pack) + '\n'
            'The attached judge-evidence-pack.txt contains the frozen sample, all 24 complete untruncated '
            'independent research reports and every independent mg source audit. Read the attachment '
            'before judging. Use file tools to inspect all 24 reports and the audits; do not infer '
            'unread content from the manifest. Include an input-completeness table listing each '
            'research job, its report hash and at least one concrete report-specific disagreement '
            'or material finding you actually inspected. If attachment parsing, context or tool '
            'access prevents full inspection, mark INPUT_INCOMPLETE, list missing jobs/sections '
            'and do not present a completed judgment. No silent truncation or majority vote. '
            'Keep the analysis focused and executable, approximately 2500 Chinese characters plus '
            'the input-completeness table. No new fact gathering; this evidence base is closed.\n'
            'Research input manifest:\n' + json.dumps(inputs,ensure_ascii=False))
        (folder / 'prompt.txt').write_text(prompt, encoding='utf-8')
        (folder/'attachments.json').write_text(json.dumps({'files':[{'relative_path':'judge-evidence-pack.txt',
            'filename':'judge-evidence-pack.txt','sha256':digest(pack)}]},indent=2),encoding='utf-8')
    print(json.dumps(metadata))

def prepare_synthesis():
    pack = (HERE / 'judge-evidence-pack.txt').read_text(encoding='utf-8')
    judges = ''.join('\n=== COMPLETED INDEPENDENT JUDGE ' + job + ' ===\n' + completed_report(job) for job in ROLES)
    brief = (HERE / 'original-brief.txt').read_text(encoding='utf-8')
    folder = HERE / 'jobs' / 'S1-final'
    folder.mkdir(exist_ok=True)
    full_inputs = '=== ORIGINAL USER BRIEF ===\n'+brief+'\n=== IDENTICAL RAW EVIDENCE PACK ===\n'+pack+judges
    freeze=json.loads((HERE/'sample-freeze-v1.json').read_text(encoding='utf-8'))
    mechanical={'artifact':'sample-freeze-v1.json',
        'file_sha256':hashlib.sha256((HERE/'sample-freeze-v1.json').read_bytes()).hexdigest(),
        'freeze_metadata':{k:v for k,v in freeze.items() if k!='skus'},
        'frozen_sku_count':len(freeze['skus']),
        'note':'The sample_frozen=false field belongs to the explicitly timestamped PREFREEZE identity-validation note, not the later immutable freeze. Missing C17 manufacturer models remain real limitations. Each W3/W4 logical report is a bundle of six disjoint 9-SKU batches; a 9/9 batch count must not replace the whole 54-SKU logical replicate denominator. Judge assertions are also claims; resolve against original artifacts and grades.'}
    full_inputs+='\n=== MECHANICAL ARTIFACT IDENTITY AND DENOMINATOR CLARIFICATION ===\n'+json.dumps(mechanical,ensure_ascii=False,indent=2)
    (HERE/'final-synthesis-evidence.txt').write_text(full_inputs,encoding='utf-8',newline='\n')
    prompt = ('You are the independent final adjudicator. Read all 24 untruncated original reports, '
        'the four independent judge reports, the frozen sample and source audit below. '
        'Do not majority-vote, silently average incompatible values, upgrade unverified sources or invent missing numbers. '
        'Resolve each material disagreement by evidence quality. Report missingness and correct denominators. '
        'Explicitly adjudicate whether any judge has generalized this research tool/session\'s access failure '
        'into a claim about normal consumers or the global market. Separate a research measurement failure, '
        'a demonstrated consumer price-discovery failure, and a proven profitable anomaly set; each needs '
        'its own evidence. Also distinguish no-go under current evidence from proof the actual market is small. '
        'Write the complete final output requested in the user brief, including all 12 questions, all 18 categories, '
        'both separate distributions, four shipping structures and separate architectures. '
        'Give all requested verdicts: broad/narrow/thin routing/full marketplace as well as shopping agent/logistics platform, '
        'Strong/Moderate/Weak/Rejected with confidence, decisive evidence, strongest counterargument and change-of-mind data. '
        'Use explicit source URLs and artifact/claim identifiers, and preserve confirmed/probable/speculative reasons. '
        'If data do not support a distribution, say so instead of constructing one. '
        'Finish with a concrete $10,000 uncertainty-reducing research program.\n'
        'All complete original inputs are in the attached final-synthesis-evidence.txt; SHA256 '
        +digest(full_inputs)+'. Read all inputs using available file tools. Include a completeness '
        'table for the 24 research reports and four judges, each with a specific inspected finding. '
        'If any input cannot be inspected, say INPUT_INCOMPLETE and identify exactly what failed; '
        'do not claim a complete synthesis. All missing real prices/rates/weights remain missing. '
        'Return the complete Chinese deliverable requested in the original user brief in the '
        'attachment, with explicit source URLs and evidence IDs. Do not invent quantiles from '
        'incomplete landed costs. This is the final report, not a plan.\n')
    (folder / 'prompt.txt').write_text(prompt, encoding='utf-8')
    (folder/'attachments.json').write_text(json.dumps({'files':[{'relative_path':'final-synthesis-evidence.txt',
        'filename':'final-synthesis-evidence.txt','sha256':digest(full_inputs)}]},indent=2),encoding='utf-8')
    print(json.dumps({'prompt_sha256': digest(prompt), 'characters': len(prompt), 'truncated': False,
        'raw_reports': 24, 'judges': 4, 'not_sent': True}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['judges', 'synthesis'])
    args = parser.parse_args()
    if args.stage == 'judges': prepare_judges()
    else: prepare_synthesis()
