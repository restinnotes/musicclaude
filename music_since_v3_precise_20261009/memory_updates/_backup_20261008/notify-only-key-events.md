---
name: notify-only-key-events
description: "Don't relay every progress event to the user; only failures, completions and conclusions"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 5b7665db-3470-493f-ac79-b22c507fb7f0
  modified: 2026-10-06T01:02:20.576Z
---

Only tell the user about key events (failures needing attention, run completions, conclusions). Do not post a message for every monitor progress line.

**Why:** 10-05 the user complained ("别这么频繁通知我 关键的再通知我") after I echoed each per-window clustering result.

**How to apply:** Monitors should filter to FAIL/Traceback/DONE only; stay silent on routine progress. Also keep delegating mechanical work (scripts, reports, fixes) to Muse per [[delegation-split]].
