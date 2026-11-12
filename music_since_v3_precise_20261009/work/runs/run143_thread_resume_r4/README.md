# run143 Thread resume r4

This new, offline-only harness follows `run141_thread_resume_r3` while retaining the frozen C7 step v2/v3, CENTER v0, THREAD_IDENT v0, and THREAD_COMPARE v0 prompt bytes. The sole v2/v3 prompt difference remains in question 3. The run133 legacy control remains `not_loaded_no_exact_disk_proof`; no old producer identity is inferred.

## Real-entry preflight

`python -X utf8 -I -B runs/run143_thread_resume_r4/go.py --real` performs the read-only strict preflight and exits blocked. It does not import a shared entry, call a CLI, submit work, create run artifacts, or read secrets. A present v4 shared entry is unverified; partial v5 is unusable; the in-flight v6 work is never auto-selected. Dependencies are not imported or claimed verified. Real generation and review remain blocked.

## Identity and response validation

- Local reusable evidence must have `execution_mode` exactly `mock_only`. Missing/unknown modes fail; an explicit unsupported real mode stays `COMPLETION_PENDING`. The mock request ID, producer kind/model/adapter/revision/transport/provider, adapter hash, and slot hash must all match that exact slot.
- Raw responses and metadata require complete strict JSON: no prefix/trailer, second value, duplicate key, `NaN`/infinity, scalar top level, or wrong frozen schema. C7 step and center fields are exact; no fields are defaulted away or semantically trimmed.
- `validate_muse_raw_unverified` applies fixed THREAD_IDENT v0 and THREAD_COMPARE v0 schemas and checks candidate-specific, exact quoted text. It returns `raw_unverified`, `real_return_count: 0`, and `music_acceptance: NOT_PERFORMED`. Caller-selected schema, provider, transport, and model labels do not authenticate anything.
- `validate_muse_return` remains pending unless an independently trusted identity verifier for a controlled archive is supplied. Its receipt must bind the exact raw response bytes and hash, task/logical task/request ID, source/template/mapping/seed/prompt hashes, completed terminal, and requested/reported provider/model/transport. The in-suite mock receipt tests only the interface and is not a backend certification or a music success.
- The mock full-chain exercise proves temporary artifact integrity and zero-new-submit reuse only. Mock review results do not count as true schemas or music acceptance. An independent judge is still required; completion stays `COMPLETION_PENDING`, production stays false, and no gate or hold changes.

Run the regression suite with `python -X utf8 -I -B tools/tests/test_run143_thread_resume_r4.py`. It invokes only temporary local fixtures and mock code.
