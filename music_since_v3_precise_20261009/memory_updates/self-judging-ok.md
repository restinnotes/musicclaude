---
name: self-judging-ok
description: "10-09 user — generators may judge their own outputs; use every available model (gpt56w, gpt6w, opus, luna, gemini, Muse) as reviewers"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 496c3129-0e46-4f8b-ae50-c1fd2d5e7540
  modified: 2026-10-09T04:08:23.821Z
---

User (2026-10-09): "生成者评自己也没关系", after asking why gemini-pro judged instead of gpt56w/gpt6w and Muse. Don't exclude a model from reviewing because it generated a candidate; put all available strong models on the panel (gpt56w, gpt6w, opus, luna_noweb, gpro, and Muse via T3 delegate_task) and report each judge's votes separately, flagging self-judgments so self-preference stays visible.

**Why:** the user wants the strongest/most diverse panel; excluding the GPT models (when gpt2 was down) looked like arbitrary model choice to them.

**How to apply:** this overrides the "never let a generator judge itself" line in notes/EXPERIMENT_AND_REVIEW.md. When a route is down, say so explicitly instead of quietly substituting another judge. Related: [[drama-not-a-flaw]], [[muse-delegate-early-stop]].
