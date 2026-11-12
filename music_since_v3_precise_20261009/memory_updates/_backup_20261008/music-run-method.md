---
name: music-run-method
description: "User's method rules for the music content-layer runs — choose models only after prompts are frozen, multi-model per stage with attribution, freedom to grow beyond the minimal pipeline under the constitution"
metadata:
  node_type: memory
  type: feedback
  originSessionId: f5c661df-9026-436a-99d1-94c3c437c97f
  modified: 2026-09-25T17:12:38.031Z
---

- Pick models only AFTER a branch's prompt is frozen, by comparing every candidate on the frozen prompt. Never lock a model mid-iteration: a half-iterated prompt may simply not elicit a model's behavior. Candidates for internal-knowledge branches include gemini-3.1-pro-high, 3.8/3.7/3.6 flash, luna (no tools), Muse (no tools); web branches likewise compare several web-capable models.
- Gemini 3.x Flash variants (3.8/3.7/3.6) are low-heterogeneity: if 3.8 is shown best, don't spend effort reviewing 3.7/3.6; focus on heterogeneous candidates.
- Do NOT add the Claude models offered by antigravity/agy (claude-opus-4-6, claude-sonnet-4-6) as candidates (user, 2026-09-25).
- Muse network isolation: config deny does not block tools on this machine; post-hoc voiding (any executed tool → discard + retry) is accepted by the user as sufficient.
- Growth order (user, 2026-09-25): the FIRST step beyond the base layer is heterogeneous prompts — design prompts (from constitution clauses) that elicit behaviors/content the existing branches don't produce; only after finding that compressing those behaviors into one agent works badly do we add more agents/layers. Don't lead with architecture layers.
- A stage may use several models at once, as long as the final synthesis can attribute every sentence to the model(s) that produced it (can be an external audit step).
- The handoff's minimal pipeline is only the user's starting idea. After the base layer (prompts grown from the original V2A) is done, I may add layers and design heterogeneous prompts freely; the only binding standard is PRODUCT_CONSTITUTION_V2.

**Why:** user message 2026-09-25 correcting that I chose Gemini 3.8 Flash while prompts were still being edited.

**How to apply:** re-run model selection on frozen prompts before synthesis decisions; keep per-sentence provenance; propose new layers when they serve the constitution. Related: [[delegation-split]], [[overview-page-style]].
