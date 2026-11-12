# run145 Thread resume r5

This is an isolated offline engineering revision of the run141 Thread resume diagnostic, based on run143 r4. It retains the 23-prefix contract, frozen v2/v3/Center/Thread prompts and sources, exact Q3-only v2/v3 prompt change, existing generation/reviewer plan, and the pending/held boundary. No musical candidate is selected or judged by this diagnostic.

## Disk evidence and parse failures

Every mock task stores its exact prompt, raw output, metadata, and full request identity before parsing is allowed to determine success. A completed parse failure is indexed on disk with its parser error, sample identity, and raw bytes. A same-slot call after restart reads and verifies that failed evidence, then stops by default without resampling. Creating a second sample requires strict `allow_new_sample_on_parse_failure=True`, a strict integer total sample budget no greater than two, and a nonempty reason. The new sample has a separate immutable path and sampling identity; a second failure keeps its reason and raw evidence, and no third sample is possible.

The full 23-step mock plan now has one deliberately synthetic NLV at k2 in each of four chains. Each exact quote creates a separate match task bound to k, the step output hash, the then-current inventory hash, quote index/text, target step slot, prompt, output, metadata, and lineage. The match JSON passes `_stage_parse("match", ...)`; deletion then requires the exact mapped source row and its disk proof. `None` leaves inventory unchanged. The k3 prefix is checked against the post-match inventory, and Center lineage covers all 23 step outputs and all match evidence. The identical second run reopens and verifies match artifacts with zero new submissions.

## Muse target and receipt contract

A single alias boundary maps generic `Muse` / `external Muse` to `claude-proxy` / `muse-spark-1.3-contributor-free` over `mcp`. Both frozen Thread Muse schemas keep their own exact result shape, candidate mapping, exact quote rules, prompt/template/source bytes, seed, and task/request identities. Raw text without a verifier remains `raw_unverified` with zero real returns. A trusted sourcebound verifier must return the exact 27-field receipt schema binding logical task/request, source/template/mapping/seed/prompt hashes, raw response bytes and size, completed terminal, target, and requested/reported/actual provider-model-transport. The 25 fixed-value fields are compared directly; attestation class and terminal ID receive their own strict checks. `TEST_ONLY` receipts always report zero real returns and `NOT_PERFORMED` music acceptance. No actual Muse authentication is asserted.

The unverified v4 entry, partial v5, and in-flight v6 remain presence-only and are never imported or auto-selected. Strict preflight is read-only and stays `COMPLETION_PENDING`; `--real` exits 3 without model/CLI calls or writes. Mock runs cannot create `DONE`, modify `CENTER_v0`, or change production/gate/hold state.

## Verification

Run the regression suite with:

```powershell
python -X utf8 -I -B tools/tests/test_run145_thread_resume_r5.py
```

The suite uses local mock data only. Passing these engineering tests does not run any of the three works' `06_ACCEPTANCE_CRITERIA.md` and does not establish production readiness.
