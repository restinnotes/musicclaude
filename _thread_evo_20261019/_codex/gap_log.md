# GPT3 submission pacing change

2026-10-29

- Scope: only gpt3_call.py submission pacing and log fields; offline tests in _codex/test_gap.py.
- Read gpt3_call.py and evo.find_job. Current code stamps both command launch and process completion.
- Preserve existing slot byte locks, arguments, prompt/attachments, NO_WEB, model/effort checks, retries and stop rules.
- Existing background processes and real run directories must remain untouched.
- All text reads/writes use Python with explicit UTF-8. PowerShell stdin BOM is stripped before executing Python snippets.
- Original gpt3_call.py saved to _codex/gpt3_call.before_gap.py.txt for exact scope comparison.

- Implemented Popen launch and prompt-matched job polling under GATE, 180 s monotonic timeout, actual submitted UTC -> epoch STAMP, and first_chunk_ms non-null gate. Existing directories are excluded, including directories later touched by another process.
- communicate() stays inside the existing slot lifetime but outside GATE; post-completion STAMP write removed. Unknown real submission fields are null rather than inventing evidence.

## Scope verification

- slots unchanged
- _Serial unchanged
- stopped unchanged
- _fail unchanged
- prompt, NO_WEB, attachments and long-prompt preparation byte-for-byte unchanged
- stdout/stderr parsing, validation, logs apart from new fields, retries and stop rules byte-for-byte unchanged
- GAP default, STOP_WORDS, slots file and shared lock paths unchanged
- one STAMP write only; Popen + communicate replace run
- Python compile passed without pycache writes
- Saved review diff: _codex/gap_diff.patch. No edits to evo.py, mg_call.py, watchdog, cache warming, scheduled tasks, or background processes.
- Read-only reference SHA256 evo.py: 7309412fdfbee1ff550284d2bc0032eb3f8c55675274645f3e369ab0b0a8e8cc
- Read-only reference SHA256 mg_call.py: 1f50df2b0a3fe6483e90985a1a74d905b908f7cc5851b6dcfb1e9326a2c564fd

## Offline validation

- Initial suite: 7 tests passed in 14.041 s. Four real Windows worker processes, real msvcrt byte locks, scaled slow-upload delay 1.5 s and GAP 0.3 s, jitter fixed to zero. Measured actual-submit gaps: 1.5903, 1.0220, 0.9985 s; all >= GAP. Every follower launched after previous first_chunk; next launch overlapped previous response tail.
- Covered null and zero first_chunk, partially written JSON, stale same-prompt jobs, timeout with actual-submit evidence, timeout with no job (fallback to current time), exit after submit without chunk, early failure/retry, protection stop, strict model/max checks, web/NO_WEB, nonempty and empty attachments, long-prompt attachment and result/log parsing.
- Tests load evo.py with only its RUNS/GPT3_RUNS assignments replaced in memory before execution, redirect all other paths to TemporaryDirectory, audit against writes outside that directory and network activity, restrict Popen to the temporary fake .cmd, and disable bytecode creation. Production code and real model calls are never launched.
- Final source inspection found active CLI bin/gpt3.cmd -> tools/chatgpt_web/gpt3_cli.py and pro_bridge_http_probe.py:121 rstrips prompt before writing prompt.txt. Matching now mirrors rstrip without changing input/message. Fake CLI and trailing-whitespace web test updated accordingly; added malformed stdout JSON failure coverage. Re-running only because of these changes.

## Final result

- SUCCESS: final offline suite passed all 7 test methods (including multiple failure/stop subcases) in 14.927 s. Actual four-process submission gaps: 1.6753, 1.0155, 1.0282 s with GAP 0.3 s. Full output: _codex/gap_test_output.txt.
- Re-ran Python compilation and exact scope comparisons after the rstrip correction: passed. Confirmed production timeout 180 s and polling interval 1 s. Original slot/stopping helpers, preparation before attempts, and all result/failure handling after communicate are unchanged (except the two requested log fields). CLI command arguments are identical.
- Experimental semantics unchanged: prompts/input, web permission, tools, model/reasoning validation, attachments/bead inputs, review criteria, concurrency slot mechanism, GAP default and 0-10 s jitter, retries/failure counts/stopping rules. evo.py and mg_call.py reference hashes remain the same.
- No real model requests, real run-directory writes, real lock/STAMP writes, background-process stops/restarts, watchdog/cache changes, or scheduled tasks. Tests ran solely in temporary directories.

## Operational limits / material risks

- Existing six processes retain the old imported implementation and share production lock/STAMP paths. Until the user restarts them, mixed old/new callers cannot guarantee the new global pacing rule; their old completion-time writes can also replace the new stamp. They were not touched.
- Per requested behavior, a 180 s wait timeout releases GATE and logs a warning. If submission time is unavailable, STAMP falls back to current time and both log fields are null for that call; strict first-chunk ordering / true submission gaps cannot be proven on this fallback path. A following gap uses the stored fallback stamp if the previous true submission was unknown.
- Matching excludes preexisting directories and requires a newly created prompt-matched job. Independently launched legacy callers with identical prompts after t0 can remain ambiguous during mixed-version operation; after all callers adopt GATE this launch phase is serialized.
