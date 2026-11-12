# 基线与关键产物索引（R1，Muse 编制，2026-10-08）

> 用途：供主 Claude 做盲比与端到端评估的配对索引。只记录事实与证据出处，不做审美裁决。
> ROOT = `D:\musicclaude\unified_run_handoff_20260924\unified_run_handoff_20260924`。路径均为绝对路径。sha256 为全文件哈希。字数为去空白字符数。

## 1. 原始 V2A + Gemini 基线（Op.52：有；Op.60/61：缺失）

| 作品 | 文件 | sha256（前16） | 生成模型/提示词版本及证据 | 日期 | 字数 | 整篇/局部 | 可否配对 |
|---|---|---|---|---|---|---|---|
| Op.52 | `ROOT\notes\baselines\op52_v2a_gemini_02.md` | `b2247fea5fe647e3` | Gemini 用 V2A 原版。证据：用户成功标准“质量不低于 V2A 原版在 Gemini 上的水平（参考 reference/ 中的文本 02、05）”，见 `notes\handoff_20261003_v2\sources\raw_chat_20260930.md:1135`；提示词原文见 `prompts\A_orig_V2A.txt` | 源文件 09-25；提取 10-08 | 4628 | 整篇 | ✅ 可与新稿配对 |
| Op.52 | `ROOT\notes\baselines\op52_v2a_gemini_05.md` | `2c89c68279ae5b78` | 同上 | 同上 | 3336 | 整篇 | ✅ 可与新稿配对 |
| Op.60 | — | — | **缺失**：全仓（SHUFFLED/NINE/blind/船歌文件名、prompts/versions、runs/run00–run01、ai_log、research_notes、notes）无 V2A+Gemini 整篇产出；`notes\e9_blind_op60\` 四篇未注明 V2A/Gemini 出处 | — | — | — | ❌ 不可配对 |
| Op.61 | — | — | **缺失**：同上，无任何 V2A+Gemini 整篇产出记录 | — | — | — | ❌ 不可配对 |

源头：`ROOT\reference\OP52_NINE_TEXTS_SHUFFLED.md`（sha256 `5ff33fe0…`，09-25）。提取方式：按 `## 文本 NN` 切分逐字节比对一致（含前导空行修正），原文逐字、未改。注意文本 02（4628字）比文本 05（3336字）长约 39%。

## 2. 九篇样本中其它文本的出处与用户评价

**明确结论：未找到用户对九篇中任何一篇的“好/坏”公开标注。** 有界搜索（`THREAD_USER_PROMPTS…` 全文119行、`HANDOFF_PROGRESS_2026100*`、`handoff_20260930/03`、`e9_blind_op60`、`chat_findings_20261005`）中，“文本02/05”仅作为质量标尺被引用（上表出处），无好坏排序；Grep“公认/争议/最好/最差/喜欢/不行”只命中 run100 Humanizer 模型排名（与九篇无关）。

| 类别 | 候选 | 用户原话与出处 |
|---|---|---|
| 公认好稿 | 文本 02、05（作为整体标尺，非单篇加冕） | “质量不低于 V2A 原版在 Gemini 上的水平（参考 reference/ 中的文本 02、05）”——`notes\handoff_20261003_v2\sources\raw_chat_20260930.md:1135`（01_GOAL.md §5 成功标准） |
| 公认好稿（第2个） | 未找到明确标注 | — |
| 有争议稿 | 未找到明确标注 | — |
| 有争议稿（第2个） | 未找到明确标注 | — |
| 相关盲比（Op.60，非九篇） | `notes\e9_blind_op60\船歌_A/B/C/D.md`（10-02） | 四篇均无模型/提示词版本标注，无用户结论落盘；A（sha `3509f6be…`）最长，C 最短。不可当 V2A 基线用 |

## 3. 当前生产呈现稿（run124_render，10-05；上游 run120–123）

生成链：珠子（run110/110b Muse 稿，sha1 `a671bc61…`）→ Humanizer（Sol→改错→Luna→Grok）→ ATTN 选择（run122 ATTN_v1，chooser gpt56w/sol61_cx）→ run124 只套呈现规则 A/B（**未重新调用选择模型**，506 次调用全是呈现+盲比 RT_COMPARE_v0）。评审见 `runs\run124_render\reviews\round_61.md`。

| 作品 | 条件B终稿（gpt56w 链） | sha256（前16） | 字数 | 整篇/局部 |
|---|---|---|---|---|
| Op.52 | `runs\run124_render\surface__B__gpt56w__op52.md` | `740483442b5e68d3f` | 15371 | 整首16站全量（呈现稿，非边听边读文章体） |
| Op.60 | `runs\run124_render\surface__B__gpt56w__op60.md` | `8436c931b0e6c54e0` | 11464 | 整首14站全量，同上 |
| Op.61 | `runs\run124_render\surface__B__gpt56w__op61.md` | `993364063b020adbdc` | 11556 | 整首12站全量，同上 |

上游对照：run120（`surface__gpt56w__op52/60/61.md`，10-05 08:41，Humanizer+ATTN_v0）；run122（ATTN_v1）；run123（ATTN_v2）；run121 为出处链。sol61_cx 链各有对应 `surface__*__sol61_cx__*.md`。**体裁提醒**：以上皆为分站实时呈现稿（16/14/12 站），与 V2A 基线“整篇边听边读文章”体裁不同，配对盲比时需注明体裁差。

## 4. run126–run130 关键产物（覆盖作品：全部 Op.60；run128 兼含 Op.52）

| run（日期） | 报告 / manifest | 核心输出 | 评审 | 覆盖 |
|---|---|---|---|---|
| run126_canon_op60（10-06） | `report.md`、`manifest.json`、`run_manifest.json` | 规范清单：`canon.json`（`e46125f1…`，A 237/T 219 核心）、`units.json`、`windows.json`（`f1e828f0…`，9 窗口 w1–w9）、H 残差 `resid.json`（`7f1c1c328…`）；抽取 muse、聚类/残差 gpt56w；`outputs/` 359 个 CANON 文件 | `reviews/round_63.md` | Op.60 |
| run127_bead_e1e4（10-07） | `report.md`、`run_manifest.json`、`calls.json`（666 次：gen+merge gpt56w，覆盖 muse/luna，leak gpt56w/muse） | BEAD 分窗：`fulltexts/N_s1–s4.md`（×1，~9.8万字符）、`M2.md`（×2→合并，`2bb99128…`，44461字）、`M4.md`（×4→合并，`ba4def03…`）、`L_BEAD/L_MERGE/L_SYN1.md`；`leak.json`（LEAK_CHECK_v2 确认 18 违规）；`coverage.json`、`compare.json`、`trace.json`；`outputs/` 696 个 | `reviews/round_64.md` | Op.60 |
| run128_mech_calib（10-07） | `report.md`、`run_manifest.json`、`calls.json`（778 次） | E5 输出：MECH_v0→v1 单变量 NONE 校准，`outputs/` 783 个 AUDIT/GEN 文件；输入为现生产珠子（op60 14 站 + op52 16 站）；结论 muse 0→5 NONE 站，gpt56w 仍 0 | `reviews/round_67.md` | Op.60 + Op.52 |
| run129_opus_bead（10-07） | `report.md`、`run_manifest.json`、`results.json` | Opus 珠子：`fulltexts/O_s1.md`（`c9c7e163…`，44277字，A 存活 0.95/T 0.90 但违规 42）；与 run127 N_s1 同题对照；`outputs/` compare 文件群 | `reviews/round_65.md` | Op.60 |
| run130_thread_e6（10-07） | `report.md`、`run_manifest.json`、`steps.json`（69 步）、`adjudication.json`、`audits.json` | Thread 两轮：清洁后珠子 `beads_clean.md`（`a04346e4…`，43989字，23 珠）、`centers.json`、`leak.json`；第一轮只读标题+【此刻】；“珍惜→抓紧→放手/接受”弧三家皆出 | `reviews/round_66.md` | Op.60 |

注：round 编号与 run 不按序（63→126，64→127，65→129，66→130，67→128），引用时以文件名配对为准。

## 5. 正式宪法与验收标准

| 文件 | sha256（前16） | 状态 |
|---|---|---|
| `reference\PRODUCT_CONSTITUTION_V2.md`（09-25） | `b63e16d9b7f69cbff` | 正式宪法本体（“产品最高层规格”）；仓库内无更新版本——`notes\CONSTITUTION_CHECK_v2*.md` 只是行为核对表（草稿/汇编），不是宪法新版 |
| `notes\chat_findings_20261005\music_pipeline_chat_findings_20261005\06_ACCEPTANCE_CRITERIA.md`（10-05） | — | 10-05 验收标准（A/T 独立、H 残差、BEAD 五条、E5 NONE、Thread 等，覆盖三首作品） |

## 6. 最关键的缺失（按影响排序）

1. **Op.60/Op.61 没有 V2A+Gemini 整篇基线**——三首配对盲比只能做 Op.52；Op.60 现有最接近的是 e9 四篇（体裁接近但出处不明），Op.61 无任何整篇参照。
2. **九篇无用户好坏标注**——“公认好稿/争议稿”只有文本 02/05 作整体标尺一句，无单篇评价，无法做“好稿 vs 新稿”定向对比。
3. **run124 生产稿与基线体裁不同**（分站呈现稿 vs 整篇文章）——直接盲比需先声明体裁差，或另选 STRUCT/MERGE 整篇稿配对。
