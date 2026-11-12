---
name: no-self-candidate
description: "In the music content-layer runs, the orchestrator (me) must not act as a synthesis/content candidate; skip anything that involves me producing content"
metadata:
  node_type: memory
  type: feedback
  originSessionId: f5c661df-9026-436a-99d1-94c3c437c97f
  modified: 2026-09-25T04:23:34.795Z
---

I must not produce content myself as a candidate (e.g. writing the synthesis article as the "编排者自己" candidate). Skip every step that involves me generating content; only external models (gpro, gflash, luna, muse) are candidates.

**Why:** user interrupted on 2026-09-25 when I started writing the synthesis myself: "你不允许自己做啊 我们先不让你参与进去 涉及你的可以先跳过".

**How to apply:** my role stays orchestration: prompt edits, attribution, reviews, stage decisions. See [[delegation-split]].

**Exception (user, 2026-09-27):** the user asked to test Claude Opus 5.5 (via a separate `claude -p` process, runner keys `opus` / `opus_web`) and GPT-6 Sol (codex, keys `sol` / `sol_noweb`) on the latest chain versions. That is an external candidate run the user requested, not me writing content in this session. Because Opus shares my model family, blind reviews that include Opus output should also use a non-Claude reviewer (e.g. the GPT-6 Luna agent) and check agreement.
