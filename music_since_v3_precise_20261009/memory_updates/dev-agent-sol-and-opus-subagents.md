---
name: dev-agent-sol-and-opus-subagents
description: 10-06 — Sol 6.1 dev permission REVOKED (~22:30); Opus may now be used freely (dev agent via Agent tool + content candidate)
metadata:
  type: feedback
---

Two permissions granted 2026-10-06 ~20:30, valid until the user revokes them:

1. "把所有的让muse做的都升级成gpt sol 6.1 medium … 你也可以让他去对你的代码做反驳" — development / mechanical tasks previously handed to Muse (scripts, smoke, reports, code review/challenge of my code) go to GPT-6.1 Sol medium via `tools/sol_dev.py` (codex exec, workspace-write + network). Task specs live in `tools/sol_tasks/`. This is the dev-agent role only; content-model choices inside experiments are unchanged (Sol is still replaced by 5.6 for content calls, see [[gpt56w-paused-20261005]]).

2. "我们链路里的最关键的几个位置 你可以派你的claude opus subagent去做 去测试他的能力" — Claude Opus subagents (Agent tool, model opus) may produce content as candidates at the most critical pipeline positions (bead synthesis, History/Thread, second-order, WHY, attention), to measure their capability against GPT-5.6. This temporarily overrides [[no-self-candidate]] for subagents only; the orchestrator itself still doesn't write content. Pass the full prompt text inline (CLAUDE.md rule), have the subagent write only its answer to a given file, then judge blind with other models.

**Why:** user wants faster/better dev work and a test of Opus at key layers.

**How to apply:** use sol_dev.py instead of muse.py for dev tasks; when the user revokes, switch back. Related: [[delegation-split]].

**Update 10-06 ~22:30:** "我撤销让你可以随便用sol6.1的许可 但是你现在可以随便用opus". Sol dev-agent permission revoked — do not use tools/sol_dev.py. Opus may be used freely: dev/mechanical tasks go to Opus subagents (Agent tool, model opus) or the runner `opus` key; Opus is also allowed as a content candidate anywhere. Until revoked.

**Update 10-08:** default dev/mechanical agent is Muse via T3 `delegate_task` (see [[delegation-split]]); Opus remains allowed for content candidates and senior review, not as the default mechanical dev agent.

**Update 10-09 (user, fork thread 9806c489):** "既然claude不可用就你自己来就行 不要调用opus了" — Opus permission REVOKED: no Opus subagents (Agent tool), no runner `opus` content/judge calls. Dev work: do it yourself in the main session or via Muse. (Existing Opus outputs stay readable.) On 10-09 I wrongly launched an Opus dev subagent after a context handoff and had to kill it — check this memory before any Agent/opus call.
