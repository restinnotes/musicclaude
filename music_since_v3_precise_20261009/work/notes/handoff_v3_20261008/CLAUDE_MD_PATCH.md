## Music Pipeline 长期执行原则（合并到原 CLAUDE.md，不覆盖原有规则）

- 使命：为认真听音乐的人生成**随音乐时间展开、作品特异、具体可感、有来路与可听依据**的“边听边读”理解，不能只优化中间层数字；产品正式宪法 V2 优先。
- Claude 主会话长期负责：理解产品、研究假设、正式 prompt 修改与归因、盲审决策、架构取舍、production 验收；不能一次失败后只写“下一步建议”。主会话**不亲自当内容候选写手**。
- **Muse 免费且已指定路由**：T3 `delegate_task`，target 使用 `providerInstanceId=claude-proxy`、`model=muse-spark-1.3-contributor-free`、`options.effort=xhigh`。不要用禁用的 `muse` provider；每轮独立 review 使用新 `clientRequestId`，不得通过 `childThreadId` 续聊；详见 `notes/CLAUDE_MUSE_ORCHESTRATION.md`。
- 自由给 Muse 并行分配工程、搜索、试验、失败案例、对抗性质疑、盲评包整理；它不代替 Claude 对音乐审美做最终裁决。任务完整结果落盘，只以短可核查报告回主会话。
- 对模型先固定 prompt/输入/预算，再比较 GPT-6 vs GPT-5.6；对提示词只改一个实验变量并记录 DERIVATION，不能“换模型+改 prompt+换架构”混作同一个胜利。
- 保留 **V2A+Gemini 原始基线**和已认可旧稿；不能以长度/覆盖率/抽象词频/NONE 数字单独判胜。戏剧化、笃定、单故事线**不自动扣分**；没有证据的心理意义才是问题。
- A/T 第一轮研究相互独立；H 是补充材料；T/H 不得擅自重写当前 Affect；前缀有效、音乐时间定位、逐句溯源和实时显示生命周期必须保持。
- 新的 E7 可以早做**诊断性样稿**进行最终阅读盲比，但旧的 E1–E7 验收仍适用，未经三首作品复验不得切换 production。
- 汇报用户只用中文且只报重要结论/故障/完成；每轮新 ZIP 到 Downloads，不维护旧 index；维护简短 `notes/ACTIVE_HANDOFF.md`。误存的 Muse 记忆已由用户删除，不要复活或擅自大改其他记忆。
