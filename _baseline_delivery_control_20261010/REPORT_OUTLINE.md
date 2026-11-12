# 最终交付报告结构（冻结基线：仅两个 web GPT）

> 本文件是报告结构冻结稿，不是研究报告正文。不创作音乐研究结论，不宣布饱和。
> 所有数字必须来自 `validate_delivery.py` 的 `delivery_validation.json`，不得手写估计。
> 术语：transport_valid（传输完整）/ schema_parse_ok（JSON 可解析）/ source_valid（与冻结 source 结构一致）。
> 三层分离：meta.status 成功 ≠ payload 无问题；transport_valid_success 才计有效成功。

## 0. 范围与冻结声明（必写）

- 冻结包日期、manifest / repetition_plan / review_manifest 版本、prompt SHA 配对一致结论。
- 仅两个 web GPT（gpt-6-thinking / gpt-5-6-thinking）；未用 Opus / Sonnet / Sol / Luna。
- 同一 job 两模型 prompt 逐字节相同；每次独立新会话，不 resume。
- 主控后续决定是否扩 r12 并完整交付；本报告只覆盖已验证证据。

## 1. 成功计数（transport_valid 为准）

- BASE r01–r05（16 job × 2 模型 × 5 = 160 格）：
  transport_valid_success / success_claimed_transport_invalid /
  confirmed_pre_submit_failure / ambiguous_failure / missing / other，分模型、分 track（A/B/C）列表。
- r06–r08 / r09–r12：逐 job×模型实际存在轮次；r06+ 配对缺口清单（一方 valid、另一方缺失/失败）。
- 评审（review_manifest 按实际长度动态读；初版 88 项：D 40 / G 40 / F 8，若调度器追加 r08/r12 评审则如实扩展）：transport_valid_success 与 by_class 明细；
  F 缺项必须点名（如 F_k18_n05_judgegpt6w 等）并给终态，不隐藏。
- success_claimed_transport_invalid 单列成因（SHA 链断裂 / txt 缺失 / 路由-effort 不符 / session 缺失），
  不并入成功数。

## 2. 所有失败与已排空状态（必全列）

- 逐条：area:job:model:round、meta.status / phase / exit_code / elapsed / utc_start。
- attemptNN 归档链：确认 pre-submit 才归档重试的证据链完整（attempt 文件与终态对应）。
- ambiguous（failure_or_ambiguous）：只给 ownedjob 只读核查建议，不重提交、不覆盖、不伪造 exit0。
- 恢复补充（如有）：单列 RECOVERED_FROM_OWNED_EVIDENCE，
  逐条写证据路径 / sha / session / 绑定可证明范围，原 CLI exit1 保留。

## 3. r05 / r08 / r12 各站 semantic_units + 价值（C 五站 k02/k11/k18/k20/k23）

- 每个站 × 模型 × 轮次：F 评审给出的独立语义 unit ID、首次出现轮次、每轮新增数、无依据淘汰数、冲突示例占位。
- 只记录“评审说了什么”，不把 JSON 可解析 / 来源 ID 稳定当作语义饱和。
- r12 仍增长则标 UNSATURATED 并交主控，不设无限循环、不宣布饱和。

## 4. D / G 顺序与自评局限（必写）

- D：旧 run124 vs 新稿，仅另一模型评；A/B 顺序互换；两模型 D 胜率不直接跨标尺比。
- G：同站同重复 6w vs 5.6w，两模型各评、顺序互换；会出现匿名自评，按评审模型分别展示 + 敏感性分析，
  自评不作独立证据；无法判定标争议。
- F：另一模型做语义去重与边际增益审查；prompt 过长分批但不省略任一重复。

## 5. 单位辨析（防误读，必写）

- A 是 36 个案例（6 批 × 6），重复 5 次是题内稳定性证据，不是 180 道独立试题。
- B 是审阅固定候选（Thread-WHY），不是生成全新 Thread；B 的“稳”只是审查结论趋稳。
- 五个 C 站点是五个音乐位置，不泛化为全曲结论。
- A36 案例、B 假说、C 站点的跨题汇总以案例/站点配对为单位，不把同题重复当独立样本。

## 4b. A36 说明（与第 5 节呼应，不计入试题数）

- A01–A06 每批 6 案例，共 36  blind ID；报告稳定性时以案例为单位给 verdict 分布，
  不把 r01–r05 的同案例重复计成新题。

## 6. CLI imported pilot 时间窗（必写）

- A01 / B02 的 r01 来自旧 pilot（imported_from_pilot + context_warning），时间窗早于本轮；
  C02 失败未导入。
- 敏感性分析同时给出“含 pilot r01”与“排除 pilot r01”两版计数。

## 7. 实际并发峰值（实测，非假定）

- 以各终态 meta 的 utc_start + elapsed_seconds 区间扫出重叠峰值与时刻；
  写明观测口径（含/排 pilot），不写“假定并发 N”。
- gpt2 初始化同时只开一个的串行约束如实记录；耗时异常（极短耗时）另报，不记为认知质量差。

## 8. 证据清单与复现命令（必写）

- 数据根、验证报告（delivery_validation.json / summary）、SHA 清单、ZIP + .sha256。
- 可调用命令（均 -I、均带 --data-root，不从下载解压目录运行）：
  `python -I validate_delivery.py --data-root <数据根> --report-dir <可信目录>`
  `python -I package_delivery.py --data-root <数据根> --report-dir <可信目录> --output <Downloads新唯一ZIP>`
- 工具路径：`_baseline_delivery_control_20261010/validate_delivery.py`、
  `_baseline_delivery_control_20261010/package_delivery.py`、
  `_baseline_delivery_control_20261010/REPORT_OUTLINE.md`。

## 9. 局限与未决事项（必写，不许用工程层掩盖）

- 所有无法作答的质量问题逐条列出；谱/录音未经本轮独立核查；历史 E5 旧裁决只作校准参考。
- 未饱和项标 UNSATURATED；不声称五站证明全曲泛化；不把失败记为沉默或低质量。
