# run144 E7 Flash diagnostic r5

This is an isolated offline engineering revision of the run139 diagnostic, based on run142 r4. It retains the frozen run130/run124/run132 inputs, E7/MECH prompt bytes, candidate contracts, blinded comparison mapping, and pending/held outcome. The legacy run130 producer remains unknown where source artifacts do not establish it.

## Request identity and immutable attempts

Before reuse, `Pipeline.execute` compares the full current identity against every prior record for the same logical slot: run and namespace, logical/request ID, step, key, requested/current model, prompt version, driver hash, frozen source/template producer hashes, exact UTF-8 prompt text, and prompt hash. A mismatch raises `IntegrityError` before creating another attempt; it never changes the key to find a cache entry.

A completed parse failure is preserved in the exact prompt/output/meta/terminal files and indexed with its parse error before the call stops. Default behavior is STOP. A new sample requires strict `True`, a strict integer total budget of at most two attempts, and a nonempty reason. Each sample gets a distinct sampling identity; failed samples remain indexed and are reverified after restart.

Transport retries use the same sampling identity and require an injected sourcebound proof verifier that binds the failed attempt to its logical request, current model/version, prompt bytes, input producer, sample identity, and retry index. A SHA string or caller `retry_safe` flag is not proof. A verified `pre_submit` failure may consume the remaining strict retry budget. Unverified, ambiguous, queue-stop, and exhausted failures preserve request/proof/error/raw/terminal diagnostic artifacts and write a persistent execution hold.

## External Muse boundary

The single canonicalization function maps the historical `Muse` / `external Muse` alias to `claude-proxy` / `muse-spark-1.3-contributor-free` over `mcp`. Packs bind six exact tasks, logical/request IDs, target, source bundle, prompt and template hashes, candidate mapping, seed, and candidate source hashes. Ingestion requires an independent sourcebound receipt with exact schema and byte-size/hash/terminal/target/provider/model/transport bindings. Without a verifier, results remain pending. Test-only receipts are labeled `TEST_ONLY`, count zero real returns, and never establish music acceptance.

The two-w slot remains held. Offline mock evidence stays `COMPLETION_PENDING`, `music_acceptance=NOT_PERFORMED`, and `production_ready=false`. `--real` performs only a read-only shared-entry presence check and exits 3; it does not import shared transport code, invoke a model/CLI, or write run output.

## Verification

Run the regression suite with:

```powershell
python -X utf8 -I -B tools/tests/test_run144_e7_flash_diag_r5.py
```

The r3 regression expected an implicit parse retry. r5 intentionally replaces that unsafe default with explicit authorization; the new regression checks both the default STOP and the explicitly budgeted immutable resample. Test fixtures are injected local mocks only.
