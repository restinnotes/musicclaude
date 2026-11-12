# r1：17 条记忆 vs 10-08 新规则核对（2026-10-08，Muse 只读）

新规则入口：CLAUDE.md 末节（10-08）、notes/STATE_AND_MEMORY.md §B、notes/CLAUDE_MUSE_ORCHESTRATION.md。
结论：(a) 7 条需最小修改；(b) 10 条保留；(c) 索引 17 行↔17 文件一一对应。未动任何记忆文件，未恢复已删误存记忆。

## (a) 冲突/过时 → 最小修改（新旧对照）

1. delegation-split.md
旧：Muse 经 `opencode run --model opencode2api/muse-spark-1.3-contributor-free#xhigh`；HTML 经 agy 到 gemini-3.8-flash。
新：Muse 改 T3 `delegate_task`（providerInstanceId=claude-proxy，model=muse-spark-1.3-contributor-free，options.effort=xhigh；每轮新 clientRequestId，不用 childThreadId 续聊）；删 agy 句，HTML 走 Muse 或既有 Gemini 路由。

2. music-run-cli-invocation.md（文件头加状态头，不改历史正文）
旧：Muse=opencode 路由现状；"Opus: no more calls after 2026-09-30 21:00"；各 GPT 键为现状。
新：加"2026-10-08：Muse 默认 T3 delegate_task，本文件 opencode/Muse 条目为历史；Opus 停用句被 10-06 自由使用取代；网页 GPT 待 gpt2 迁移，旧路由（safechain/mg/codex）只作有日期的历史证据。"

3. overview-page-style.md
旧："每做完一组都 rerun build_site.py 实时更新 html"。
新：该句作废（10-03 起不维护 index/HTML，改每轮 ZIP；见 zip-per-round-no-index）；保留纯中文、无机器参数、引文核验等风格要求。

4. gpt56-web-route.md（头加一行）
旧：safechain 为现行调用方式。
新：加"2026-09-26 safechain 时期历史证据；现行网页 GPT 入口待 gpt2 迁移（未完成）；水杯题（>3min、答8）判据仍可复用。"

5. dev-agent-sol-and-opus-subagents.md
旧："Opus 可随便用：dev/mechanical tasks go to Opus subagents"。
新：改为"默认机械开发回到 T3 delegate_task Muse；Opus 用于有价值的内容候选与高级评审，不做默认机械代理"。

6. no-self-candidate.md（例外段更新）
旧：例外=2026-09-27 经 claude -p 测 Opus/Sol 外部候选。
新：例外改为"Opus 子智能体可在关键位置当内容候选（10-06 许可）；编排者本人仍不写参评稿"。

7. opencode2api-deploy-watchdog.md（头加一行）
旧：全文以 opencode2api 为现行 Muse 通道。
新：加"仅当仍经 opencode2api 路由调用时适用；Muse 默认已切 T3 delegate_task。"

## (b) 保留（10 条，均与新规则一致或被其重申）

music-run-method、reply-in-chinese、baseline-anchor、stop-when-conclusive、style-matters-for-model-choice、drama-not-a-flaw、luna-research-delegation、zip-per-round-no-index、notify-only-key-events、gpt56w-paused-20261005。

## (c) 索引一致性

MEMORY.md 17 行↔磁盘 17 个 .md 文件名一一对应，无缺失、无多余；已删误存记忆无索引行，不恢复。
小瑕疵：索引第 1–2 行钩子句含 agy/opencode（已退役路由字样），待上面文件加状态头时顺手更新，不必单独改。
