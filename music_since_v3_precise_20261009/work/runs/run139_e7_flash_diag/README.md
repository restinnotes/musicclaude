# run139 E7 Flash diagnostic

Run139 is an isolated Op.60 engineering diagnostic. Its fixed configuration is gen=chooser=gflash, with gflash and luna_noweb as both auditors and judges. The input is frozen run130 Op.60 beads plus the run130:gpt56w inventory history. The historical producer is recorded as unknown because the source does not verify it.

The comparison uses a=the run139 reading view, b=run124 production B, and two c groups from run132. Both Op.60 c candidates are reconstructed V2A+Gemini anchors, not the original V2A source. Old source runs, prompts, templates, and CLAUDE files are read-only.

## Safety and execution

Importing go.py does not read the frozen production inputs, change environment variables, write files, or invoke a CLI. Direct execution is blocked. The optional tools/experiment_calls_v4.py entry is inspected lazily only after an explicit real-run attempt; even then the run remains blocked until that shared exact-artifact entry and its real CLI protocol have independent acceptance.

Offline tests inject a caller that writes complete files under a temporary directory: exact prompt, output, metadata, and terminal identity. These records use the explicit MOCK:run139_e7_flash_diag namespace and cannot be accepted as real resumes. The pipeline reparses exact output bytes; a parse_ok claim or cache-only response is insufficient. Completed parser failures remain immutable and a retry gets a new attempt directory. A queue_stop terminal immediately stops all following jobs and stages.

Run the offline suite from the repository root:

```powershell
python -I -B tools/tests/test_run139_e7_flash_diag.py
```

The code deliberately does not offer a CLI smoke path or submit model work. The offline mock is structural evidence only. It cannot complete the diagnostic or establish a content result.

## Required coverage

- why: exactly k2–23, with only inventory_after(k-1) supplied to each prompt;
- mech generation: exactly k1–23, followed by an audit from each configured reviewer for every generated relation;
- surface decisions: exactly k1–23, serially, with stable item identities and full KEEP/RETIRE/REPLACE/APPEND evidence;
- compare: both baseline groups × both judges × order 0/1/2, with every candidate placed in each of 甲/乙/丙 exactly once;
- Muse and two-w packs: full comparison prompts, candidate text hashes, source/template/driver locks, seed, order, and mapping. Muse remains pending; two-w remains held by run135 post_submit_ambiguous;
- reader/report artifacts: full selected content plus actual 展开可看 and 曲终回顾 text, all main WHY decisions, source identity limits, and lifecycle decisions.

Any later Muse return must also pass an independently supplied transport/model verifier, in addition to complete exact prompt/output/meta/terminal files, a full compare schema with candidate-grounded quotes, and the exact task-ID set. No verifier is currently accepted, so no review result can be ingested. The held two-w pack cannot be submitted or ingested by this run. Pack creation alone is not a review.

Completion is always FAILED or COMPLETION_PENDING; this diagnostic never writes DONE or reports production readiness. Missing Muse and two-w work keep it pending. The reused WHY/MECH/E7 contracts have known coverage limits, so the run cannot be described as a one-variable model win.
