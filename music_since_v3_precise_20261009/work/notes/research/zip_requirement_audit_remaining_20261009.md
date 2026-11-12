# ZIP 要求审计第三轮台账（2026-10-09，剩余项补核，不改前两轮文件）

- 审计员：research 子代理（只读；未做模型调用、未写候选内容、未启动后台、未派子任务）
- 本轮限定（brief 原文）：只核前两轮明确未读的要求类文件，不重复已有完整核证、不读全量 raw、不运行包中脚本
- 输出：本文件＋同目录 `zip_requirement_audit_remaining_20261009.json`（机器可读）
- 判定标准：按正式宪法 V2 / 06 验收逐条判断旧架构要求是真失效还是应保留成产物任务；**不凭"旧"废弃**；MP4 等当前不做须给具体依据
- 前两轮纠正保持：SUP-04 撤销（主会话写手禁令有效）、"不派子任务"仅审计 scope、run135 只有 gpt56 短项 healthy

## §0 本轮读取清单（机器事实）

### (A) 三包任务全文：30/30 从 ZIP 原文读完（此前 r1 JSON 零点名，见 §3）

- parallel 包（17 文件）：`00_MASTER_AGENT_PROMPT.md`、`01_SHARED_FROZEN_CONTEXT.md`、`MANIFEST.json`、`README.md`、schemas 5 份、tasks 8 份（01–07＋99）——**全部已读**
- review-build 包（14 文件）：`00_MASTER_AGENT_PROMPT.md`、`01_FROZEN_STATE.md`、`MANIFEST.json`、`README.md`、schema 1 份、tasks 9 份（01–09）——**全部已读**
- vnext 包（21 文件）：`00_MASTER_AGENT_PROMPT.md`、`01_ARCHITECTURE_VNEXT.md`、`02_HISTORICAL_BEHAVIOR_FREEZE.md`、`03_AGENT_CONCURRENCY_AND_STABILITY.md`、`04_PIPELINE_IMPLEMENTATION_TARGET.md`、`MANIFEST.json`、`README.md`、schemas/README、tasks 13 份（01–13）——**全部已读**

### (B) chat_findings：ZIP 内 8 md vs 本机同名 8 文件，逐字节全等（BYTE_MATCH 8/8）

| 文件 | sha256 |
|---|---|
| 00_README.md | 6c85c10a5c567fd325a7792f7ef9b1efb56c28a4a2f3d8cdb32f2b1516dde0b8 |
| 01_NEW_FINDINGS.md | 36f78ac7295ecced9d7aafb6b732dc8e6d227330ab0b73d9d9972f13e2e129e3 |
| 02_CORRECTIONS_TO_PRIOR_ASSUMPTIONS.md | 366f765022d5740d53e36d773b9820e035a46196de0c4444a6f08890d32c6276 |
| 03_PROPOSED_ARCHITECTURE.md | e58f6cf4b0495306b8dd612527d433dfeec405c576c8cf184216a3dc8feec69c |
| 04_MATERIAL_BRANCHES_AND_PERMISSIONS.md | 032b7f8eb97a99779eab5c81bedffce6ab517b8594016dcdc1ea9593744394c6 |
| 05_EXPERIMENT_PLAN.md | 9a2d57af03ff19e08d4ee389e26e67f9434ba2fb8c6bb468fac4c58e1a6f0f72 |
| 06_ACCEPTANCE_CRITERIA.md | 69b29abccdbda25e13358f403957b61d682e42485d6c2487b258afd65a6abfa9 |
| 07_CLAUDE_NEXT_TASK.md | 8b1920ff073a413d63ac92caa722cbf64379bb46503ee580c16b81af39837969 |

### (C) 附件包 vs Downloads v3 包：15/15 全 hash MATCH（basename 一致＋逐文件 sha256 全等）

两包各文件 sha256（两边完全相同）：CLAUDE_MD_PATCH `bd14b8b0…01ed98b`、README_FIRST `9b2b3754…6ba6d99af1e`、SHA256SUMS `2dbe6f7b…f675d13794db`、START_PROMPT `eaf292db…59dc04126ffc46`、ACTIVE_HANDOFF_TEMPLATE `f342d25e…4dee6e4aec541`、CLAUDE_MUSE_ORCHESTRATION `cf14efb2…c212776d`、EXPERIMENT_AND_REVIEW `4f1a69d0…ec648e1b16`、PRODUCT_AND_AUTHORITY `2380aa2a…c21c0c6ad5dc62d0fe3d58ebd`、RESEARCH_ROADMAP `24ad7783…174bb4731`、STATE_AND_MEMORY `a9c4d102…28fdb1f60c72890cc`、WORK_PACKET_TEMPLATE `9a272204…cc0ce0ebdb222`、ACCEPTANCE_20261005 `69b29abc…afd65a6abfa9`（与 chat_findings 06 同 hash，同一文件）、HANDOFF_PROGRESS_20261007 `7fc201bb…3e2be5815d6a24`、NEXT_TASK_20261008_PREVIOUS `94500450…17a629bdd8f65`、PROMPT_DEVELOPMENT_RULES `59405d6f…62f9e85c00b2`。

## §1 新增有效要求（24 条，REQ-RM 系列；"保留成产物任务"=新链 E7/工程侧待用，"已证明（遵守中）"=纪律性原则非音乐完成）

### RMA. Parallel 包（8 条）

- **REQ-RM-01｜Texture/Form 独立平行地图，只读、不直接触发字幕**。源：parallel `tasks/01_OP60_TEXTURE_FORM_MAP.md`（"完全暂时忽略当前 whole-work 心理中心"／"不直接决定字幕"）＋`01_SHARED_FROZEN_CONTEXT.md §8`（"与 Affect 平行…不受心理中心指导…最终用于 boundary cross-check 与 timing infrastructure"）。判定：与四层 D3/D4（REQ-TL-04 Step A 只找可听候选事件）同向，**保留成产物任务**。状态：未做。注：Op.61 包（task 02）所列 mm.1–21…mm.269–288 九段为"重点区域，不是预设边界"（文件自带声明，与 REQ-TL-03 不伪精确一致），作为该作品输入数据保留。
- **REQ-RM-02｜Center Thread 投影方法：label 更短更抽象，禁污染 local**。源：parallel `tasks/03_OP60_CENTER_THREAD.md`（"label 要比 Main realtime 更抽象、更短"／"不让所有 local content 变成 center 的例子"）。判定：投影纪律与 REQ-TC-07（吞局部独立性）一致，**保留成产物任务**；旧节点结构（3 stages 9 nodes）是旧 Center 产物，不当新 truth。状态：未做。
- **REQ-RM-03｜Op.52 UI 行为考古清单：编号/颜色/生命周期/window overlap＋五项禁恢复**。源：parallel `tasks/05_OP52_UI_BEHAVIOR_RECOVERY.md`（"是否允许语义窗口 overlap"／"planner 错误串行截断"／禁"atom = viewer update…truncation…mandatory causality"）。判定：E7 呈现层前身，与 REQ-E7-02/03 同向，**保留成产物任务**；所点名旧仓库路径（experiments/…）仅作考古线索。状态：未做。
- **REQ-RM-04｜Title 退回短词元素，不跑大规模 chain，不生成最终标题**。源：parallel `tasks/06_TITLE_ELEMENT_EXTRACTOR.md`（"1–4 个汉字…不写完整判断句"／"不生成 100+ title candidates"／CENTER/PLOT 两类＋HIGH_POTENTIAL/TOO_LITERAL/TOO_ABSTRACT/TOO_EXPLANATORY 评级）。判定：标题工作新链未进入，方法**保留成产物任务**。状态：未做。
- **REQ-RM-05｜WHY_NOW surface contract 方法：salience 门＋Local/Long-range 可不同呈现**。源：parallel `tasks/07_WHYNOW_SURFACE_CONTRACT.md`（"不知道前文就会误听当前"等 salience criteria／"Local vs Long-range 是否同样呈现…可以不同"／"WHY_NOW 不能和 Center Thread 合并"）。判定：正是 REQ-WHY-02 缺的呈现答案，**保留成产物任务**；具体形式（〔历史反光〕去留）以 E7 定稿为准，见 §4 冲突 1。状态：未做。
- **REQ-RM-06｜Texture↔Affect cross-check 五分类，subdivision 非问题**。源：parallel `tasks/99_INTEGRATION_REVIEW.md §A`（ALIGNED／TEXTURE_SUBDIVISION_WITHIN_SAME_AFFECT／AFFECT_SHIFT_WITHOUT_TEXTURE_BOUNDARY／STRONG_CONFLICT／UNCLEAR；"TEXTURE_SUBDIVISION…不是问题本身…只有 STRONG_CONFLICT 才需要未来人工回看"）。判定：D3/D4 boundary cross-check 前身，**保留成产物任务**。状态：未做。
- **REQ-RM-07｜跨包用户决策：4+4 surface gaps deferred＋Op.61 19 口径**。源：parallel `01_SHARED_FROZEN_CONTEXT.md §3`（"Op.60: 40/44 = 90.9%…Op.61: 52/56 = 92.9%…用户明确要求本轮先不补"）＋`§4`（"21 realtime decisions…19 actual display events"）＋review `tasks/06`（"必须最终只有 19 actual display events"）＋vnext `tasks/11`（"Op61 19 display-event baseline 不被意外改写"）。判定：三包一致的用户决策/基线口径，非旧架构专属，**保留**（gaps 进 E7 处理；19 口径为回归锚）。状态：已证明（遵守中：生产仍 run124，未补 gaps）。
- **REQ-RM-08｜Center 是 organizer、禁时间机械换色＋hue/lifecycle 分工**。源：parallel `01_SHARED_FROZEN_CONTEXT.md §5`（"Center 是 organizer，不得覆盖 local heterogeneous content"）＋review `tasks/03_RIGHT_RAIL_AND_LIFECYCLE.md`（"hue 表示 thematic 身份…lifecycle 用亮度…禁止 Stage 1 蓝/Stage 2 紫 mechanical 换色"）。判定：前者与 REQ-TC-07 一致保留为原则；后者为 E7 右栏规范前身，**保留成产物任务**。状态：未做。

### RMB. Review-build 包（6 条＋1 SUP 追加见 §2）

- **REQ-RM-09｜Composition grammar：角色保留原名＋六原则**。源：review `tasks/02_PRODUCT_COMPOSITION_SPEC.md`（CORE/FACET/ALTERNATIVE/WHY_NOW/CENTER_THREAD/RECALL/JUST_PAST"不要笼统压成 Main/Secondary"；"不追求最少字数…高异质性内容必须有独立可见位置…不因为新元素出现而机械截断旧文本"）。判定：E7 composition 前身，与 06 呈现节同向，**保留成产物任务**。状态：未做。
- **REQ-RM-10｜WHY_NOW viewer 规则：salience gate 六项＋timing 建议为 prototype 参数**。源：review `tasks/04_WHYNOW_VIEWER_PROJECTION.md`（"current meaning genuinely depends on prior context…without history the current moment would be materially misheard"；"CORE 稳定后 1–3 秒出现…不要把 timing 数字写成语义硬规则"）。判定：**保留成产物任务**；timing 数字文件自声明非硬规则。状态：未做。
- **REQ-RM-11｜Timing 校准五分类**。源：review `tasks/05_TIMELINE_TEXTURE_CALIBRATION.md`（EXACT_ALIGNMENT／MICRO_LEAD／MICRO_LAG／INTERNAL_TEXTURE_SUBDIVISION_NO_SCENE_CHANGE／UNCLEAR）。判定：D3/D4 timing 基础设施前身，方法**保留**；但"禁止改变 semantic scene count"是旧冻结禁令，新链 timeline 未冻，该禁令不延续。状态：未做。
- **REQ-RM-12｜Renderer 功能清单＋QA blocker 清单＋只修渲染层**。源：review `tasks/07_RENDERER_IMPLEMENTATION.md`（lifecycle 六态／recall glow／HOLD 吸收／style config 外置"不要硬编码在 semantic data 中"）＋`tasks/09_REVIEW_BUILD_QA.md`（播放/timeline/visual/lifecycle/content 五组 blocker；"只允许修 renderer/timing/layout…禁止修 upstream semantics"）。判定：E7 渲染验收前身，**保留成产物任务**；QA content 禁项中"不出现〔历史反光〕"随 E7 定稿而定（§4 冲突 1）。状态：未做。
- **REQ-RM-13｜两支 MP4 当前不做（远期保留），三依据**。源：review `00_MASTER_AGENT_PROMPT.md`（"构建并渲染 Op.60 与 Op.61 两支完整可观看的 Review Build V1 视频"）＋`tasks/08_RENDER_REVIEW_VIDEOS.md`。判定：**当前不做，远期产物任务保留**，依据：① REQ-E7-01（语义链通过后才切 production，E7 run134 未跑）；② SUP-05（旧产品层目标冻结）；③用户"不切 production"。注：task 08"可复用旧音频源、字幕必须重新生成"与"不要使用 stale old ASS"两条纪律在将来渲染时仍适用。状态：阻塞（待 E7）。
- **REQ-RM-14｜PROVISIONAL 标记纪律**。源：review `01_FROZEN_STATE.md`（Center 顶部 surface"必须标 PROVISIONAL_CENTER_SURFACE"；临时标题"肖邦《船歌》Op.60 — Review Build V1"）。判定：与 REQ-E7-01（诊断样稿隔离标注）同一纪律，**保留为原则**。状态：已证明（遵守中：run134_e7_diag 即标诊断隔离）。

### RMC. Vnext 包（10 条）

- **REQ-RM-15｜Articulation 独立 research＋position/label 分离＋冲突不伪造共识**。源：vnext `tasks/02_ARTICULATION_RESEARCH.md`（"若声称谱面某小节有明确 marking，必须核对实际 score/source"）＋`tasks/04_ARTICULATION_JUDGE.md`（"必须分离 BOUNDARY POSITION 与 FORMAL LABEL…冲突则保留，不伪造 consensus"）。判定：D3/D4 证据诚实性要求，**保留成产物任务**；"gpt2agent→ChatGPT Web 链路"路由表述旧，被 gpt2 迁移取代。状态：未做。
- **REQ-RM-16｜Affect Boundary Review 五 verdict＋禁输 Center**。源：vnext `tasks/05_AFFECT_BOUNDARY_REVIEW.md`（TRUE_CONTINUITY／CONTINUITY_WITH_TRANSFORMATION／DISTINCT_CURRENT_AFFECT／FIELD_BOUNDARY_NEEDS_REVISION／UNCLEAR；"禁止输入 Center"；"目标是 review/纠偏，不是推翻"）。判定：D3/D4 Step B/C 前身，与 REQ-ARCH-07 一致，**保留成产物任务**（对象换为新链纯净珠子/Reviewed Affect）。状态：未做。
- **REQ-RM-17｜Prefix History Bank＝evidence ledger，严格 prefix-only**。源：vnext `tasks/06_PREFIX_HISTORY_EXTRACTION.md`（"它是 evidence ledger，不是自由故事生成器…严格 prefix-only"）。判定：与 REQ-TC-03/05、prefix-clean 同向，**保留成产物任务**。状态：未做。
- **REQ-RM-18｜WHY-NOW V3：可输出 NO_MATERIAL_ADDED_MEANING，禁机械因果**。源：vnext `tasks/08_WHYNOW_V3.md`（"必须检查 Center 与 History 两个 prerequisites，但可输出 NO_MATERIAL_ADDED_MEANING"／"保留 local/recent motion 与 long-range reflection"／"避免机械'因为A所以B'"）。判定：正是 REQ-TC-05/06 缺的语义门控内容，**保留成产物任务**；"带着核心困扰"一句带旧 Whole-work 叙事残留，慎用（§4 冲突 3）。状态：未做。
- **REQ-RM-19｜LEGITIMATE_CONTINUITY＋最小重跑原则**。源：vnext `tasks/09_REALTIME_RECOMPOSER_ADAPTER.md`（"跨 strong AFFECT_RECHECK boundary 若 HOLD，必须有 LEGITIMATE_CONTINUITY"）＋`tasks/07_EXISTING_STRUCTURAL_BRANCH_ADAPTER.md`（"只有 Reviewed Affect 有实际变化时，才重跑受影响的 downstream join"）。判定：前者为新原则**保留**；后者"复用 existing Center/Situation/Sparse、禁重跑 Center Search"属旧架构专属（SUP-06），仅最小重跑纪律保留。状态：未做。
- **REQ-RM-20｜Coverage 新增 temporal/relational/boundary 三维，只报告不自动 repair**。源：vnext `tasks/10_COVERAGE_V3.md`。判定：REQ-ARCH-08 的延伸，**保留成产物任务**；"保留 Coverage V2"按 06 验收为准。状态：未做。
- **REQ-RM-21｜回归锚：通用项保留，旧架构专属项按 SUP-06**。源：vnext `tasks/11_REGRESSION_TESTS.md`。判定：prefix causality、alternatives、no atom-per-block、HOLD、8 gaps untouched、Op61 19 口径等通用项**保留**；Center baseline、Situation first JOIN、Sparse、Coverage V2 obligations 按 SUP-06 以 06 为准。状态：部分（通用项遵守中，旧专属项待 06 裁决）。
- **REQ-RM-22｜取证/稳定性纪律：run 记录字段＋并发上限＋稳定性五步**。源：vnext `tasks/12_END_TO_END_RUN.md`（"记录 runtime / agent wave stats / calls / failed lanes / retries / stability incidents / hashes"）＋`03_AGENT_CONCURRENCY_AND_STABILITY.md`（"任意时刻最多 10 个"／超 25% 异常"暂停…记录 AGENT_STABILITY_INCIDENT…降并发…查明…报告"＋AGENT_STABILITY_REPORT）。判定：与 REQ-ROUTE-03/09 同向，通用工程纪律**保留**；Center×8 数字（6–8 可 consolidation）为旧行为，新链 fan-out 由主会话定。状态：部分（run 记录纪律遵守中，并发/稳定性待新链验证）。
- **REQ-RM-23｜"Center 不参与 Affect"跨架构保留**。源：vnext `01_ARCHITECTURE_VNEXT.md`（"Center 不参与 Affect Distillation / Affect Boundary Review…Situation JOIN 是 Center 与 Affect 第一次正式结合"）＋`02_HISTORICAL_BEHAVIOR_FREEZE.md` 同条。判定：旧架构虽被取代（SUP-06），但该条与 REQ-ARCH-07（A/T 首轮独立）同一原则，**保留为原则**。状态：已证明（遵守中：run130 纯净珠子链）。
- **REQ-RM-24｜历史冻结清单拆分：通用原则保留，旧专属按 SUP-06**。源：vnext `02_HISTORICAL_BEHAVIOR_FREEZE.md`（20 项保留＋4 项不碰）。判定：RAW 鲜活、width-first、closed-book、prefix-causality、local/long-range 独立价值、alternative routing、coverage ledger、persistent recall、lifecycle 六态、reading debt、HOLD 无空白、scene economy、"same Affect 不能自动推出 HOLD"等**保留为原则**；Center×8、Situation 第一 JOIN、Sparse、V2.3 grouping 按 SUP-06；"不碰 gaps/title/wording/render"中 gaps/render 按 SUP-05 与 REQ-E7-01，title/wording 由 E7 定。状态：部分（原则遵守中，旧专属待裁决）。

## §2 SUP 追加（1 条）

- **SUP-08｜review task 01（OP60 Center ref 修补）真失效**。源：review `tasks/01_FIX_OP60_CENTER_REFS.md`（9-field→8-field mapping：1-1→AF-V3-01…3-3→AF-V3-08）。依据：修补对象（旧 8-field Affect＋旧 Center 3×9 节点）已被新链取代（run127 纯净珠子、run130 新 Thread），无复用价值；且旧 mapping 本身要求"核对真实 measure ranges 后再写，不可盲拷"，无人执行过。状态：失效，不再作为验收依据。

## §3 本轮关闭的前两轮未核项（3 项）

1. **r1 §4 第 3 条 / r2 §5 第 3 条关闭**：三包任务文件从"抽读"变为 30/30 全文已读（§0(A)）。核查：r1 机器文件全文无 `tasks/` 点名（脚本实测 NONE），此前确无逐份核证；本次补齐。三十份中新增 24 条 RM＋1 条 SUP-08（schemas/MANIFEST/主 prompt 的执行编排部分为旧指令纪律，见 RM-07/08/13/22 跨条覆盖，不另建号）。
2. **r1 §4 第 6 条 / r2 §4 第 3 项关闭**：chat_findings ZIP 内 8 md 与本机同名文件逐字节全等（§0(B)，BYTE_MATCH 8/8＋全 hash 落盘）。r1"经本机同名副本"读取的转引风险消除。
3. **r1 §4 第 7 条 / r2 §4 附件项关闭**：附件包 vs Downloads v3 包 15/15 全 hash MATCH（§0(C) 全 hash 落盘）。r2"抽 2 文件"的抽样风险消除。

## §4 冲突/待裁决（4 项，不掩分歧）

1. **〔历史反光〕去留**：parallel task 07 把既有 `〔历史反光〕` 列为待评估选项之一（给 2–4 方案选一推荐）；review task 04 则已定"不再使用固定〔历史反光〕"。后者是更新的旧链决策，但仍是旧链决策——**新链 E7 未定稿前两者都不冻结**，以 E7 盲比为准（RM-05/RM-10 方法保留，形式待定）。
2. **"禁止改变 semantic scene count"（review task 05/06）**：旧冻结禁令；新链 timeline 未冻——**该禁令不延续**，D3/D4 重切不受此限。
3. **"带着核心困扰"（vnext task 08）**：旧 Whole-work 中心叙事残留措辞，与"禁预设叙事"方向相抵——新链 WHY-NOW 提示词不得照搬该句（RM-18 已标慎用）。
4. **三包主 prompt 的"并行 spawn subagents"执行形式**：旧"主 Agent 派 subagents 做内容"形式已被当前分工（主会话编排＋Muse 代工＋T3 delegate_task）取代——执行形式失效，但其中"只读、不改 production、不确定标 UNCLEAR/NEEDS_HUMAN_REVIEW、STOP 不自动进入下一阶段"四条纪律保留（RM-07/22）。

## §5 仍未核（维持，读者限权解释）

1. 大 ZIP outputs/raw（按指令不批量读）；hetero/humanizer 全量 raw。
2. 1003v2 `sources/` 内快照与原始聊天全文。
3. `tools/gpt2_adapter.py`、各 run `go.py`、run133 `cache_*.json` 内容（代码属主会话）。
4. run124 附录 surface 全文；run132 baseline 产物与 run136 后续。
5. round_63/64/65/67 judge prompt 禁偏见条款逐份在场验证（仅 adjudication 类 2 份已验）。
6. r1 63 条中除本轮 §1–§4 点名外未逐条回查原文。

## §6 r2 数字勘误确认（机器事实）

- r2 文字称"22 条"，`new_requirements` 数组实测长度 **24**（脚本复核一致）。本轮台账：新增有效 **24 条**（RM-01…RM-24），SUP 追加 1 条。累计有效：63＋24＋24＝**111 条**（SUP 共 8 条不计入）。

## §7 给主会话的效用摘要（只说增量）

1. **三包 30 份任务已无未读**：r2 §5 第 3 条关闭；旧包里真正值得进 E7 的是 RM-05/09/10/12（WHY_NOW contract＋composition＋viewer 规则＋renderer/QA），E7 诊断样稿可直接引用，缩小试错面。
2. **MP4 不做有三条具体依据**（RM-13）：E7 未过、SUP-05 冻结、用户不切 production——不是"旧=废"，是条件未满足；将来渲染时 task 08 的"重生成字幕、禁 stale ASS"纪律仍适用。
3. **新冲突 4 项中第 1 项最急**：〔历史反光〕去留旧链内部分歧，E7 定稿须明确裁决，不要默认沿用 review 包的"不再使用"。
4. **两组 hash 全过**：chat_findings 转引风险与附件抽样风险消除；附件 ACCEPTANCE_20261005 与 chat_findings 06 同 hash（同一文件），台账引用时可互认。
