---
name: muse-delegate-early-stop
description: 10-08 — Muse via T3 delegate_task often ends its turn mid-task on long engineering work; read-only research tasks complete fine
metadata:
  node_type: memory
  type: project
  originSessionId: 496c3129-0e46-4f8b-ae50-c1fd2d5e7540
  modified: 2026-10-08T22:28:14.723Z
---

Observed 2026-10-08 (5 of 7 tasks): Muse (claude-proxy / muse-spark-1.3-contributor-free / xhigh) frequently "completes" after emitting a text-only status line (e.g. "Docker 已启动…", "拦截逻辑同步完…") with nothing committed; once it was "Provider turn failed". Read/index/case-mining tasks (baselines, increment cases, memory review) finished normally. Also: any background process Muse starts dies when its turn ends.

**Why:** cost a few hours of wall time on the gpt2 router/driver scripts before I switched.

**How to apply:** give Muse research/indexing/mining/stat tasks; for multi-file engineering, either chunk the task very small or do it yourself in the main session (Opus banned since 10-09, see [[dev-agent-sol-and-opus-subagents]]). Never let Muse own long-running processes — have it write go.py + dry-run, then launch from the main session as a tracked background job. Check disk/git state after every Muse "completion" rather than trusting its summary. Related: [[delegation-split]].
