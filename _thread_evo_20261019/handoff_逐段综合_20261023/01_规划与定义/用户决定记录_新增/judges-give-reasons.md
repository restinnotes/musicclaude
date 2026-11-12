---
name: judges-give-reasons
description: "10-23 user — every judge verdict (each label, score, yes/partial/no) must come with a short reason so it can be calibrated"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 7c623294-a1ea-40eb-b513-ae6588ad2c39
  modified: 2026-10-23T01:41:59.175Z
---

User (2026-10-23): "你让评委做的时候也要让他说理由 这样你也方便校准".

**Why:** bare labels and scores can't be checked. On 10-23 the whole-draft judge rated N8 as explaining 87% of main beads, while the sectional judge said 36–42%. Without reasons there was no way to tell which judge was misreading.

**How to apply:**
- In every judge schema, pair each per-item verdict with a one-sentence reason, e.g. `{"verdict": "部分", "why": "…"}`.
- Pair each score with the passage it rests on.
- Before trusting a judge, read a sample of its reasons against the text.

Related: [[thread-taste-calibration]], [[self-judging-ok]].
