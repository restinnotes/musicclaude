# DELIVERABLES_v3 — 全自动 A-Pool→珠子 实验交付索引（2026-10-17）

> 本轮（任务书 V）交付一览。除标注者外，文件都在 `D:\musicclaude\_bead_auto_20261016\out\`。
> 停止规则已执行：珠子实验完成后不再发起新的研究提示；判断权交还用户。T、H1–H5 未进入本轮珠子生成。

## ① 每路线 找到/补齐/采用 计数 — `ROUTE_COUNTS_v3.md`

12 路线（Gemini-flash-int/web、gpro-int/web、Muse-int/web、Luna-int/web、GPT-5.6w-int/web、GPT-6w-int/web）× 各 3 份采用 = **36 份**；历史原件直接采用 25 份 + 本轮补齐 11 份（gpt56w 各 2、luna-int 1、gpt6w 各 3）。未采用历史原件 43 份全部保留归档；V2A/Gemini 基线 5 份（A-orig）单独保留为质量参照。同族版本不互替、副本 sha 去重不计新轮——执行记录在 `A36_LEDGER.md`。

## ② 完整来源清单 + 路径（含 V2A 基线） — `A36_LEDGER.md` / `A36_LEDGER.json`

36 份采用件逐条给出 run、模型名、prompt 版、轮次、字符数、绝对路径、sha256 前 12 位；第二节列 43 份保留归档 + 5 份 V2A 基线的完整路径。珠子每段的段内台账（来源行 model|channel|runjob|SHA12）在 `STEP4_inputs_v3\`（车道 prompt）与 `out\BEADS_v3_INTERNAL.md` 段头可见。

## ③ 冻结分段（C2，14 段，无新切点） — 本文件 + `A_POOL_MAP_v3.json`

S01 mm.1–3 序奏 / S02 4–16 第1主題 / S03 17–23 間句 / S04 24–34 第1主題(確保) / S05 35–39 間句 / S06 40–50 第2主題前半 / S07 51–61 第2主題前半(確保) / S08 62–71 第2主題後半 / S09 72–77 間句 / S10 78–83 挿入句 / S11 84–92 第1主題(再現) / S12 93–102 第2主題後半(再現) / S13 103–110 第2主題前半(再現) / S14 111–116 終結句。
主力/跨段/全局复核（GPT-6w 三分片独立判定）结论:`A_POOL_REVIEW.md` —— 403 单元全覆盖,放置问题 0,UNCERTAIN/UNRESOLVED 0,DROP 5。珠子生成后未调整任何分段或座椅（-chair- 约束遵守）。

## ④ 全部珠子正文 — `BEADS_v3_INTERNAL.md`（167 KB，逐字未改一字）

14 段珠子①节原样收录（GPT-6w=gpt-6-thinking / effort=max，经 gpt2-safechain 双文件门禁）；每段末行是机器抽取的该珠引用单元清单。生成车道的原始响应与失败证据在 `step4_out\raw|err|meta\`、`beads\STEP4_SXX.md`。

## ⑤ 珠子↔来源 溯源 — `BEAD_TRACE_v3.md` + `WIDE_HEADONLY_v3.md` + 本文件"未引用与缺席"

逐段列出珠子引用的 SRC id（机器抽取,非模型自报）；对照池内槽位统计：

| 槽位 | 池内 | 被珠子引用 | 备注 |
|---|---|---|---|
| PRIMARY | 126 | 123 | 未引用 3 条:SRC-gpt56w-int-2-U21、SRC-luna-web-3-U13、SRC-gpt6w-web-2-U12 |
| CROSS | 217 | 217 | 全部被引用 |
| GLOBAL | 55 | 0 | 按版式设计不入车道（见 `STEP4_inputs_v3\_ATTACH_LAYOUT_v3.1.md`） |
| DROP | 5 | 0 | 剔除台账在 `A_POOL_REVIEW.md` |

引用 id 对 `A36_units.json` 全注册校验：**0 条幻觉 id**。
字节上限收纳策略的两项偏差与影响,已如实标注：(a) WIDE 跨段条目（覆盖≥4 段）只在其归属段收录全文、其余段仅头行——非归属段对它们的引用共 **74 处**（按段明细:`WIDE_HEADONLY_v3.md`）,这些引用只能视为头行级证据；(b) GLOBAL 整曲底色不随车道,不产生本轮引用。

## ⑥ 一份短篇读者版 — `READER_v3.md`（47 KB）+ `BEADS_FOR_USER.md`（上一轮对照）

14 段珠子的②节读者正文原样摘集；每段首行是珠子自带标题。框标记（`<box>`）缺失处正文逐字完整、以段标 `[box-tag-unclosed, body-intact-verbatim]` 注明（共 10 段）。

## 运行事实（透明性备忘）

- 珠子生成 14 车道并行首波：12 OK（491–1302 s,5,925–8,187 chars）＋2 条 `initializer_queue_timeout`（600 s 队列未排到,提交前失败、无提交标记）。按"明确未被接收可安全重发"重试 S02/S05 单波:双双成功（523/644 s）,无内容降级、无模型更换。全程未把失败归因于池内容长度（失败车道与成功车道字节形态一致）。
- 抽取器修复记录：SRC id 正则曾漏连字符段；①/② 锚点曾漏 H1 形态与文件首 BOM——修复后 12/14→14/14 全量重跑一致,`BEADS_v3_INTERNAL.md`、`READER_v3.md`、`BEAD_TRACE_v3.md` 均为终版。
- 上一轮珠子（`BEADS_FOR_USER.md`）与 READER_v3.md 可直接盲对；两版均由冻结池生成,差异只来自池扩充与容器版式。

## 等用户决断的事项

1. READER_v3.md 与旧版珠子的质量对比结论（你定取舍/是否进入下一轮合并或重生成）。
2. WIDE/GLOBAL 两条字节收纳偏差是否接受为长期版式（摘要见⑤;完整规则在 `_ATTACH_LAYOUT_v3.1.md`）。
3. 未引用的 3 条 PRIMARY 是否需要人工查看（其文本在 `A36_units.json`,id 已列出）。
