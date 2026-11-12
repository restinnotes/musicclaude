# Music Pipeline｜Claude 自主研究接手包 v3（2026-10-08）

这是一份 **增量控制包**，不是工程源码，也不是把 10 月 5 日方案推倒重来。目的：新的 T3Code Claude 主会话真正理解用户想要的音乐聆听体验，独立负责研究、裁决、持续迭代；在 `delegate_task` 中尽量把可并行工作交给免费 Muse。

## 安装（Windows 原工程内）

1. 在原项目根目录解压本包：将 `notes/` 文件夹中的新文件放入项目 `notes/`；`reference/` 是只读备份资料，可以整夹留在项目根目录。**不要覆盖任何旧的 source、run、prompt、记忆或 CLAUDE.md。**
2. 将 `CLAUDE_MD_PATCH.md` 中的规则**人工合并**到原有项目级 `CLAUDE.md`（避免重复、冲突），不要用新文件直接覆盖原有 `CLAUDE.md`。如不方便，直接把 `CLAUDE_MD_PATCH.md` 留在根目录，启动指令会要求 Claude 读取。
3. 在 T3Code 的**原工程工作目录**开启新的 Claude 主会话，复制发送 `START_PROMPT.md` 的全文。以后重开 session 优先读项目状态，不需要重读全部旧日志。
4. 确保本地原工程仍有完整宪法 V2、V2A+Gemini 起始参考、run126–130 和历史提示词。`reference/` 只是帮助对照的极少量快照，不提供原工程。

## 文件清单

- `START_PROMPT.md`：**唯一需要贴入新主会话的启动词**。
- `CLAUDE_MD_PATCH.md`：主会话每次都应牢记的短规则。
- `notes/PRODUCT_AND_AUTHORITY.md`：项目定义、质量标准与旧源文件权威顺序。
- `notes/CLAUDE_MUSE_ORCHESTRATION.md`：**已确定的 T3Code `delegate_task` 调 Muse 用法**，避免误用 Muse Code provider、childThreadId。
- `notes/RESEARCH_ROADMAP.md`：真正需要完成的研究路线、阶段衔接与通过条件。
- `notes/EXPERIMENT_AND_REVIEW.md`：模型比试、盲评、因果归因、异常降级与精简回传合同。
- `notes/WORK_PACKET_TEMPLATE.md`：交给 Muse 的可复用任务合同与回传格式。
- `notes/STATE_AND_MEMORY.md`：跨会话无损接续、17 条历史记忆的最小维护方式。
- `notes/ACTIVE_HANDOFF_TEMPLATE.md`：每次接手的简短状态快照模板。
- `reference/`：原任务、最新进度、验收条件和提示词开发规则的**只读副本**；仅供定位，遇本机更新以已验证的原项目版本为准。

## 重要变更（相对前一版接手包）

1. **Muse 按零货币成本处理，不设子代理数量/调用次数的任意上限。** 主会话 token、上下文污染和关键决策质量是优化重点。
2. **内部 Muse 路由已由用户确认**：`delegate_task` → `providerInstanceId=claude-proxy`、`model=muse-spark-1.3-contributor-free`、`options.effort=xhigh`。不要重新研究/迁回 OpenCode；发生实测失败才诊断。
3. 每轮独立 review 都**新建** `delegate_task` 和 `clientRequestId`，不向旧 `childThreadId` 续聊。
4. 项目不只优化中间模块：在不更改 production 的前提下**尽早生成新版 E7 诊断性完整样稿**，与原始 V2A+Gemini 基线及旧生产稿盲比。
5. 允许 GPT-6 与 GPT-5.6 固定提示词对照，以及 **GPT-6 驱动的简化架构对照**；模型比较和架构比较必须分开归因。
6. 用户说误存的 T3 Claude Custom 记忆及索引已删除。**不要恢复那份错误记忆**，也不要自动大规模重写 17 条记忆。

## 优先级冲突时

原始用户目标/当前明确指示 > 项目正式宪法 V2 与材料权限 > 原任务验收条件 > 最新本机可复现证据 > 本包研究流程 > 更早临时指示/历史运维记忆。对未知事实做查证，不把 `CONSTITUTION_CHECK_v2.md`（核对记录）错当原始宪法本体。
