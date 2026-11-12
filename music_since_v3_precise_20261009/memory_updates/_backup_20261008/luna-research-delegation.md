---
name: luna-research-delegation
description: "For web research / asset sourcing / image generation, delegate to Luna Max via codex exec instead of scraping myself"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 510a44a3-2505-4fb7-b337-27468386bd2a
  modified: 2026-09-28T16:43:08.364Z
---

When a task needs web research, asset collection or image generation, hand it to Luna Max via
`codex exec --skip-git-repo-check -m gpt-6-luna -c model_reasoning_effort="max" -c web_search="live" --json -` (prompt on stdin), rather than writing scrapers myself.

**Why:** user interrupted my own scraping (2026-09-28, retail-investing poster) and said "你用这种方式让luna max来帮你查资料、生图".

**How to apply:** write a brief file, launch parallel Luna sessions in background, keep composition/aesthetic judgment for myself. `-s danger-full-access` is blocked by the auto-mode classifier; use `-s workspace-write -c sandbox_workspace_write.network_access=true -C <dir>`. Related: [[music-run-cli-invocation]], [[delegation-split]].
