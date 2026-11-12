# ZIP 有效要求—证据—缺项台账（2026-10-09，只读审计）

- 审计员：research 子代理（只读；未做模型调用、未写候选内容、未启动后台程序、未派子任务）
- 范围：12 个音乐项目相关 ZIP（见 §0）＋本机权威笔记＋正式宪法 V2＋run110–134 关键报告/ DONE / manifest（按需抽读）
- 输出：本文件＋同目录 `zip_requirement_audit_20261009.json`（机器可读全量条目）
- 优先级（已执行）：最新用户授权（10-09）＞ 正式宪法 V2 与材料权限 ＞ 原 06 验收 ＞ 最新本机证据 ＞ 新流程 ＞ 旧临时命令
- 状态定义：已证明 / 部分 / 未通过 / 未做 / 阻塞。**只有实际打开读过的证据才标"已读"**，其余标"仅目录"/"转引"，见每条"核实度"。
- 秘密、cookies、tokens、session handles：未收录（核查中未见写入报告的此类内容）。

## §0 范围 ZIP 与读取方式

| # | ZIP | 文件数 | 读取方式 |
|---|---|---|---|
| 1 | Downloads/music_pipeline_parallel_agent_pack.zip | 17 | README/MANIFEST/主prompt/共享上下文/3个任务全文已读 |
| 2 | Downloads/music_pipeline_review_build_prompt_pack.zip | 14 | README/MANIFEST/主prompt/冻结态/5个任务全文已读 |
| 3 | Downloads/music_pipeline_vnext_parallel_prompt_pack.zip | 21 | README/MANIFEST/主prompt/架构/冻结/并发/目标/7个任务全文已读 |
| 4 | Downloads/music_pipeline_handoff_20260930.zip | 16 | 00/10/12/MANIFEST＋04/05/06/02/07/08全文已读 |
| 5 | Downloads/music_pipeline_handoff_20261003_v2.zip | 33 | 00/12/13/MANIFEST＋06/08/04/02全文已读；01/03/05/07/09/10/11/14 未读 |
| 6 | Downloads/music_pipeline_chat_findings_20261005.zip | 9 | 8 个 md 全文已读（经本机同名副本） |
| 7 | Downloads/music_pipeline_round_20261003_2356.zip | 5950 | 仅顶层结构＋需求类文件名；未批量读 outputs/raw（按指令） |
| 8 | Downloads/music_pipeline_round_20261004_1131_models.zip | 2370 | 同上 |
| 9 | Downloads/music_pipeline_round_20261005_1349_full_impl.zip | 12813 | 同上 |
| 10 | Downloads/music_pipeline_round_20261007_0608_chat_findings.zip | 7044 | 同上＋内含 chat_findings 同名 8 文件（与 #6 同名） |
| 11 | Downloads/musicclaude_claude_muse_autonomous_20261008_v3.zip | 15 | 全部需求类文件已读（README/START/PATCH/ROADMAP/EXPERIMENT/ACCEPTANCE/NEXT_TASK/PROMPT_RULES） |
| 12 | D:/musicclaude/unified_run_handoff_20260924.zip | 23 | 结构已列；宪法/ prompts 经本机工程副本读 |
| 13 | 附件 6109102d-…-zip.zip（autonomous v3 同构包） | 15 | 文件清单与 #11 一致（同名 15 文件），抽读等同 |
| 14 | heterogeneous_H1_H5_forensic.zip（5855 文件） | 5855 | 只读顶层目录核证（按指令）；novelty_v2 剩 100 premiss：已有不测理由，不机械补跑 |
| 15 | D:/musicclaude/humanizer_forensic_raw_artifacts.zip | 811 | 结构＋README 级，未读全量 raw |

本机已读：宪法 V2 全文；RESEARCH_ROADMAP / PRODUCT_AND_AUTHORITY / PROJECT_STATE / HANDOFF_PROGRESS_20261007 / EXPERIMENT_AND_REVIEW 全文；05_EXPERIMENT_PLAN、06_ACCEPTANCE_CRITERIA 全文（本机副本）；run126/127/128/130 的 report 头部＋DONE＋run130 manifest 抽样；ACTIVE_HANDOFF；PROBLEM_REGISTER 头部；run129/run131/run132/run133/run134 状态文件。

## §1 要求台账（有效 63 条；SUP 失效/被覆盖 7 条见 §2）

### A. 路由精确身份与缓存（源：10-08 增量指令 §1、EXPERIMENT §5/§6、06 复现条）

- **REQ-ROUTE-01｜gpt2 先实测后改造，不编造 CLI 参数**。源：`music_pipeline_next_task_20261008.md §1`（"在用户 Windows 环境实测 `gpt2 --help`……不得凭猜想编造 CLI 参数"）。覆盖说明：现行有效，一次性工程约束。证据：`tools/gpt2_adapter.py`（存在，已列目录；内容未读）＋ACTIVE_HANDOFF"mock 18/18 过"。核实度：目录确认＋转引。状态：**部分**（真实烟雾 run131 FAILED，前两次提交前失败；10-09 称 gpt2 已恢复直调 58s 正常，待重跑验证）。下一动作：重跑 run131 真实烟雾并落盘身份证据。
- **REQ-ROUTE-02｜gpt56w/gpt6w 经统一适配层走 gpt2，不静默回退**。源：同上（"不得静默回退到 mg、Codex API 或其他替代模型"）。证据：ACTIVE_HANDOFF"runner 默认仍走旧 mg，`MUSIC_WEB_ROUTE=gpt2` 才走 gpt2"。核实度：转引。状态：**未通过**（默认路由未迁）。下一动作：主会话工程侧统一默认路由或书面保留双轨理由。
- **REQ-ROUTE-03｜每次请求落盘完整身份元数据**（请求模型名/实际返回模型名/档位/命令版本/prompt 哈希/输入输出哈希/起止耗时/stdout/stderr/返回码/重试与路由变化）。源：同上。证据：run126–130 均有 meta/＋manifest（含 prompt 与输入 sha256，run130 manifest 已抽验）。核实度：已读。状态：**部分**（旧 mg 时代完整；gpt2 新身份字段待 run131 验证）。下一动作：run131 落盘样例验收。
- **REQ-ROUTE-04｜缓存键含模型实际 ID＋CLI/适配器版本＋档位＋提示词＋输入哈希＋生成参数；修复 runner 只认 job_id 缺陷**。源：同上＋`01_NEW_FINDINGS H2`（"Do not equate 'file exists' with 'verified/current'"）。证据：HANDOFF_PROGRESS_20261007"runner 本身的缓存仍只认 job_id（新脚本绕开了）"。核实度：转引。状态：**未通过**（通用路径未修）。下一动作：主会话工程修复＋回归测（本审计不碰代码）。
- **REQ-ROUTE-05｜历史 run 只读不覆盖、版本隔离**。源：10-08 指令 §1＋EXPERIMENT §6。证据：run126 `archive_gpt56w_1005` 保留、smoke 不改写全量根产物（run126 report 已读）。核实度：已读。状态：**已证明**。
- **REQ-ROUTE-06｜可疑输出标 suspect 隔离＋健康通道配对复测；不删隔离文件**。源：EXPERIMENT §5。证据：HANDOFF_PROGRESS"10-05 旧 run126 部分可疑结果按旧状态处理"（是否实质隔离未逐验）。核实度：转引。状态：**部分**。下一动作：抽查一例 suspect 标记与复测记录。
- **REQ-ROUTE-07｜不凭客户端名称声称真实后端型号/推理深度**。源：EXPERIMENT §2。证据：run126 report 用"模型键与名字（web, mimicgate）"写法（已读）。核实度：已读。状态：**部分**（gpt2 时代待延续）。
- **REQ-ROUTE-08｜凭证/cookies/tokens 不进报告或仓库**。源：10-08 指令 §1。证据：抽查的报告/manifest 均无此类字段。核实度：已读（抽样）。状态：**已证明**。
- **REQ-ROUTE-09｜每 run 记录 commit＋prompt/model/input/output hashes**。源：06 复现节。证据：run126–130 均有 run_manifest.json（run130 已抽验含 git_commit、模板/输入/输出哈希）。核实度：已读。状态：**已证明**（run133/134 进行中除外）。

### B. 两 w 同 prompt 同路由新鲜对照（源：10-08 指令 §2、ROADMAP 轨道 2、EXPERIMENT §1/§2；最新用户：主会话做工程不调用 Opus——本节对照不含 Opus 生成）

- **REQ-FAIR-01｜同角色同轮锁定输入/时间边界/生产 prompt/长度预算/相当 effort，独立会话，新鲜配对**。源：10-08 指令 §2.2（"最终新旧模型对比要使用同一路由下新鲜生成的配对样本"）＋EXPERIMENT §2。证据：无（gpt2 阻塞，对照未跑）。状态：**阻塞**。下一动作：run131 通过后按 BEAD→E5/Thread/Center→表达顺序开对照。
- **REQ-FAIR-02｜首轮不换模型＋改 prompt/架构混改**。源：10-08 指令 P1＋EXPERIMENT §1。证据：run133 设计 C7_STEP_v2 vs v3 单变量（ACTIVE_HANDOFF；go.py 存在，内容未读）。核实度：目录确认＋转引。状态：**部分**（run133 停在 partial）。
- **REQ-FAIR-03｜五角色对照：BEAD/E5/HistoryThread/Center/表达**。源：10-08 指令 §2.3。证据：无。状态：**未做**。下一动作：优先 E5/Thread/Center，其次 BEAD（按 §2.4 顺序）。
- **REQ-FAIR-04｜匿名盲比＋相近篇幅比质量，不以长度判推理强**。源：ROADMAP 2.1＋EXPERIMENT §2。证据：历史 round_64/65/66 盲比存在（reviews/ 目录确认；细则未读）。核实度：目录确认。状态：**部分**（旧链有；新对照无）。
- **REQ-FAIR-05｜允许混合模型职责，不预设统一胜负、不因新默认升级**。源：ROADMAP 2.1/2.2＋10-08 指令 §2.4。证据：HANDOFF_PROGRESS"分窗 ×2 当前候选"（单模型内结论，非混合对照）。状态：**未做**。
- **REQ-FAIR-06｜重复试验抗采样波动；可疑降级样本先隔离**。源：10-08 指令 §2.2＋EXPERIMENT §5。证据：run127 ×1/×2/×4 设计符合；新链无。状态：**部分**。

### C. 薄层 vs 最小架构、防丢、防稀释（源：ROADMAP 2.2、05 E1–E3、06 相关节、04 材料权限）

- **REQ-ARCH-01｜固定 model＋可比信息权限，比"现有四薄层"vs"最小足够简化候选"**。源：ROADMAP 2.2。证据：无。状态：**未做**。下一动作：先写简化候选的"为何可能更好/丢什么/归因如何成立"再开跑。
- **REQ-ARCH-02｜E1：GPT-5.6w ×1 vs ×2 vs legacy 多遍，同规范清单**。源：05 E1＋06 防丢节。证据：run127 report（已读头部）：分窗 A 核心 0.85（×1）/0.89（×2）/0.92（×4），一次全曲 0.59，旧 MERGE 0.59，现生产珠子 0.52；round_64。核实度：已读。状态：**部分**（Op.60、旧 mg 路由、BEAD 分窗语境；GPT-6w 侧未测；生产候选 ×2 未冻结）。下一动作：gpt2 路由下复测 ×2（不必重做 ×1/×4 全套，先比最有希望的 ×2）。
- **REQ-ARCH-03｜生产用满足阈值的最薄配置**。源：06。证据：HANDOFF_PROGRESS"生产候选 ×2"（未冻结）。状态：**部分**。
- **REQ-ARCH-04｜E2：A/T-only vs 平铺 H vs 核心优先＋残差**。源：05 E2＋06。证据：run127（平铺 A 核心 0.85→0.79；残差 H 新增 0.87、A 核心 0.80→默认不加 H；round_64）。核实度：已读（report 头）＋转引。状态：**部分**（Op.60 已证明；Op.52/61 未推）。
- **REQ-ARCH-05｜H 残差四分类＋A/T 核心清单显式受保护**。源：04＋06。证据：run126 canon.json/resid.json/windows.json（存在；内容未读）、report（已读头）。核实度：已读（头）＋目录确认。状态：**部分**（Op.60；三首未全）。
- **REQ-ARCH-06｜E3：H1–H5 在当前模型池重测残差价值**。源：05 E3。证据：run126 round_63（退役 H1/H5；H4 改期待材料；H2 看尺度；H3 进 Thread 第二轮）。核实度：转引。状态：**部分**（Op.60；GPT-6w 未纳入；Op.52/61 未推）。
- **REQ-ARCH-07｜A/T 首轮独立**。源：06＋04。证据：HANDOFF_PROGRESS"Op.60 ✓"；run127 纯净珠子链。核实度：转引。状态：**部分**（Op.60；三首未全）。
- **REQ-ARCH-08｜覆盖参照用规范源清单＋量 unsupported additions**。源：06＋01 H1。证据：run126 canon＋run127"无出处新增约 0"。核实度：转引。状态：**部分**（Op.60）。
- **REQ-ARCH-09｜正式生产用当前选定/显式冻结版本输入**。源：06。证据：ACTIVE_HANDOFF"生产配置未变（run124 surface B gpt56w）"。核实度：已读。状态：**部分**（旧生产有版本；新链未冻）。

### D. 珠子（源：05 E4、06 珠子节、01 D3–D6、1003v2 A 节）

- **REQ-BEAD-01｜affect_core 不从 A/T 混写散文生成（E4 纯净珠子）**。源：05 E4＋06。证据：run127/129 round_64/65（新珠子盲比胜现生产珠子：luna 8–9/9、muse 5–7/9；Opus 覆盖 0.95 但盲比输且违规最多→写手定 GPT-5.6）。核实度：转引。状态：**部分**（Op.60；Opus 珠子结论来自旧 Opus 产物，只读引用，不新增）。
- **REQ-BEAD-02｜后见与未来定义此刻均 fail；prefix-clean（"未来隐藏是否仍自然成立"）**。源：01 D4＋06。证据：LEAK_CHECK_v2；run127"前缀违规仍多"；run130 确认违规 18 条（report 已读头）。核实度：已读。状态：**部分**。
- **REQ-BEAD-03｜facets/alternatives/sequential 内部分型**。源：01 D5＋06。证据：BEAD_v0 内部分型（模板存在；内容未读）。状态：**部分**。
- **REQ-BEAD-04｜field/bead 尺度合理；粗珠含多 sequential state 要 review**。源：01 D6＋06。证据：run101/102/103 时间轴工作（目录确认；内容未读）。状态：**部分**。
- **REQ-BEAD-05｜局部质量不低于 STRUCT_v1**。源：06。证据：round_64/65 盲比胜。核实度：转引。状态：**部分**（Op.60）。
- **REQ-BEAD-06｜时间轴辅助珠子、不做冻结权威**。源：03 提案＋02_CORRECTION 8。证据：run102_struct_timeline 等（目录确认）。状态：**部分**。

### E. 二阶理解 E5（源：05 E5、06 二字节、01 E1/E2、ROADMAP 轨道 3、10-08 指令 §3）

- **REQ-E5-01｜专用二阶任务存在；只读规范珠子内容**。源：05 E5＋06＋03 §2G。证据：run128 MECH（report 已读头：60/59/59 站生成调用；三家审核）。但输入是旧生产珠子（run110/110b），非 run130 纯净新版（10-08 指令 §2.2 明确指出）。核实度：已读。状态：**部分**。下一动作：在纯净珠子上重跑 E5。
- **REQ-E5-02｜NONE 常见到证明不硬造**。源：06。证据：run128 NONE 率表（已读）：gpt56w v0/v1 皆 0 空站（30 站全满 2.0 条）；muse v1 5/30；round_67。核实度：已读。状态：**未通过**。不成立证据：加一句约束对 GPT-5.6 无效（每站写满 2 条）。
- **REQ-E5-03｜机制 grounded 珠子；生成后独立审核过滤矛盾/外借＋删句反事实**。源：PROJECT_STATE 判断（A1–A9 真洞见 vs B1/B7 矛盾）＋10-08 指令 §3。证据：MECH_AUDIT_v0 判据偏宽（B8/B9 图像化重述也判 insight，转引）；删句反事实未做。状态：**部分**。下一动作：收紧审核判据＋删句反事实试验。
- **REQ-E5-04｜不以 NONE 率/配额/禁词/剪好段为成功；删句须说出失去什么**。源：ROADMAP 轨道 3＋10-08 指令 §3。证据：原则已立，无实验。状态：**未做**。
- **REQ-E5-05｜二阶不并入通用去重；relation 与 vivid anchors 分离保存**。源：1003v2 B4＋07_NEXT_TASK 约束 7。证据：run128 结构（目录确认）。状态：**部分**。

### F. History/Thread/Center/WHY（源：05 E6、06 相关节、01 F1–F4、1003v2 §06、02_PRODUCT_CONSTRAINTS §4）

- **REQ-THREAD-01｜首轮 History/Thread 只读珠子序列**。源：05 E6＋06。证据：run130（K=23 纯净珠子；三家 step；round_66）。核实度：已读（头）。状态：**部分**（Op.60）。
- **REQ-THREAD-02｜第二轮 adjudicate 独立 T/H 假设，不作上游权威**。源：同上。证据：run130 adjudication（吸收偏宽，待收紧）。状态：**部分**。
- **REQ-THREAD-03｜alternatives 开放；无强制单 Center；可多中心/no_single_center**。源：06＋01 F3。证据：run130 三家各 3 不同中心，Opus 第二 center（"一句很郑重的话……"）最贴（PROJECT_STATE 已读；旧 Opus 产物只读引用）。状态：**部分**。竞争假设 C9（THREAD_ADJ 单 thread_after 致收敛）待 run133 后测。
- **REQ-THREAD-04｜不塌成通用治疗/道德弧；审过早主题化/假因果/吞局部**。源：06＋1003v2 C4。证据：run130 纯净输入下"珍惜→抓紧→放手"照样长出（round_66；机制非 T 混入）。核实度：转引。状态：**未通过**。下一动作：run133（C7_STEP 加作品特异性一句）——现 partial，且原设计含新 Opus 生成，与 10-09 禁新 Opus 冲突，**需改设计**（见 §3）。
- **REQ-THREAD-05｜History 只存 durable change；R6 空步不单独优化，并入 E7 检验**。源：PROJECT_STATE（0/69 含"首次登记"，宪法 C3 承认"已改变的期待"属 History）。证据：决策记录已读。状态：**部分**（决策已立；E7 未验）。
- **REQ-THREAD-06｜H5 默认 RETROSPECTIVE_ONLY，不进实时 Affect**。源：04＋06。证据：HANDOFF_PROGRESS"needs_future 标记＋R 条件排除 ✓"。核实度：转引。状态：**已证明**（Op.60）。
- **REQ-THREAD-07｜H4 期待显式 prefix-valid（产生时/检验时分离）**。源：04＋06。证据：HANDOFF_PROGRESS"✗（未做）"。状态：**未做**。
- **REQ-WHY-01｜local WHY 与 long-range WHY 可共存；WHY 可 NONE**。源：06＋01 F4。证据：WHY_GATE_v4 旧时间轴（对照用，不可复用为 truth）。状态：**未做**（待 E7/新 timeline 重跑）。
- **REQ-WHY-02｜最强作品特异 WHY 不系统藏于次级面**。源：06＋01 G3。证据：无（呈现层未做）。状态：**未做**。
- **REQ-WHY-03｜History→WHY：WHY＝当前 bead×已成立 Thread；门控问"删历史后听法是否改变"**。源：1003v2 §06＋02_PRODUCT_CONSTRAINTS §4。证据：无。状态：**未做**。

### G. E7 呈现（源：05 E7、06 呈现节、01 G1–G5、ROADMAP 轨道 4）

- **REQ-E7-01｜语义链通过后才切 production；诊断性样稿可提早、隔离标注**。源：05 E7＋ROADMAP 轨道 4＋v3 PATCH。证据：run134_e7_diag 骨架 go.py 已落盘（progress.md 已读），未跑。状态：**未做**。
- **REQ-E7-02｜locator 短而可选**。源：06。证据：run124 强制长【听】bug（PROJECT_STATE 已读）。状态：**未做**。
- **REQ-E7-03｜KEEP/RETIRE/REPLACE/APPEND；过期【此刻】撤下**。源：06＋01 G2。证据：run124"Op.52 m.203 仍挂 m.169 旧内容等 4 条"（已读）。状态：**未做**。
- **REQ-E7-04｜终写不造新语义结论；结尾不道德化/金句**。源：06＋01 G4。证据：无。状态：**未做**。
- **REQ-E7-05｜Humanizer 仅按需＋当前输出重测 bake-off**。源：06＋01 G5。证据：run100/112 旧 bake-off（只读；humanizer_forensic 包结构确认，未重测）。状态：**未做**。
- **REQ-E7-06｜AUDIT 四层 bug（强制【听】/旧【此刻】不撤/主 WHY 缺席等）修复验证**。源：`notes/AUDIT_4LAYER_20261005.md`（**未读**，经 PROJECT_STATE/HANDOFF_PROGRESS 转引）。状态：**未做**。核实度：转引（原文未核）。

### H. 三作品泛化、溯源、盲比、冻结（源：任务要求、ROADMAP 轨道 5、EXPERIMENT §6、记忆 baseline-anchor）

- **REQ-GEN-01｜Op.52/60/61 时间审核/leak/多义/溯源全覆盖**。源：任务＋ROADMAP 轨道 5。证据：Op.60 主链完整；Op.52 仅 run128 E5 含 op52 站＋旧生产面；Op.61 仅 run108 旧补充。状态：**部分**（Op.60；52/61 待 P2 推广）。
- **REQ-GEN-02｜逐句来源/溯源链**。源：任务＋1003v2 J3。证据：manifest＋prompt 哈希链完整；raw span→meaning→下游使用链（run121_provenance 存在，内容未读）。核实度：目录确认。状态：**部分**。
- **REQ-GEN-03｜端到端盲比：新链 vs 原 V2A+Gemini 原稿 vs run124**。源：任务＋记忆 baseline-anchor。证据：Op.52 原稿已定位（notes/baselines/op52_v2a_gemini_02/05.md，存在确认）；run132 用原版 V2A 提示词在 Gemini 重建（DONE；gpro_web 版细节见 PROJECT_STATE）；Op.60/61 无原始基线，重建锚须明确标注"非真原稿"。三方盲比待 run134。状态：**部分**。
- **REQ-GEN-04｜未经三首原验收不切 production、不改验收**。源：任务＋EXPERIMENT §6。证据：生产仍 run124（ACTIVE_HANDOFF）。状态：**已证明**（遵守中）。
- **REQ-GEN-05｜DONE≠产品验收**。源：任务。证据：HANDOFF_PROGRESS 06 清单仍多项 ✗（H4、NONE、治疗弧、R6 空步、WHY/呈现、runner 缓存）。状态：**已证明**（清单诚实）。
- **REQ-GEN-06｜每轮 ZIP 到 Downloads；ACTIVE_HANDOFF≤30 行；中文报关键**。源：v3 PATCH＋记忆。证据：本机多轮 ZIP 存在；ACTIVE_HANDOFF 已读（约 30 行内）。状态：**已证明**。注：本审计按任务要求只写两文件，不产 ZIP。
- **REQ-GEN-07｜冻结回滚能力**。源：ROADMAP 轨道 5。证据：git＋manifest 可回滚 run124；新链未冻。状态：**部分**。

### I. 评审治理（源：10-09 最新用户授权＞EXPERIMENT §3/§4 旧规则）

- **REQ-REV-01｜评审阵容 GPT-5.6w、GPT-6w、Gemini Flash、Muse；自评允许但须标记；至少一名独立评审；Pro 可额外、不替代 Flash；禁新 Opus；不派子任务**。源：10-09 最新用户。覆盖说明：覆盖 EXPERIMENT §4 第 6 条"不允许主 Claude 亲自产出参赛候选"（旧禁令失效，改为"自评允许但标记"）；Opus 约束覆盖 1003v2 F5 的默认参照做法。证据：run133 计划 `RUN133_REV=gpt56w,gpt6w,opus,luna_noweb,gpro`（ACTIVE_HANDOFF）——含 Opus 且缺 Flash/Muse 具名，与新授权不符，需改。状态：**阻塞**（待 run133 改设计重跑）。下一动作：评审阵容改为 gpt56w/gpt6w/gflash/Muse（＋gpro 可选），自评项标记。
- **REQ-REV-02｜每份 judge prompt 写禁偏见条款**（戏剧化/笃定/单故事不扣分；NONE 可为正确答案；引证原文；遇证据不足判不可判）。源：EXPERIMENT §3＋记忆 drama-not-a-flaw。证据：round_63–67 评审存在（目录确认），**未逐份验证条款在场**。核实度：目录确认。状态：**部分**。下一动作：抽查两份 judge prompt 全文。
- **REQ-REV-03｜盲审匿名＋随机种子＋来源 ID；数字全脚本算**。源：EXPERIMENT §4。证据：run130 match 由 muse 判、盲比对存在（转引）。状态：**部分**。
- **REQ-REV-04｜prompt 纪律：单变量/逐句归因/DERIVATION/无作品专属/三首泛化/四分支冻前不调综合**。源：PROMPT_DEVELOPMENT_RULES＋0930 §5。证据：run133 单变量设计；DERIVATION 沿用。核实度：转引。状态：**已证明**（执行中）。
- **REQ-REV-05｜已有不测需理由；不机械补跑**（novelty_v2 剩 100、hetero 5855 只读取证）。源：10-09 任务。证据：本台账方法节（§0 #14）。状态：**已证明**（本次遵循）。

## §2 被覆盖/失效要求（7 条，不再作为验收依据，但保留来源备查）

- **SUP-01｜旧 mg 路由**（0930/1003 时代）。被 10-08 gpt2 迁移取代。证据：ACTIVE_HANDOFF 双轨现状。
- **SUP-02｜Sol 系内容调用**（run32/57/79 等）。10-05 起停新 Sol，以 5.6 取代；旧产物只读。源：HANDOFF_PROGRESS＋1003v2 F5。
- **SUP-03｜"每个 run 更新 index.html"**。10-03 撤销，改为每轮 ZIP。源：记忆 zip-per-round-no-index＋v3 PATCH。
- **SUP-04｜"主 Claude 不得产出参赛候选"**（EXPERIMENT §4.6）。被 10-09"自评允许但标记"覆盖。
- **SUP-05｜review-build 两支 MP4＋8 gaps 暂缓路线**（review_build pack：冻结旧语义做 Review V1）。旧产品层目标；新四薄层链未稳前不执行，且 MP4 渲染非当前验收项。状态：冻结。
- **SUP-06｜vnext 旧架构**（Articulation/Situation/Sparse/WHY V3 等）。被 10-05 四层架构取代。源：03_PROPOSED_ARCHITECTURE。
- **SUP-07｜parallel pack 的"不重做冻结语义"清单**（Generator/RAW/Canonical/Distillation V3…）。针对旧生产基线；新链 E1–E4 已部分重做（run126/127），旧冻结清单不再逐项适用，以 06 验收为准。

## §3 最关键缺项（按阻塞程度）

1. **gpt2 真实路由未打通**（REQ-ROUTE-01/02/04）：run131 FAILED；runner 默认仍 mg；其后 FAIR 全系、E1 复测、run133/134 全阻塞。10-09 称 gpt2 已恢复——待重跑验证。
2. **run133 partial ＋设计与新授权冲突**：原设计用新 Opus 生成（10-09 已禁），评审阵容缺 Flash/Muse 具名。需改设计后重跑，才能裁决 Thread 治疗弧假设（REQ-THREAD-04）。
3. **E5 NONE（REQ-E5-02 未通过）＋审核偏宽＋反事实未做**：二阶链条的验收核心，需在纯净珠子上重跑＋收紧 MECH_AUDIT＋删句反事实。
4. **H4 prefix-valid（未做）、WHY 全系（未做）、E7 全系（未做）**：后半链空白；R6 空步已决策并入 E7（REQ-THREAD-05），故 E7 是汇合点。
5. **三首泛化（REQ-GEN-01 部分）**：52/61 新链未推；Op.60/61 基线只有重建锚（须标非真原稿）；端到端三方盲比待 run134。
6. **评审条款逐份验证缺失**（REQ-REV-02）：禁偏见条款是否真在每份 judge prompt 中，未逐验。

## §4 读取不完整之处（诚实声明）

1. 大 ZIP（#7–#10，共约 2.8 万文件）的 outputs/raw 未批量读（任务指令如此）；需求结论以各包 md＋本机 run 报告为准。
2. hetero 5855 文件仅顶层目录核证；humanizer 包仅 README 级。
3. 1003v2 的 01/03/05/07/09/10/11/14 未读；parallel/vnext/review 三包任务文件为抽读（非逐份）。
4. `notes/AUDIT_4LAYER_20261005.md` 未读，run124 bug 经 PROJECT_STATE 转引。
5. round_63–67 评审细则、run121_provenance 内容、run124 报告全文未逐读。
6. ZIP 内文件与本机副本未做 sha 逐字节比对；chat_findings 以本机副本为准（与 ZIP 同名）。
7. 附件 v3 包与 Downloads v3 包仅清单级一致（同名 15 文件），未逐字节比对。
8. `tools/gpt2_adapter.py`、各 run `go.py` 内容未读（代码工作属主会话，本审计只读）。
