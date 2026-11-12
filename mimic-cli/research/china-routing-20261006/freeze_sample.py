"""Commit an explicitly reviewed domestic-first sample; never discover or select overseas SKUs."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from completed_reports import completed_files

HERE = Path(__file__).resolve().parent

def freeze(path, approval_reference, review_mode='human'):
    target = HERE / 'sample-freeze-v1.json'
    if target.exists():
        raise SystemExit('v1 already frozen; preserve it and preregister a separate version for corrections')
    payload = json.loads(path.read_text(encoding='utf-8-sig'))
    if not isinstance(payload, dict) or not isinstance(payload.get('skus'), list) or not payload['skus']:
        raise SystemExit('Reviewed input needs a nonempty skus list')
    if payload.get('overseas_sku_research_before_freeze') is not False:
        raise SystemExit('A domestic-first no-overseas-research attestation is required')
    if not isinstance(payload.get('exclusion_log'), list) or not isinstance(payload.get('category_gaps'), list):
        raise SystemExit('Keep explicit exclusion_log and category_gaps, including empty lists when appropriate')
    identifiers = set()
    for row in payload['skus']:
        required = ['sku_id', 'category_id', 'brand', 'model', 'exact_variant',
                    'domestic_evidence', 'domestic_selection_rule', 'sampling_stratum']
        required_nonnull=[key for key in required if key!='model']
        if not isinstance(row, dict) or any(not row.get(key) for key in required_nonnull):
            raise SystemExit('Each frozen SKU must have ' + ', '.join(required))
        if 'model' not in row:raise SystemExit('Keep model field explicit, including null if manufacturer model number not observed')
        if not row.get('model') and not (row.get('item_id') and row.get('domestic_product_url') and row.get('exact_variant_verified') is True):
            raise SystemExit('Null model needs concrete item ID, product URL and mg-verified exact variant; no invented manufacturer number')
        if row['sku_id'] in identifiers:
            raise SystemExit('Duplicate sku_id')
        identifiers.add(row['sku_id'])
        if row['sampling_stratum'] not in ['domestic_head', 'domestic_opportunity']:
            raise SystemExit('Keep domestic-head and domestic-opportunity strata explicit')
    for job in ['W1-A', 'W1-B', 'W1-C', 'W2-A', 'W2-B', 'W2-C']:
        try:
            completed_files(job)
        except ValueError as error:
            raise SystemExit(str(error))
    input_digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if review_mode == 'delegated_coordinator':
        authorization = HERE / 'delegated-completion-authorization.json'
        review = HERE / 'domestic-sample-coordinator-review.json'
        if not authorization.exists() or not review.exists():
            raise SystemExit('Delegated authority and an actual recorded source/model review are both required')
        review_data = json.loads(review.read_text(encoding='utf-8'))
        if review_data.get('review_performed') is not True or review_data.get('reviewed_input_sha256') != input_digest:
            raise SystemExit('Coordinator review is missing or does not match the concrete sample')
    payload.update(version=1, frozen_at_utc=datetime.now(timezone.utc).isoformat(),
        review_mode=review_mode, review_authority_reference=approval_reference,
        human_review_performed=review_mode == 'human', reviewed_input_sha256=input_digest,
        intended_population='domestically evidenced candidates across 18 categories; not a probability sample',
        weights_policy='Unobserved GMV weights remain missing; overlapping categories need explicit reconciliation',
        overseas_unavailable_policy='retain denominator; distinguish verified absence from not observed/search blocked')
    encoded = json.dumps(payload, ensure_ascii=False, indent=2).encode('utf-8')
    # Exclusive create is the gate. A second operation cannot overwrite a frozen sample.
    with target.open('xb') as handle:
        handle.write(encoded)
    digest = hashlib.sha256(encoded).hexdigest()
    (HERE / 'sample-freeze-v1.sha256').write_text(digest + '  sample-freeze-v1.json\n', encoding='utf-8')
    print(json.dumps({'path': str(target), 'sha256': digest, 'sku_count': len(payload['skus'])}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reviewed_sample', type=Path)
    parser.add_argument('--approval-reference', required=True,
        help='Actual human approval/message reference, not an invented approval')
    parser.add_argument('--review-mode', choices=['human', 'delegated_coordinator'], default='human')
    args = parser.parse_args()
    freeze(args.reviewed_sample, args.approval_reference, args.review_mode)
