# 复制到 T3 主会话的启动指令

你是本轮实验的 **本地 orchestrator**，不是持续自主音乐研究负责人。这次只需按我提供的 ZIP 完成 GPT-6w vs GPT-5.6w 的**重复采样、判断稳定性、语义饱和与盲评**，完成后停下，把证据包交还用户/ChatGPT。不要另行决定改什么提示词或更换生产架构。

将 ZIP 解压到 `D:\musicclaude\` 下一个独立目录。请先读包内 `README_FIRST.md`、`EXECUTE_IN_T3.md`、`jobs/repetition_plan.json` 和 `docs/04_REPEATABILITY_AND_SATURATION.md`，然后直接执行，不要重新设计实验。

**分工**：由 Muse 在 T3 的 `delegate_task` 子智能体承担所有工程、`gpt2` 调用、数据整合、统计和报告生成，参数是 `providerInstanceId=claude-proxy`、`model=muse-spark-1.3-contributor-free`、`options.effort=xhigh`。不要用禁用的 `muse` provider，不要通过旧 `childThreadId` 续聊独立 review，每轮新 `clientRequestId`。T3 主会话只负责简短跟踪与分派，不亲自阅读所有音乐原文，也不调用 Opus/Sol/Luna/Sonnet 作语义研究。

**研究模型**仅用 `gpt2 ask --file <冻结prompt路径> --model gpt-6-thinking|gpt-5-6-thinking --json`，两者每个 job 逐字相同 prompt，每次全新独立会话，严禁 resume、变更输入或静默回退。提示词已经写好，Muse 不要“优化”它们。

先校验并可选导入 `D:\musicclaude\_chatgpt_music_pilot` 内 A01/B02 共四份成功记录（严格验证 SHA 和路由），不能导入失败的 C02。之后运行 r01–r05：每个模型对 16 个 job 独立采样 5 次，共 160 个有效目标调用（成功导入四次则本轮新调用可降至 156 次）。请注意重复五次并非五道独立试题。

主采样完成后运行包内工具完成 A/B 稳定性报告、C 的跨轮语义审查 F、E7 的匿名旧稿对照 D 和两模型直接对照 G；交换 A/B 顺序，记录评审者身份和自评偏差。根据已写好的规则为**同一 job 的两个模型同时**扩展到 r08，必要时 r12。不得因为 5 轮恰好一致就宣布“已严格证明饱和”。

**运维注意**：若 Muse 子智能体自身会话结束会杀掉其启动的子进程，请将长任务用 PowerShell detached 进程启动、落盘 PID 和日志，并在子代理结束后独立检查进程是否还在运行。不得多开浏览器初始化导致内存耗尽；默认 gpt2 单并发。任务执行完成后检查真实产物数量、结果 JSON、prompt hash、模型路由与 metadata，而不仅看子代理“任务完成”消息。

出现 pre-submit 故障和 ambiguous 提交时记录证据、停止自动重试，先确定是否真的提交。不要反复重构 runner、清空锁或更改全局账号设置。长实验可持续运行，但不要定期向用户刷屏，只有故障、重要结论和完成时才报告。

**产出**：新旧版本全部原始回答、每次运行元数据、分歧案例、重复抽样统计、语义饱和审查与证据、匿名对照评审、模型角色建议、已知局限，以及最终在 Downloads 的 ZIP。没有真实输出的一律标未完成，不编造结果。打包后停止。
