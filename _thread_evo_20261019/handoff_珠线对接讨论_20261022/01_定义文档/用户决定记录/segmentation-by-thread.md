---
name: segmentation-by-thread
description: "10-15: big segments come from Thread/Center; beads are framed by those segments; music texture is only for segmentation"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 3dd33401-a148-4b6c-852d-5e78085f8b0a
  modified: 2026-10-15T00:57:37.869Z
---

**Big segments come from Thread/Center.** User on 2026-09-20: "本来大段就应该用 center 来分段的". User on 2026-09-21: segment by Center 困扰 or by 情绪场, combined with 音乐纹理. On 2026-10-15 the user chose Thread-based segmentation.

**Beads are framed by those Thread segments.** Do not keep the tiny beads (run130 has 23 for Op.60).

**Music texture and music facts serve segmentation only.** They place and verify boundaries and in-segment timing. They are not content inputs for Inner.

**Why:** Small beads broke up the source emotion. Only 38% of Op.60 A units fit inside one of the 23 beads, versus 84% inside Gemini's 6 stages.

**How to apply:**
- Thread proposes segment boundaries.
- Music texture checks that each boundary falls on an audible change.
- Affect fills the content inside each segment.
- Thread never rewrites that content (constitution B3).

Related: [[final-product-is-video]], [[baseline-anchor]].
