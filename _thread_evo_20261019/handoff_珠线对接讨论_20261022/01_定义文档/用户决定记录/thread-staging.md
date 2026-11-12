---
name: thread-staging
description: 10-20 user — write the full Thread first with no length cap; compression and bead selection are later, separate steps (like bead STRUCT → reader)
metadata:
  type: feedback
---

User (2026-10-20): don't compress the Thread at the generation step; finish the full Thread first, then compress/select later, the same way beads go full → reader. Beads may also be brought in at a later step, after which compression and selection happen.

**Why:** compressing while still working out the understanding risks losing it; the video reading budget (~4–6 字/秒; the 14 bead readers alone already fill it) belongs to a later presentation step.
**How to apply:** at the Thread stage, judge only the full Thread's quality (no length criterion, though padding and repetition still count against it). Treat bead integration and compression/selection as their own stages with their own criteria. Related: [[thread-taste-calibration]], [[final-product-is-video]].
