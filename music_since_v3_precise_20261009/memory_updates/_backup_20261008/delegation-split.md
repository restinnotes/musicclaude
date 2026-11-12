---
name: delegation-split
description: "In the music content-layer runs, delegate all non-aesthetic work to Muse, HTML viewers to gemini-3.8-flash; keep only aesthetic/prompt judgment myself"
metadata:
  node_type: memory
  type: feedback
  originSessionId: f5c661df-9026-436a-99d1-94c3c437c97f
  modified: 2026-09-25T06:47:23.740Z
---

Delegate everything that does not involve aesthetic judgment to Muse (`opencode run --model opencode2api/muse-spark-1.3-contributor-free#xhigh`, prompt via stdin): scripts, file/meta bookkeeping, directory work, encoding, diff views, unit pre-screening, report assembly. HTML viewers/front-end pages go to gemini-3.8-flash-high via agy (stream-json stdin). Keep for myself only: prompt edits, behavior attribution, review verdicts, stage decisions.

**Why:** user said (2026-09-24) "只要不涉及审美的东西都可以交给muse做 尽量减少你自己的工作量" and "html查看器这种东西交给gemini3.8flash做".

Reinforced 2026-09-25: "机械性质的工作尽量交给muse去做…他自己也能研究怎么关闭网络代理的 你尽量只负责审美和提示词演进" — this includes infrastructure debugging (tool/network isolation, process babysitting, re-running failed jobs, coverage/statistics tables), not just writing scripts.

**How to apply:** before writing any tooling code myself, write an inline full-requirements task and hand it off; then only verify the result. Related: [[music-run-cli-invocation]].

Update 2026-09-30: for a while the user had Sonnet (high) sub-agents take over parallel mechanical tasks; then said "接下来别用 sonnet 了 回去用 muse". Default is Muse again for scripts/batch runs/summaries (tools/muse.py tools/muse_tasks/T*.md; muse.py writes its own .log — do not redirect stdout to that file).

- 2026-10-01: background runs that Muse starts from inside its task (go.py) die when the Muse session ends; after a Muse task reports 【任务完成】, check the run is alive and relaunch its go.py detached with PowerShell Start-Process (caches are reused).
