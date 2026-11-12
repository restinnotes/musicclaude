# 审计交付导航

先读 AUDIT_REPORT.md，再看 COUNTERFACTUAL.md 的假设与 QUALITY_RISKS.md 的质量边界。

必需交付共六项：

- AUDIT_REPORT.md：真实构成、覆盖率、分工预测与明确建议。
- TOKEN_LEDGER.csv：3903次去重Claude响应，真实usage、缓存、模型、类别、来源行号。
- TASK_ATTRIBUTION.csv：1008个触发根任务×类别证据簇，不是1008个独立生产实验。
- COUNTERFACTUAL.md：A/B/C公式、全部参数、缓存/交接/返工敏感性与入口比较。
- QUALITY_RISKS.md：两个质量事件、10个历史影子案例、已验证与待验证边界。
- AUDIT_METHOD.md：来源、去重、价格公式、覆盖缺口与复现步骤。

其他CSV/JSON提供未匹配请求、聚合残差、分类映射、案例成员、参数、敏感性、文件hash与测试回执。

复算入口：scripts/READ_ONLY_REPRODUCE.py；Python标准库，读原JSONL固定字节前缀并验证hash。没有在本包内复制原始JSONL或凭证文件。CLASSIFICATION_RULES_REFERENCE.py / CASE_SELECTION_RULES_REFERENCE.py是规则参考，依赖内部中间数据，不是独立执行入口。

已核验历史API等价代理基线$514.733106165；不是订阅收费。情景净节省不是已验证实绩；不能直接折算五小时额度。当前有279条未匹配请求头与独立Haiku聚合残差，均未伪造逐次Token。

没有修改生产系统、安装插件或重跑生产模型实验。独立项目副本位于 D:\musicclaude\_thread_evo_20261019\_claude_token_audit_20261028 。
