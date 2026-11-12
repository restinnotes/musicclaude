# run141 Thread resume r3

**Completion state: `COMPLETION_PENDING`.** No `DONE` marker is written. The run141-r2 claim is not treated as evidence because this workspace has no corresponding artifacts. This implementation is an orchestration and integrity harness; it does not create candidate prose, make a musical acceptance decision, or claim that mock outputs are results.

## Scope and frozen protocol

- `C7_STEP_v2` and `C7_STEP_v3` are read from the existing prompt files and checked for exactly one contiguous change on question 3. Both variants use the same frozen 23-bead source. Each version/model chain builds its own sequential History prefix from its exact preceding parsed steps and required no-longer-valid match evidence. The associated `CENTER_v0` input cites all 23 output SHA256 values from that one chain.
- The planned generation matrix is `gpt56w` and `gpt6w` × v2/v3. Review coverage is the exact set `gpt56w`, `gpt6w`, `gflash`, `luna_noweb`, and external Muse. Reviewer coverage is checked by identity sets, not counts. Self-review entries carry an explicit marker and raw external reviews stay `raw_unverified` until independently normalized.
- Existing run133 GPT-5.6w material is not loaded because exact disk/provenance proof is incomplete. If later verified, it may be labeled `frozen_control_only`; it cannot stand in for a new GPT-5.6w/GPT-6w matched prompt comparison. New Opus and Sol work is excluded.
- Any source reuse requires disk metadata, exact prompt bytes, exact output bytes, recomputed parse equality, full job identity, producer identity, and matching SHA256 values. Cache-only records do not qualify. Multiple successful records for one slot are an ambiguity error. Missing legacy producer identity remains unrecorded; this code never fills it in.
- Muse task packs contain the complete prompt, template text, source text, mapping, seed, and hashes inline. The validator rejects altered bindings and file-read references. A pack alone does not count as a Muse review: a real result must include transport, provider, model, schema, raw response, and exact original-text quotations.
- Queue stop marks remaining jobs in the current stage stopped and prevents every later stage from starting. Failed slots are never retried over prior success artifacts.

## Commands

Run the isolated, full mock chain from the repository root:

```powershell
python -I runs/run141_thread_resume_r3/go.py --mock
```

The mock writes only below a temporary directory, verifies every artifact from disk, then repeats the same plan and requires zero new submissions on the second pass. Its terminal state remains `COMPLETION_PENDING`; mock responses cannot satisfy production acceptance.

Read-only production preflight:

```powershell
python -I runs/run141_thread_resume_r3/go.py --strict
```

At implementation time `tools/experiment_calls_v4.py` is absent. The strict path therefore returns `COMPLETION_PENDING`, does not import the old runner, and does not submit any jobs. If a v4 file later appears, it remains blocked until its exact transport/provenance protocol is independently accepted. No actual CLI, model, network, or subdelegate call is made here.

Run the offline test file:

```powershell
python -I tools/tests/test_run141_thread_resume_r3.py
```

## Limits

No generation, matching, review, or Center output from a live provider is present. The two planned `w` models are held; reviewers and Muse have no true returns. Production completion, external self-evaluation, canonical normalization, and independent musical judgment remain unverified. Freeze hashes cover source, templates, driver, and configuration; changing any requires a new run ID.
