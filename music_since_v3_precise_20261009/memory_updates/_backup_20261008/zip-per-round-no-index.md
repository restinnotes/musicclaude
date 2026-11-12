---
name: zip-per-round-no-index
description: "From 2026-10-03 do not update index.html after runs; instead zip each finished round's work into Downloads"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 5b7665db-3470-493f-ac79-b22c507fb7f0
  modified: 2026-10-04T03:32:57.917Z
---

User (2026-10-03): stop updating index.html — not after each run, not at all for now. Instead, when a whole round of work is finished, pack everything from that round (new/changed notes, prompts, tools, muse_tasks, the round's runs/<run>/ dirs without outputs/raw and empty cwd dirs) into one zip in C:\Users\zuoyi\Downloads.

**Why:** the user evaluates progress by handing zips to another model; index rebuilds cost time and calls. Sizes are small enough to zip everything.

**How to apply:** overrides CLAUDE.md rule 7 ("每个 run 结束都要更新 index.html") until the user says otherwise. At the end of a round, build e.g. music_pipeline_round_<YYYYMMDD_HHMM>.zip with a short README of what's inside; mention the path in the report. Related: [[delegation-split]], [[music-run-cli-invocation]].
