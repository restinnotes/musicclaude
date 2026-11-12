# 机械扩样判定结论（只读冻结判词，无模型调用）

- 工具：`inspect_adaptation.py`（参数化目录，`python -I` 运行）；队列：`extension_queue.json`。
- 规则：stage 目标 8/12；触发来源 F recommend_more/late_new、unstable、order_disagreement=true；配对双模型；invalid/ambiguous 槽位不补发、不改原文；字数/词频/sourceID 集合不是饱和证明；音乐断言/戏剧化/单故事不是缺陷。
- 145 vs 146：r01–r05 口径 valid=145、canonical meta success=146；差 1 在 `B18/gpt6w/r02`——meta success（txt 18562 字节），原校验 `analyze_repeats.normalize` 按 `POOL inputs/op60/B_k18.json` 的 hypothesis_id 全集与 verdict 白名单解析 txt 时报 `Invalid control character at line 157 col 261`，故判 invalid；冻结缺口保留，不重生、不改原文。
- 可执行集合：A 六 job 全扩（A01–A06，每 job 至少一个 unstable blind；跨模型众数翻转 B006/B007/B027/B031/B035/B040/B058 等，仅供配对扩样，不做语义裁决）；B 五 job 全扩（B02/B11/B18/B20/B23；其中 gpt6w/B18/M18_1 三判词各 1，n=3 样本最薄）；C 继续 r08 剩余槽位不重复开：C02 剩 1（gpt56w/r06 failure_or_ambiguous）、C11 剩 2（gpt56w/r08 与 gpt6w/r08 均为 failure_or_ambiguous）、C23 剩 6（两模型 r06–r08 全部 failure_or_ambiguous）；需两 webGPT 评审：F_k18（gpt56w 写、5 valid、尚无 F 行）与 F_k02（缺 gpt6w 评审）；样本不足不可补发：F_k18 gpt6w 写（仅 r01/r02/r05 有效）、F_k20 gpt6w 写（r04 invalid）。
- order 翻转仅一处：`D k23 r01 gengpt56w judgegpt6w`（AB=legacy / BA=new），属评审位置敏感，按冻结规则触发 C23 扩样理由之一，不代表生成模型变化。
