---
name: thread-structured-output-and-advisor
description: 10-21 user — keep pushing autonomously; when out of ideas, hand current results to a reviewer model for next-step advice; final Thread output should be structured (not prose) to serve video production
metadata:
  type: feedback
---

User (2026-10-21): "你继续尽量多的继续去推进 … 每次所有手头做完都交给评审问问他建议继续往哪里推进如果你没有思路的话 … 我们目前还是优化内容 … 最后产出会是结构化的 … 不是散文式的 这样或许服务给下一步的做视频会好的多".

**Why:** the user is often away. Progress should not stall waiting on them. A structured output (per segment: headline mechanism, causes with segment refs, revisions, direction, bead lines) maps directly onto video timing.

**How to apply:**
- After each batch finishes, keep going: pick the next content experiment yourself.
- If unsure where to go, ask a GPT reviewer for advice. Give it the current best outputs, the user's stated preferences and what has been tried.
- Target deliverable: machine-readable JSON plus a rendered structured view. No prose.
- Focus stays on content quality (Center, History, Connection, why-now, mechanism; natural speech, no formula sentences).

- 10-21 later, user correction: I misread "structured" as "shortest possible narration". I hid why-now and history in an invisible internal layer, which left a descriptive ~900-char show layer.
  - Structured means the content lives in explicit fields: now / why_now (natural explanation, not 因为…所以 formula) / history items (which concrete earlier experience → what effect now) / revises / open. Don't over-compress.
  - Why-now must be visible.
  - Don't over-invest in model-reader tests that ceiling. Check advisor suggestions against the user's own criteria before adopting them.
- 10-21 user clarification: structured = a graph. Discrete elements (经历、认识、愿望、恐惧、办法、发现、机制、状态、问题) with typed relations between them (导致、改写、唤起、失效、冲突、用来抵挡…), like the earlier ← / → / ↺ arrows. Presentation and extraction are derived from the graph later. why-now = incoming edges into a segment's state. Implemented in `tgraph.py`.

Related: [[thread-form-not-prose]], [[experiment-autonomy]], [[notify-only-key-events]].
