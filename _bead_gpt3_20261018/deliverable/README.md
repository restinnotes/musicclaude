# 船歌 Op.60 · A Pool → Bead / STRUCT（gpt3 正式生成，2026-10-18）

- **READER.md**：十四颗可直接阅读的新 Bead（模型原样输出拼接，未人工改写）。
- **struct/S01–S14.json**：每段的正式结构化资料：facets（精确小节、原稿引文、独立来源数、置信度、是否进入正文）、alternative_readings（不同完整听法及冲突关系）、internal_sequence（段内先后变化）、merged_as_equivalent、rejected（范围不符/拼接等拒收理由）。每条引文附 `quote_verified`（脚本逐字核对）。
- **DIFF_vs_short.md**：与旧短版的差异（字数、各类条目数由脚本计算；文字说明为模型自述）。
- **EVIDENCE.json + raw_responses/**：每段的 gpt3 证据目录、会话句柄、模型 gpt-6-thinking / max、Temporary+Unpersonalized、终止校验、原样请求与响应及 sha256。完整证据（HTTP 记录、离线 PNG）留在本机 `D:\musicclaude\gpt2agent-safechain\runs\gpt3\`。

## 做法
- 输入：冻结十四段 structure.json、短版 FINAL_BEADS（仅作可读性参考，并标注哪些颗含已排除来源）、**24 份非 Muse A 原稿**。按用户 10-18 要求，Muse 不调用、其 6 份历史原稿也不使用；交接包"04 核对线索"中依赖 Muse 原稿的 S02/S04 线索因此未提供给模型。
- 每段一次独立 gpt3 调用（同一提示词模板 `prompts/TEMPLATE.md`，只替换段号/小节），附件为 `input_bundle.zip`。14/14 成功，未重试。
- 本地 agent 未撰写或修改任何正文/STRUCT 内容；脚本只做拼接、计数与引文核对。

## 脚本核对结果
- 引文逐字命中：1083/1083（14 段全部 100%）。
- 无任何条目以 SRC-muse 为来源。
- S13 所有 facet 小节均落在 103–110 内，未把 111 提前写入。

是否合格由用户判断。
