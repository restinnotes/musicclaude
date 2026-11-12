# ZIP 要求审计补充台账（2026-10-09，只读补核，不改历史文件）

- 审计员：research 子代理（只读；未做模型调用、未写候选内容、未启动后台、未派子任务）
- 补核对象：上轮 `notes/research/zip_requirement_audit_20261009.md/json`（63 有效条＋7 SUP）的遗漏与错误
- 本次新读（原文已读，非转引）：
  1. `notes/handoff_20261003_v2/01_CURRENT_STATE.md`（与 ZIP hash MATCH `925baf9a645cc928`）
  2. `03_PARALLEL_EXECUTION_PLAN.md`（MATCH `f35fef23f9ac7a49`）
  3. `05_SECOND_ORDER_UNDERSTANDING.md`（MATCH `74a31c28c8c34b53`）
  4. `07_HUMANIZER_ATTENTION.md`（MATCH `f290877c9193881b`）
  5. `09_PROMPT_DEVELOPMENT_RULES.md`（MATCH `59405d6fd7db10b6`）
  6. `10_ENGINEERING_REPRODUCIBILITY.md`（MATCH）
  7. `11_AGENT_ORCHESTRATION.md`（MATCH）
  8. `14_SOURCE_INDEX.md`（MATCH）
  9. `02_MASTER_PROBLEM_REGISTER.md`（ZIP 原文已读＋MATCH）
  10. `04_AFFECT_TIMELINE_D3_D4.md`（ZIP 原文已读＋MATCH）
  11. `06_HISTORY_THREAD_CENTER_WHY.md`（ZIP 原文已读＋MATCH）
  12. `08_MODEL_AND_EVAL.md`（ZIP 原文已读＋MATCH）
  13. `00_START_HERE.md` / `12_EXECUTION_ENTRYPOINT.md` / `13_STATUS_TABLE.md`（ZIP 原文已读＋MATCH）
  14. `notes/AUDIT_4LAYER_20261005.md` 全文已读（32 行组件对照表＋专项清单＋工程事实）
  15. `runs/run126_canon_op60/reviews/round_63.md`、 `run127/reviews/round_64.md`、 `run129/reviews/round_65.md`、 `run130/reviews/round_66.md`、 `run128/reviews/round_67.md`、 `run124/reviews/round_61.md` 全文已读
  16. `runs/run121_provenance/report.md` 全文已读（§1–3＋附录抽 10 条链＋附录 B 切站表）
  17. `runs/run124_render/report.md` 头部已读（§1–3＋R2 表；附录 surface 全文未读）
  18. `runs/run135_gpt2_recheck/report.md`＋`FAILED`＋`health.json` 头部已读
  19. `notes/EXPERIMENT_AND_REVIEW.md` 全文已读（§1–6）
  20. `notes/ACTIVE_HANDOFF.md` 全文已读（23 行，10-08 晚＋10-09 用户行）
  21. run130 `adj__*.txt` 抽 2 份已读（judge 条款在场抽验）
  22. 附件 v3 包 vs Downloads v3 包：basename 一致，`START_PROMPT.md` 与 `EXPERIMENT_AND_REVIEW.md` sha256 前 16 位 MATCH
- 仍未读：大 ZIP outputs/raw（按指令不批量读）；hetero/humanizer 包全量 raw；run124 附录 surface 全文；1003v2 `sources/` 内快照与原始聊天全文；parallel/vnext/review 三包任务文件逐份（仍抽读）；`tools/gpt2_adapter.py` 与各 run `go.py` 内容（代码属主会话）。

## §1 状态纠正（上轮错误，必须更正）

- **CORR-01｜SUP-04 无效，上轮"覆盖"判定错误，撤销。** 上轮 §2 SUP-04 称 EXPERIMENT §4.6"主 Claude 不得产出参赛候选"被 10-09"自评允许但标记"覆盖——错误。10-09 用户原话（ACTIVE_HANDOFF 第 22 行）是"生成者可以评自己"，即**外部生成模型允许评审自己的输出（须标记自评）**，不等于解除"主会话不得当音乐内容候选写手"。CLAUDE.md 第 48 条"主会话不亲自当内容候选写手"与记忆 `no-self-candidate`（用户 09-25 当面叫停主会话亲自写 synthesis）仍然有效。EXPERIMENT §4.6 全文已读："不允许主 Claude 亲自产出一份参赛整篇候选，再用自身评审其胜利。可以由独立 Opus/GPT/Muse 生成候选，由 Claude 裁决"——**该条继续有效，不再列为 SUP**。连带更正：上轮 REQ-REV-01 中"覆盖 EXPERIMENT §4 第 6 条（旧禁令失效…）"一句作废；REQ-REV-01 重写见 §3。
- **CORR-02｜"不派子任务"不是用户全局禁令。** 上轮 REQ-REV-01 把"不派子任务"列为 10-09 用户授权内容——错误。"不跑模型、不写候选、不启动后台、不派子任务"是上轮审计任务对**审计子代理本身**的限制（本轮同样适用），不是用户对主会话的全局禁令（00_START_HERE/12_ENTRYPOINT 明确要求"大量派生子 agent 并行"）。REQ-REV-01 中的"不派子任务"删除。
- **CORR-03｜run135 现状数字更正。** 上轮 §3 称"10-09 称 gpt2 已恢复直调 58s 正常，待重跑验证"——现已核实 run135 报告原文：`gpt56w short ok/healthy/match（60.5s）`；`gpt6w short failed（post_submit_ambiguous，headless_native_result_rejected，无自动重试）`；两项 long 均为 `skipped_queue_stop`；`route_healthy=false`，`FAILED` 内容为 `all_four_healthy=False`。即：**只有 gpt56 短项 healthy，gpt6 短项失败、长项未提交**，不是全面恢复。上轮 REQ-ROUTE-01/FAIR 系的"阻塞"状态维持，且须注明 gpt6w 短项失败细节。
- **CORR-04｜REQ-REV-02 从"部分"收紧为"部分（条款在场已抽验两份，仍缺逐份）"。** 抽读 run130 `adj__gpt56w__b0/b1` 两份全文：均含"一条假设讲得越完整、越动人，并不代表它越有依据""写得戏剧化、具体、笃定都不影响判断"——禁偏见条款**在场**（与 EXPERIMENT §3 一致）。但 round_63/64/65/67 的覆盖/盲比 judge prompt 是否逐份含该条款仍未验（本轮只验了 adjudication 类）。REQ-GEN-03 所述"Op.52 原稿已定位"经核实存在（`notes/baselines/op52_v2a_gemini_02/05.md`），维持。
- **CORR-05｜REQ-E7-06 由"未做"改为"部分"。** AUDIT_4LAYER 原文已读：其 §2 把"强制【听】/旧【此刻】不撤/主 WHY 缺席"等落实为 `tools/run124_render.py` 条件 A/B 的具体规则引用（非空泛转引）；且 round_61 已对 A/B 两规则做三首盲比并定稿 B（位置小标题＋宏观段规则，STRONG 两条）。但"主 WHY 缺席"等 Thread/WHY 侧 bug 的修复验证仍未做。故 REQ-E7-06 应为**部分**（呈现规则侧已验证＋定稿，语义侧未验），而非"未做"。

## §2 新增有效要求（22 条，编号接续上轮）

### J. 补：时间轴与 D3/D4（源：04、02-A4/A5/A7/J1、00）

- **REQ-TL-01｜m.27 反例回归**：run70 三家细切（17–23/24–31/32–34 量级）无一家首刀在 27，旧 `27–43` 系 Muse 自由叙事遗留；D4 评测集须含此反例。源：04 §1、03 Lane A-5、02-A3。状态：**未做**（D4 评测集不存在，J1 OPEN 最高优先）。
- **REQ-TL-02｜乐句边界≠Affect 边界**：乐句中间切可合理，前提是有可听音乐事实支撑；反之传统曲式未换段不禁止 Affect 变化。源：04 §2。状态：**未做**（原则已立，无工程化）。
- **REQ-TL-03｜transition range，不伪精确**：边界允许 `transition around m.24–26`，不假装精确到单小节；不把三家 24/25/26 做并集切四刀；不把 run70 文字切点直接当音乐事实。源：04 §4/§6。状态：**未做**。
- **REQ-TL-04｜D3/D4 三步审计**：Step A 只找可听候选事件（不讲心理）→ Step B 每事件判 CONTINUE/LOCAL_CHANGE/IMPORTANT_CHANGE → Step C 有支持的语义变化才成 micro-bead 边界。源：04 §5。状态：**未做**。
- **REQ-TL-05｜macro+micro 两级＋climate 作属性**：macro episode 保留持续气候（climate 不另建层，KEEP AS PROPERTY）；micro-bead 为语义重判最小单位；不要求每 micro-bead 更新 History。源：04 §4、02-A5/A8、06 §4。状态：**未做**。

### K. 补：Thread/Center/WHY（源：06、02-C/D、08）

- **REQ-TC-01｜Thread 允许多步"还看不出"＋C3 防过早主题化**：C7 第二颗珠子即宣布全曲核心须审；细珠子上"至少两段"门槛易满足（round_66：线 2–3 段即成形）。源：06 §4、02-C3、round_66 §2。状态：**未通过**（现象已复现，门槛未修）。
- **REQ-TC-02｜Center 晚形成、多候选、不回写 Affect**：三家各 3 候选、无 no_single_center（round_66 §4）现状下，"晚形成"与"禁回写"两条均未验证。源：02-C6、06 §4。状态：**部分**（多候选✓，晚形成/禁回写未验）。
- **REQ-TC-03｜History 只存 durable change＋micro-bead 允许 NO_HISTORY_CHANGE**：round_66 空步仍 0/23，R6 不通过现状未改。源：06 §4、02-C1。状态：**未通过**（与上轮 REQ-THREAD-05 并列，05 记决策、03 记机制，两条都成立）。
- **REQ-TC-04｜C5 结尾不过度解决**："学会/彻底释怀/完成和解"须更高门槛，否则保持开放。源：02-C5、06 §5。状态：**未做**。
- **REQ-TC-05｜WHY-NOW 门控定义**："忘掉前面，当前珠子会不会被听成另一件事"→不会则 NONE；会则只说差在哪里，不重写 History、不写"因为前面…所以现在…"。源：06 §6、02-D1。状态：**未做**（旧 WHY_GATE_v4 为 ≥3/4 粗暴门槛，AUDIT_4LAYER 已判改语义门槛）。
- **REQ-TC-06｜WHY_GATE_v4/SELECT 旧输出只作对照**：新 timeline/Thread 之后重跑，不得直接复用为 production truth。源：06 §7。状态：**未做**。
- **REQ-TC-07｜Thread/WHY 评审五维**：作品特异、可追溯到 beads/History、过早主题化、吞局部独立性、过度解决。源：08 §3 末（eval 章节）。状态：**未做**。
- **REQ-TC-08｜SELECT 门槛人工校准＋Luna 不作唯一稀疏裁判**：≥3/5 只是工程值；Luna 筛选偏宽。源：02-D5、08 §2。状态：**未做**。

### L. 补：Humanizer/呈现/注意力（源：07、02-E、08）

- **REQ-HU-01｜Humanizer 只转表达、不重断语义；允许有控制丢信息**：优化"听者价值/阅读负担"，不以 coverage 为最高目标；删次要限定/合并重复/改顺序/一 Outer 代多句均可。源：07 §2/§3、02-E1/E2。状态：**未做**。
- **REQ-HU-02｜Outer 效率标准**：好 Outer 让听者更快省力同时理解多个关系；需两句解释寓意的寓言机关为失败。源：07 §4、02-E3。状态：**未做**（标准已立，无评测）。
- **REQ-HU-03｜主实时层≠完整知识库**：内部可冗余完整；实时层只显示单位注意力价值最高的少量，其余进次级/回顾/不显示；STRUCT_v2 是内部组织形式非最终 UI 文本（round_61 §决定已采纳）。源：02-E5/E6、07 §6、round_61。状态：**部分**（规则已定稿 B，E7 新链未跑）。
- **REQ-HU-04｜Humanizer 独立评价六维**：自然度、信息密度、一遍理解、流畅性（无概念压缩包感）、Outer 效率、关键 meaning 保留（1–2 个，不求 100%）。源：07 §5、02-J4。状态：**未做**。

### M. 补：模型/新颖度/证据（源：08、02-F/G/H、05）

- **REQ-MN-01｜Grok 信号 TENTATIVE＋服务不稳**：run68 唯一高于 noise floor＋WHY 短鲜活会说 NONE，但结论待定、服务稳定性差。源：08 §1、02-F2。状态：**部分**（信号记录在案，stricter residual 未测）。
- **REQ-MN-02｜旧 run37 不得当排行依据**：后续分 local/global、semantic/rendering 口径重做。源：08 §3、02-G1（VERIFIED）。状态：**已证明**（遵守中，无复用记录）。
- **REQ-MN-03｜residual novelty 从严＋语义/渲染分开＋local/global 分开**：问"剩余是否让听者注意到池里没有的东西"；G2 判定偏宽 OPEN；G4 分开 OPEN。源：02-G2/G3/G4。状态：**未做**。
- **REQ-MN-04｜Web 事实清单模式未验证＋H3 支持 D3/D4**：web 主角色为可听结构事实/史料/演奏证据（H1 STRONG DIRECTION）；"只输出音乐事实清单→内容层使用"（H2）未验证；web/score-aware 证据用于 timeline 校验为 NEW HIGH-PRIORITY HYPOTHESIS。源：02-H1/H2/H3。状态：**部分**（角色已定，清单模式与 D3/D4 支援均未验）。
- **REQ-MN-05｜二阶语言不变硬**：为"更深"造过密比喻机关/抽象关系词/漂亮收束为 OPEN 问题；relation 与 vivid anchors 分开存（B4 ACTIVE），Humanizer 可重融。源：02-B3/B4、05 §2/§7。状态：**未做**。

### N. 补：过程纪律（源：00、12、09、11）

- **REQ-PR-01｜不整包翻译候选为 production prompt**：每个候选能力先作 probe/condition 验证（09 第 13 条）；交接包≠新架构规格。源：00 执行原则、12 开头、09-13。状态：**已证明**（run126/127/133 均单变量 probe，遵守中）。
- **REQ-PR-02｜backlog 不默认解决**：没做的 OPEN/TESTING/DEFERRED 不因修别项而视为解决；P0→P1→P2→P3 门控（timeline 冻前不宣布新 Thread/WHY 为 production，Gate A）。源：00 §7、12 P0–P3、03 Gate A。状态：**已证明**（生产仍 run124，上轮 REQ-GEN-04 一致；本条把门控一般化）。

## §3 REQ-REV-01 重写（替代上轮同编号条目）

- **REQ-REV-01（v2）｜评审阵容：gpt56w＋gpt6w＋Gemini Flash＋Muse；自评允许但须标记；至少一名独立评审；Pro 可额外、不替代 Flash；禁新 Opus。** 源：10-09 用户授权（ACTIVE_HANDOFF 第 22 行"生成者可以评自己…分评审单列、标出自评"）＋现行禁新 Opus 约束。说明：①"自评"指外部生成模型评自己输出并标记，不涉及主会话写候选（CORR-01）；②run133 现状 `RUN133_REV=gpt56w,gpt6w,opus,luna_noweb,gpro` 含 Opus 且缺 Flash/Muse 具名，与本条不符，需改设计（上轮下一动作维持）；③"禁新 Opus"与 08 §1"Opus 只把已存样本当对照"一致。状态：**阻塞**（待 run133 改设计重跑）。

## §4 引用一致性抽核（hash 级）

- 1003v2 ZIP 15 个 md 全 MATCH 本机 `notes/handoff_20261003_v2/` 同名副本（含本次补读的 10 份，§0 第 1–13 项列出短 hash）。
- 附件 v3 包 vs Downloads v3 包：15 文件 basename 全同；抽 `START_PROMPT.md`、`EXPERIMENT_AND_REVIEW.md` sha256 前 16 位 MATCH。
- chat_findings：上轮"经本机同名副本"读取未做 hash 比对——本轮仍未补（`notes/chat_findings_20261005/` 与 ZIP #6/#10 内 8 文件未逐字节比对），记为仍未读项（§5 第 3 条）。
- round_63–67 与 round_61：本轮已读**本机 runs/ 原文**（非 ZIP 内转引）；大 ZIP（#7–#10）内是否含相同 reviews 未比对——旧大包 raw 按指令不批量读，不影响结论（本机 runs/ 为事实来源，00_START_HERE 亦定此优先级）。

## §5 仍未读项（诚实声明，读者可据此限权解释本台账）

1. 大 ZIP #7–#10 的 outputs/raw（按指令不批量读）；hetero 5855 与 humanizer 811 全量 raw。
2. 1003v2 `sources/` 内项目快照、原始长聊天与工作包原样副本全文。
3. parallel/vnext/review 三包任务文件逐份全文（仍为抽读）。
4. `tools/gpt2_adapter.py`、各 run `go.py`、run133 `cache_*.json` 内容（代码属主会话）。
5. run124 附录 surface 全文；run132 baseline 产物与 run136（仅 go.py）后续。
6. round_63/64/65/67 judge prompt 禁偏见条款逐份在场验证（仅验 adjudication 类 2 份）。
7. 上轮 63 条中引 EXPERIMENT/ROADMAP/06 的条目，本轮未逐条回查原文（只核 §1/§3 点名的条目）。

## §6 给主会话的效用摘要（只说增量）

1. **SUP-04 撤销**：主会话写手禁令仍有效；run133 若有"主会话候选"设计须删，但 gpt56w 自评标记路线不受影响。
2. **新增 22 条中最高优先**：REQ-TL-01（m.27 回归集）与 REQ-TC-05（WHY-NOW 门控定义）——前者是 D4 评测的现成抓手，后者直接决定 WHY 稀疏化的语义门槛写法。
3. **run135 定论**：gpt2 路由未恢复（gpt6 短 fail、长项 hold），FAIR 系与 E1 复测继续阻塞，不要按"已恢复"排计划。
4. **REQ-E7-06 升为部分**：E7 呈现规则侧已有 round_61 定稿依据，缺的是语义侧验证——E7 诊断样稿可引用 B 规则为既定输入，缩小试错面。
