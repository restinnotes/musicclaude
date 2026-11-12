---
name: overview-page-style
description: "What the user wants from run overview HTML pages — plain Chinese, prompt-version evolution, reviews summarized by Gemini, no machine parameter names"
metadata:
  node_type: memory
  type: feedback
  originSessionId: f5c661df-9026-436a-99d1-94c3c437c97f
  modified: 2026-09-25T16:00:43.071Z
---

The run overview page must be readable by a person: plain Chinese only, no file names, job ids, parameter names or internal codes. It should show only: how each branch's prompt evolved version by version (which sentence changed, why, effect), how each round was reviewed, and key findings. I design the template once; Gemini 3.8 Flash summarizes the reviews into the data; facts like sentence diffs and test coverage are computed by script, not written by the model. Reusable prompts/templates are saved to disk (prompts/tooling/, tools/site/).

Also required (2026-09-25): every judgment must be tied to a named constitution criterion with plenty of verbatim evidence (from outputs, not only reviews), details in second-layer drawers, a sticky TOC/quick-jump, saturation curves shown on the page, and quotes verified against sources. Summarizer model may be Muse if it writes richer content — compare, don't assume. Compared 2026-09-25: Muse copied review verdicts faithfully and 99.7% of its quotes verified vs Gemini 3.8 Flash 83% with inflated verdicts, so Muse is the default summarizer (`build_site.py --model muse`).

**Why:** user on 2026-09-25: the call-log style viewer was "完全看不懂…全部都是各种给机器看的参数名", asked for this redesign and for the prompts to be persisted for reuse.

**How to apply:** user (2026-09-25): "每做完一组都去调用gemini实时更新我们的html" — after EVERY finished group (a run, a review, a batch of reruns), immediately rerun `python tools/site/build_site.py` (full Gemini summary, not --reuse); check the Gemini summary against the reviews for overstated claims before showing the user. Related: [[delegation-split]].

**Superseded 2026-10-03:** the "update html after every group" instruction is replaced by [[zip-per-round-no-index]]; keep only the page-style guidance above.
