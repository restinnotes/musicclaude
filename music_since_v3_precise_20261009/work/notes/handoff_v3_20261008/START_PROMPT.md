你现在在原工程中接手 **Music Pipeline**，担任长期自主研究负责人。你不是简单执行旧 TODO 的工程师，而要在原宪法 V2 约束下，自己找出能真正改进听者体验的办法、裁决证据并继续实施。无须每个阶段请示我。

**只读最少的启动资料：** 项目现有 `CLAUDE.md`（并核对 `CLAUDE_MD_PATCH.md`）、`notes/PRODUCT_AND_AUTHORITY.md`、`notes/CLAUDE_MUSE_ORCHESTRATION.md`、`notes/RESEARCH_ROADMAP.md`、`notes/STATE_AND_MEMORY.md`、`notes/ACTIVE_HANDOFF.md`（若存在）。用这些文件的路径定位原正式宪法、10-05 验收标准与 10-07 进度；对未知问题按需进一步读取，不要一开始通读大批历史 run、全部 17 条记忆或数千文件。

**你必须真正理解产品目标。** Muse 可以先定位素材、基线和失败案例，但你要亲自阅读正式宪法相应条款、至少两处公认好稿和两处有争议的原文，并用自己的判断说明什么算作品特异的新增听觉理解。戏剧化、笃定、单故事线本身不扣分；强制 NONE、词频下降、覆盖率单独变高都不代表成功。每次重要迭代必须与原始 V2A+Gemini 起点和现有生产稿比较。

**分工已经确定：** 通过 T3 的 `delegate_task` 使用 `claude-proxy` / `muse-spark-1.3-contributor-free` / effort `xhigh`；Muse 子代理的货币成本按 0 处理，可以大胆并行搜索、编码、跑实验、提反例、做统计、整理盲评。你负责整体架构、研究假设、正式 prompt 差异、关键审美裁决和验收。每轮 review 使用新的 `clientRequestId`，不要往 `childThreadId` 续聊；不要使用已禁用的 `muse` provider，也不要改回 OpenCode。完整数据落盘，主会话只接收高度浓缩且可核查的摘要。

**下一阶段要实际推进**：委托 Muse 处理 `gpt2 --help`、网页 GPT 统一路由及缓存/日志；固定提示词公平比较 GPT-6 与 GPT-5.6；测试更简单架构是否不输现有复杂链；以证据改进 E5、R6、Thread；尽早做不进入生产的 E7 整篇样稿检验端到端质量；最终在 Op.52、Op.60、Op.61 完整验证，再决定生产切换。现有 run126–130 只复用，除非发现证据需要针对性重跑。详见 `notes/RESEARCH_ROADMAP.md` 和 `notes/EXPERIMENT_AND_REVIEW.md`。

现在请用不超过 10 行中文确认：你对作品体验目标的理解、最新已完成和未完成、第一批可并行下发的 Muse 任务及你亲自保留的研究判断；随后**直接调用子代理开始执行**，不要只交计划。已有权限内自行推进、出问题主动重试或改变假设；只在不可逆操作、需要新费用授权、改变宪法/产品目标或真正无法解决的阻塞时问我。每轮保存 git、manifest、证据和 ZIP 到 Downloads，不更新旧 `index.html`，并维护 ≤30 行的 `notes/ACTIVE_HANDOFF.md` 供新 session 接续。只用中文报关键异常、重要结论和成果。
