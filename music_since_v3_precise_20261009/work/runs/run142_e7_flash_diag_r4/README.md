# run142 E7 Flash diagnostic r4

This is a new, offline-only continuation of `run139_e7_flash_diag`. It keeps the frozen `WHY_GATE_v4`, `MECH_v1`, `MECH_AUDIT_v0`, `E7_SURFACE_v0`, and `E7_COMPARE_v0` prompt bytes and the original input/source lineage. The recorded run130 history producer remains `unknown`; the driver does not manufacture a legacy producer identity.

## Real-entry preflight

`python -X utf8 -I -B runs/run142_e7_flash_diag_r4/go.py --real` performs only a read-only presence check and exits blocked. It does not import or initialize `tools/experiment_calls_v4.py`, inspect secrets, modify `sys.path`, call a CLI, create run output, or submit a model request. A present v4 entry is still unverified; a v5 partial entry is unusable; the in-flight v6 work is never selected automatically. Shared-entry dependencies are not imported or claimed verified. The real route remains blocked.

## Response and evidence rules

- Model-facing response parsing accepts one complete JSON object/array, or one complete JSON fence. Prefixes, trailers, a second JSON value, duplicate keys, `NaN`/infinities, scalars, and wrong top-level types fail. Metadata uses the same strict JSON rules and exact artifact fields. The original output bytes remain the evidence bytes.
- Compare rankings and position-to-candidate maps must be complete bijections. Every quoted best/worst excerpt must be present in that position's mapped candidate; every hindsight quote and every explicit `only_here` citation is checked against that same candidate. Missing or mixed valid/fabricated quotations fail.
- A completed parse failure stops by default. Creating another immutable sample requires `allow_new_sample_on_parse_failure=True`, an explicit bounded `max_attempts`, and a nonempty `new_sample_reason`. Each sample has a distinct attempt and sampling identity; prior prompt/output/meta bytes are retained. Transport retry policy permits only proven `pre_submit` safety with a remaining budget. `post_submit_ambiguous` and `queue_stop` never retry.
- Offline mock outputs are synthetic test fixtures, not musical candidates or acceptance evidence. Full mock runs stay `COMPLETION_PENDING`; Muse review is not performed, two-w remains held, music acceptance is `NOT_PERFORMED`, and production remains false.

Run the regression suite with `python -X utf8 -I -B tools/tests/test_run142_e7_flash_diag_r4.py`. Tests use temporary directories and an injected mock caller only.
