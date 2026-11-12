# SOURCE / Pool 保真审计

审计时间：2026-10-17T17:14:11.596875+00:00。根目录：`D:\musicclaude`。只读原件、旧构建代码和新 manifest；本次仅在 `_bead_quality_20261017/audits/` 写交付文件。未调用模型、未访问网络、未生成珠子、未修改旧文件或生产 Pool。S13 只做 UID 与传输完整性的机械检查，不重复其音乐事实核查。

**结论：正式来源可以冻结为真实标签证据支持的 30 份。** 原名义 30 份含两份 Sol，已明确排除；在 safechain 的 10 月 11 日旧任务目录找到两份真实 `gpt-5-6-thinking` 同提示输出，主 agent 已采用为 `SRC-gpt56w-int-r1` / `SRC-gpt56w-web-r1`。这不是新增采样。先前按 28 份运行的 pilot 应继续标作 pilot28，其两路同 Pool 的对照关系不变。

这里的“身份支持”按证据层级记录：请求配置、运行器初始化、服务端返回标签分别保存；不将本地别名当作对上游权重的独立鉴定。**Luna-int 第三份实际联网，30 份不等于每个组都有三次严格同条件离线/联网样本。**

## 1. 最终交付与主 agent 使用方式

- `SOURCE_POOL_MANIFEST.json` 的 `sources` 恰好 30 条正式来源；另有 `excluded_audited_sources` 保留两条已剔除 Sol 的审计证据，不可混算。
- 每条包含原始绝对路径、完整 SHA256、真实字符/字节数、原元数据、prompt 规范化 SHA、模型与工具证据，以及每个 UID 的原文偏移、行号、范围、文本 SHA、继承标题。
- `REPLACEMENT_UNITS.json` 顶层 `adopted` 为 ledger 结构元数据，`sources` 与 A36 的单元结构兼容；两份各 12 个连续原文段，24 段串接可精确还原原文件。两份各 U01、U12 为前言/整曲总结，单列 GLOBAL；不从总结正文里的小节号推导局部范围。
- 未重写 Pool。下面的旧 Pool 问题针对冻结包；新 FULL 的修复状态以本次 `live_formal30_validation` 快照为准，不按 `sources/` 目录文件总数判断。

## 2. 身份纠错与历史替补

`SRC-gpt56w-int-1` 和 `SRC-gpt56w-web-1` 的原 meta 逐字为 `"model_name": "gpt-5.6-sol#xhigh (web, mimicgate)"`，`stdin_mode` 为 `mg_file`。它们的 `gpt56w` 只是旧 key，不是 5.6 Thinking 身份。旧 ledger 的“排除旧 Sol”与实际采用存在矛盾。当前正式名单必须保留排除记录，不能只改模型显示名。


- `SRC-gpt56w-int-1`：原件 [D:/musicclaude/music_work_since_1008v3_20261009/runs/run106_gpt56_material/outputs/A-int__A_int_v1__gpt56w__op60__s1.md](D:/musicclaude/music_work_since_1008v3_20261009/runs/run106_gpt56_material/outputs/A-int__A_int_v1__gpt56w__op60__s1.md)；元数据 [D:/musicclaude/music_work_since_1008v3_20261009/runs/run106_gpt56_material/meta/A-int__A_int_v1__gpt56w__op60__s1.json](D:/musicclaude/music_work_since_1008v3_20261009/runs/run106_gpt56_material/meta/A-int__A_int_v1__gpt56w__op60__s1.json)；SHA `22359c50ba24b67146fae8926d0fcafe1161a83c2186e4cb3603f82ae3d14ceb`。

- `SRC-gpt56w-web-1`：原件 [D:/musicclaude/music_work_since_1008v3_20261009/runs/run106_gpt56_material/outputs/A-web__A_web_v2__gpt56w__op60__s1.md](D:/musicclaude/music_work_since_1008v3_20261009/runs/run106_gpt56_material/outputs/A-web__A_web_v2__gpt56w__op60__s1.md)；元数据 [D:/musicclaude/music_work_since_1008v3_20261009/runs/run106_gpt56_material/meta/A-web__A_web_v2__gpt56w__op60__s1.json](D:/musicclaude/music_work_since_1008v3_20261009/runs/run106_gpt56_material/meta/A-web__A_web_v2__gpt56w__op60__s1.json)；SHA `7bfd64e80946ee87b0bbc73610424d9946ba41ed7c3c47189463d6bd781c79d4`。


已核实的替补（使用新 SRC，旧 Sol UID 不复用）：


- `SRC-gpt56w-int-r1`：[D:/musicclaude/gpt2agent-safechain/runs/yi-cookie-repair-20261006/job-2ee58aaae2e043a7a531b3dd4047022d/response.txt](D:/musicclaude/gpt2agent-safechain/runs/yi-cookie-repair-20261006/job-2ee58aaae2e043a7a531b3dd4047022d/response.txt)，4581 字；SHA `20ff2e27bd7b4f8376d7b99291b33c114ae434a53cec368e2bfa622083fd6d8d`。请求/服务端均 `gpt-5-6-thinking`，`max`；完成记录、终端消息和 response SHA 均通过。prompt 规范化 SHA `c4c4f98386ab47efb54a4e9d6173ce2abd2a6e0038267903b242870fdaa61124`，与现用 A_int_v1 完全一致。工具消息观察数 0；int 为 0，web 实际观察到 `web.run`。详见同目录 `started.json`、`result.json`。

- `SRC-gpt56w-web-r1`：[D:/musicclaude/gpt2agent-safechain/runs/yi-cookie-repair-20261006/job-3da49a4b00a34e89b9cf83236bc36645/response.txt](D:/musicclaude/gpt2agent-safechain/runs/yi-cookie-repair-20261006/job-3da49a4b00a34e89b9cf83236bc36645/response.txt)，5616 字；SHA `d6c2de25e3e4ccb9497f02ccc84b868f71eeb2ca5b0ccab41008725ed50a6e26`。请求/服务端均 `gpt-5-6-thinking`，`max`；完成记录、终端消息和 response SHA 均通过。prompt 规范化 SHA `8066a8b43e47985d1956ecd57800d597268ed127cd56dc320bbbfc664eed8289`，与现用 A_web_v2 完全一致。工具消息观察数 19；int 为 0，web 实际观察到 `web.run`。详见同目录 `started.json`、`result.json`。


替补来自 10 月 11 日原任务存档，不在 `music_work_since_1008v3_20261009` 的 A36 inventory 采集范围内，因此只查旧 A36 inventory 会错误地得出“无替补”。此前发现的 run30 不是本次替补：s1 `failed`、0 字；s2 `suspect_degraded`，且 provider_meta 记有 web_citations=2、search_result_groups=6，不应作为同条件 int 填数。最终 30 份原件 SHA 均不同，两份替补也不同于已有四份 5.6 Thinking fill。

## 3. Luna 第三份与同条件限制

`research_fill/run_luna_fill.ps1` 第 12 行显式 `-m gpt-6-luna`，所以不能因为 ledger 没有 model_cli 就把它认成 GPT-6 Thinking。该命令没有禁止内建 web_search；raw 第 6 行 assistant_message 为：

> 我会先核对乐谱的小节编号，再按听感把作品分成几个有依据的阶段来讲；情绪描述会明确当作聆听中的解释，而不是唯一标准答案。

同一 raw 在 8、11、14、17、20、24、27 行出现七条 `item.completed` / `web_search`，前五条有结果，后两条结果为空。第 8 行 query 为 `Chopin Barcarolle Op 60 score measure numbers pdf 112 bars ...`。因此“tool-free / noweb”描述不真实；模型命令身份可证，后端原始模型标识未在这份 JSONL 中返回。作为用户批准的质量材料可留用，作为第三次离线重复不成立。前两份 Luna-int raw 未观察到 web_search；Luna-web 三份分别有 10、15、12 次完成的 web_search。


[D:/musicclaude/_bead_auto_20261016/research_fill/run_luna_fill.ps1](D:/musicclaude/_bead_auto_20261016/research_fill/run_luna_fill.ps1:12)；[D:/musicclaude/_bead_auto_20261016/research_fill/raw/A-int__A_int_v1__luna__op60__f1.jsonl](D:/musicclaude/_bead_auto_20261016/research_fill/raw/A-int__A_int_v1__luna__op60__f1.jsonl:8)



同条件还应分开记录以下变化：

- 历史 gflash/muse/luna A-int prompt 为 273 字，规范化 SHA 前缀 `1c769a248faa`；GPT-w A-int 为 289 字、`c4c4f98386ab`，额外带有“回答时请不要进行联网搜索。”。相同 `A_int_v1` 名称不代表逐字同 prompt。Luna fill 仍用 273 字版本。
- A-web 同提示规范化 SHA 前缀为 `8066a8b43e47`。gflash-web 前两轮为 init/ndjson 日志，第三轮为 OpenCode 风格工具日志，不能称同一 harness 的严格复测。
- gflash-int 三份各记录 attempts=2；gflash-web 第二份 attempts=3。独立结果/独立会话可核实，不代表无重试随机样本。
- Muse-int raw 有 read/bash/glob 等失败工具请求；不能凭“int”声称模型从未尝试工具。GPT-w int fill 的 bounded observations 出现 unknown 工具事件，未足以证明为联网，也不应据此宣称已强制完全无工具。
- Muse 及部分历史来源只有 meta 的模型路由声明；gflash 的五份 raw init 可再次核对 `gemini-3.8-flash-high`；GPT-w fill 与两份替补另有 server model_slug。manifest 区分这些证据强弱，不伪装成等强度的身份鉴定。

## 4. 连续原文、截断和计数


冻结包与 `_bead_auto_20261016/out/` 的 ledger、units、v3 map 逐字节相同。原名义 30 份的原件 SHA 全部匹配 ledger，全部 **354 个 unit** 经 CRLF/CR→LF 标准换行解码后均为连续原文子串。严格不做换行规范化时仅 **157 / 354** 命中；其余为原文件 CRLF 与 JSON LF 的差异，不能把“逐字”误报成“逐字节”。manifest 同时提供两种结果。

将 unit 正文与 `title_inherited` 对回原文件，**未覆盖的非空白字符为 0**，没有找到 unitize 把正文重写、定长剪尾或漏掉整个后半段的证据。13 个无范围标题壳已折入后继单元的 `title_inherited`，UID 出现跳号是正常的；例如 gflash-int-3 的 U03/U05/U07/U09/U11/U13 对应六个阶段，不是只留了三段。`n_units` 是折叠前计数，数组长度/`n_units_real` 是折叠后计数。

仍有 **13 个带范围的 Markdown 标题单元**没有自有正文，因为 title-only pass 只折叠“没有范围”的标题。例：`SRC-gpt6w-web-1-U09` 只是“mm.40–61…心事”的标题，实质段落在 U10；`SRC-gpt6w-web-3-U02` 也是标题。不能用这些标题当新增证据票；单行 bullet 可能本身含完整叙述，不能把所有 `text == head_line` 都误判为空标题。

旧 ledger 的 19 份 historical “chars”实际是文件字节数，11 份 fill 则为输出字符串长度；例如 gflash-int-1 为 6937 字节、2714 个 LF 文本字符。该列混用单位，不宜用于模型表达长度比较。最终 manifest 已分别给 bytes 与 characters。

正式 30 份包括原 28 份的 329 个 unit，加替补 24 个，共 **353 个 unit**；被剔除 Sol 与 V2A 均不计入。

## 5. Pool 收纳与假引用判别

旧 `build_step4_v3.py` 正文实现（不是头部注释）在超过字节预算时把 WIDE 门槛从 4 降为 3；只在第一个覆盖段放全文，后续段仅列 UID/模型/范围，并禁止引用缺失正文。

| 旧段 | map 条目 | 真正可见正文 | WIDE 头行 |
|---|---:|---:|---:|
| S02 | 60 | 54 | 6 |
| S07 | 44 | 37 | 7 |

S02 的非 GPro 缺正文 UID：`SRC-luna-int-1-U02`, `SRC-gpt56w-int-1-U11`, `SRC-gpt56w-int-2-U14`, `SRC-gpt6w-web-3-U02`。S07 的非 GPro 缺正文 UID：`SRC-muse-int-3-U04`, `SRC-gflash-web-3-U04`。例如 S07 的 Muse-int-3 U04 有 264 字正文，旧附件只有头行；不能把未读正文当作“模型阅读后主动舍弃”。

GLOBAL 全部 55 条未随旧段输入（原名义 30 份中为 49 条）。提示称“全文见 A_POOL_MAP_v3.json”，但该 map 的 global 只有 UID/ranges/chars 等索引，**没有 text 字段**；真正全文在 A36_units 和原件。旧 `A_POOL_REVIEW.md` 的“GLOBAL 进入每段第五部分”与实际 builder 相矛盾。最终正式 30 来源的 GLOBAL 为 51 条，仍应明确它们是否只归档、是否实际输入，不把归档数当阅读覆盖数。

14 个旧珠子的机器提取 UID 均存在：未发现捏造不存在 UID。S02、S07 的提及 UID 也都属于其旧 map。可是 `merge_step4_beads.py` 只检查 ID 存在，不验证本段是否传了正文、是否在当前白名单、更不验证句子被该来源支持。旧内部文本把“保留／舍弃／风险／不可使用”中的 UID 一并抽取为引用，因而**mentions 不是 adopted citations**。尤其当前被排除的 GPro/Sol 在旧珠子有真实 UID，属于不合格来源引用，不能自动洗白为新 30 份的证据，也不能一概说旧作者编造了 UID。

S02 的 map 有 `SRC-muse-int-1-U03` 正文，但旧珠子全文未提及其 UID；S07 的 `SRC-gpt56w-web-3-U06` 也未提及。相反，“不可使用的 WIDE”清单列出的 UID 只是拒用登记。manifest 分开列出 missing / unmentioned / WIDE / now-excluded，避免混算。

## 6. S02：具体表达在哪里被泛化

以下均为现存文件逐字引文；比较的是表达保留，不把源文本的编号、历史陈述视为已核真的事实。


`SRC-muse-int-1-U03`；[D:/musicclaude/music_work_since_1008v3_20261009/runs/run08_final_models/outputs/A-int__A_int_v1__muse__op60__s1.md](D:/musicclaude/music_work_since_1008v3_20261009/runs/run08_final_models/outputs/A-int__A_int_v1__muse__op60__s1.md:12)

> 像靠在船舷上，眼睛看着远处，不敢看太用力，怕把这片刻看碎了。


旧读者正文：[D:/musicclaude/_bead_quality_20261017/baseline_package/beads/STEP4_S02.md](D:/musicclaude/_bead_quality_20261017/baseline_package/beads/STEP4_S02.md:168)

> 眼前的一切太珍贵了，怕自己动作稍微大一点，就把它惊醒。


视线、船舷和“不敢看太用力”的具体身体动作，变为通用的动作轻重与怕惊醒。该源 UID 未出现在旧内部账本，不能认定句子直接由此改写；这里只确认本可使用的独特表达没有保留。


`SRC-muse-int-2-U03`；[D:/musicclaude/music_work_since_1008v3_20261009/runs/run08_final_models/outputs/A-int__A_int_v1__muse__op60__s2.md](D:/musicclaude/music_work_since_1008v3_20261009/runs/run08_final_models/outputs/A-int__A_int_v1__muse__op60__s2.md:11)

> 你想起一段很好的过去，你知道回不去了，但你此刻并不想回去，你只是觉得“有过真好，但有过就意味着没了”。


旧读者正文：[D:/musicclaude/_bead_quality_20261017/baseline_package/beads/STEP4_S02.md](D:/musicclaude/_bead_quality_20261017/baseline_package/beads/STEP4_S02.md:182)

> 像忽然翻到一张发黄的旧照片，先感到曾经的暖意，过一会儿，才感到那一点无法重新触及的距离。


原来的“不想回去”与“有过即意味着没了”的矛盾被改成常见的旧照片与距离。原件的 138 小节前提有风险；表达好不等于能不经对齐直接入 S02。


`SRC-muse-web-3-U03`；[D:/musicclaude/music_work_since_1008v3_20261009/runs/run37_pool_novelty/outputs/A-web__A_web_v2__muse_web__op60__s3.md](D:/musicclaude/music_work_since_1008v3_20261009/runs/run37_pool_novelty/outputs/A-web__A_web_v2__muse_web__op60__s3.md:23)

> 第一次是安慰，第二次是犹豫，第三次已经有点疼了。


旧读者正文：[D:/musicclaude/_bead_quality_20261017/baseline_package/beads/STEP4_S02.md](D:/musicclaude/_bead_quality_20261017/baseline_package/beads/STEP4_S02.md:174)

> 第一次是：“此刻很好。”
> 
> 再说一次，已经有一点不舍。
> 
> 又一次回到那里，仿佛心里多了一句没有说出口的话：“能不能再久一点？”


保留了三次停留的结构，却把安慰→犹豫→疼的不同质地改成幸福→不舍→延长幸福，更统一，也更单一。标题“太幸福了，反而不敢用力”则确实沿用了这份源的好表达，不能说全盘丢失。



## 7. S07：中段的身体处境与二阶感受


`SRC-muse-web-2-U04`；[D:/musicclaude/music_work_since_1008v3_20261009/runs/run08_final_models/outputs/A-web__A_web_v2__muse_web__op60__s2.md](D:/musicclaude/music_work_since_1008v3_20261009/runs/run08_final_models/outputs/A-web__A_web_v2__muse_web__op60__s2.md:31)

> 好不容易幻想出一个温暖的地方，赶紧搬进去，但心里不踏实，总要起来检查门锁。


旧读者正文：[D:/musicclaude/_bead_quality_20261017/baseline_package/beads/STEP4_S07.md](D:/musicclaude/_bead_quality_20261017/baseline_package/beads/STEP4_S07.md:137)

> 越珍惜，越不能完全安心；越不能安心，反而越想靠近。


“检查门锁”的强迫性动作和安居失败消失，剩下抽象的珍惜／不安／靠近循环。该 unit 覆盖35–61，须保留范围边界意识。


`SRC-gpt56w-int-3-U07`；[D:/musicclaude/_bead_auto_20261016/research_fill/outputs/A-int__A_int_v1__gpt56w__op60__f2.md](D:/musicclaude/_bead_auto_20261016/research_fill/outputs/A-int__A_int_v1__gpt56w__op60__f2.md:139)

> 像深夜里一个人已经决定睡觉，却发现脑子开始重新播放白天的一段谈话。你并没有新的事实可想，却不停从另一个角度重新想它。


旧读者正文：[D:/musicclaude/_bead_quality_20261017/baseline_package/beads/STEP4_S07.md](D:/musicclaude/_bead_quality_20261017/baseline_package/beads/STEP4_S07.md:137)

> 一个念头说过了，还是觉得不够；似乎安慰了自己，过一会儿又重新想起。


深夜回放谈话、没有新事实仍反刍，是比泛称念头反复更准确的心理过程。旧珠子有相关概念，但削弱了它可辨认的处境。


`SRC-gpt56w-web-2-U06`；[D:/musicclaude/_bead_auto_20261016/research_fill/outputs/A-web__A_web_v2__gpt56w__op60__f1.md](D:/musicclaude/_bead_auto_20261016/research_fill/outputs/A-web__A_web_v2__gpt56w__op60__f1.md:55)

> **原来是在想着某个人、某件事；现在却开始沉迷于“自己正在感觉”这件事。**


旧读者正文：[D:/musicclaude/_bead_quality_20261017/baseline_package/beads/STEP4_S07.md](D:/musicclaude/_bead_quality_20261017/baseline_package/beads/STEP4_S07.md:117)

> 美好本身开始发烫。


源里有“感受对象→沉迷感受本身”的层次变化；旧文主要变成温度、浓度、热烈程度的增加。这是 S07 最有价值的被泛化维度之一。



反例也必须记录：S02 的“对方偶尔望你一眼，你心里就已经很满足”直接存在于 `SRC-gpt6w-int-3-U03`；gflash-int-3 U05 的潮湿、倦意、微醺、皮肤触感在旧正文仍有保留。S07 的“语言暂时跟不上感受”明显保留了 `SRC-gpt56w-int-2-U06` 的表达；`SRC-gpt6w-int-2-U05` 的“无法彻底进入对方内心／无法让此刻永远停住”也被近原文保留。因此问题不是一律禁止沿用原句，而是一些鲜明动作、悖论和感受机制被统一成泛泛的“太珍惜，所以害怕”。

S07 的“竞争解释”还混有定位误差：gflash-int-3 U07 把自己标作40–61并写“mm.51开始…dolce sfogato”；Muse-int-3 U04 则把该标记放在45附近，原件前言又假设138小节。这里仅指出它们与其他源的分段定位不一致，不在本审计重做外部事实核查。这样的差异不能直接升级为同一正确乐段的平等审美竞争；应先交给定位核查。旧 S07 已主动拒用其中部分 WIDE，不能反过来指控它引用了没看到的那份正文。

另一个来源性问题：`SRC-gflash-int-1-U11` 原句“我的身体在衰竭，但我的心依然能跳得如此滚烫。”是模型给出的拟人化独白，并非肖邦真实引语。旧 S07 把它列为不进入正文的内容，这一限制是恰当的；不能为保留文采而删掉该来源性质说明。

## 8. 新 formal30 manifest / FULL 快照


本次按 [D:/musicclaude/_bead_quality_20261017/sources/SOURCE_MANIFEST.json](D:/musicclaude/_bead_quality_20261017/sources/SOURCE_MANIFEST.json) 审查，来源数 **30**，与审计正式 30 ID 集合一致：**True**。所有 manifest 哈希和归档副本与原件相等：**True**。不因目录中残留不被引用的排除文件判污染。


| 段 | 新 FULL 单元数 | 字节 | 缺正文 | 不合格/未知 UID | 缺继承标题 |
|---|---:|---:|---:|---:|---:|
| S02 | 50 | 44470 | 0 | 0 | 3 |
| S07 | 37 | 34130 | 0 | 0 | 1 |
| S13 | 45 | 46814 | 0 | 0 | 1 |


继承标题是独立字段；早期新 builder 只传 `u[text]`，会漏掉它们。本次以实际文件检查结果为准：缺标题清单逐项保存在 manifest 的 `live_formal30_validation.segment_checks`。不要把单元正文完整误写成“连标题也全量保留”。S13 此处只验文件传输与身份，不评价内容。


## 9. 独立旧提示词表达对照：V2A Gemini Flash（不进生产 Pool）


亲读 ledger `kept_and_exclude` 中 run16 的两份 A_orig_V2A 原件。它们没有 A36 UID，以下只用真实路径与原文件行号。选择依据是表达的可感性，不是对传记、谱面、术语位置或历史引语真实性的背书；不以旧提示词质量参照补足正式30，也不参与同版本三轮统计。


[D:/musicclaude/music_work_since_1008v3_20261009/runs/run16_baseline_anchor/outputs/A-orig__A_orig_V2A__gflash_web__op60__s1.md](D:/musicclaude/music_work_since_1008v3_20261009/runs/run16_baseline_anchor/outputs/A-orig__A_orig_V2A__gflash_web__op60__s1.md:29)；无 A36 UID。

> 左手那永不停止的摇晃，是水的物理属性，它不在乎人的喜怒哀乐；而右手的歌声却充满了人的脆弱、迟疑与渴望。

把不理会人的水流和人的脆弱放在两个并行声部上，张力来自可感到的不同力量；比笼统“甜蜜又忧伤”有结构。


[D:/musicclaude/music_work_since_1008v3_20261009/runs/run16_baseline_anchor/outputs/A-orig__A_orig_V2A__gflash_web__op60__s2.md](D:/musicclaude/music_work_since_1008v3_20261009/runs/run16_baseline_anchor/outputs/A-orig__A_orig_V2A__gflash_web__op60__s2.md:25)；无 A36 UID。

> 它既像两个深爱的人靠在一起低语，又像一个疲惫不堪的人在与自己的内心对话。

同一声音保留双人相伴和一个人自语两种方向，用具体动作表达解释差异。


[D:/musicclaude/music_work_since_1008v3_20261009/runs/run16_baseline_anchor/outputs/A-orig__A_orig_V2A__gflash_web__op60__s1.md](D:/musicclaude/music_work_since_1008v3_20261009/runs/run16_baseline_anchor/outputs/A-orig__A_orig_V2A__gflash_web__op60__s1.md:68)；无 A36 UID。

> 音乐结束了，你依然身处冰凉昏暗的房间里。

从音乐里的空间切回听者所处房间，感官和视角都很明确。只取文学表达参照，不把原件相邻的尾声小节说法带入正式材料。


## 10. 逐来源索引（正式 30 份）


完整原件/日志/提示路径、SHA、UID offsets 见 JSON。此表便于人工定位；替补与旧 Sol 分开，不暗中覆盖身份。


| SRC | 原件 | SHA前12 | unit数 | 关键备注 |
|---|---|---|---:|---|
| `SRC-gflash-int-1` | [A-int__A_int_v1__gflash__op60__s1.md](D:/musicclaude/music_work_since_1008v3_20261009/runs/run05_saturation/outputs/A-int__A_int_v1__gflash__op60__s1.md) | `0e685f46bc26` | 22 | 原文连续匹配；模型证据层级见JSON |
| `SRC-gflash-int-2` | [A-int__A_int_v1__gflash__op60__s2.md](D:/musicclaude/music_work_since_1008v3_20261009/runs/run05_saturation/outputs/A-int__A_int_v1__gflash__op60__s2.md) | `eafde7307dec` | 8 | 原文连续匹配；模型证据层级见JSON |
| `SRC-gflash-int-3` | [A-int__A_int_v1__gflash__op60__s3.md](D:/musicclaude/music_work_since_1008v3_20261009/runs/run05_saturation/outputs/A-int__A_int_v1__gflash__op60__s3.md) | `7dfa9128b167` | 7 | 原文连续匹配；模型证据层级见JSON |
| `SRC-muse-int-1` | [A-int__A_int_v1__muse__op60__s1.md](D:/musicclaude/music_work_since_1008v3_20261009/runs/run08_final_models/outputs/A-int__A_int_v1__muse__op60__s1.md) | `cd539e72d63d` | 9 | 原文连续匹配；模型证据层级见JSON |
| `SRC-muse-int-2` | [A-int__A_int_v1__muse__op60__s2.md](D:/musicclaude/music_work_since_1008v3_20261009/runs/run08_final_models/outputs/A-int__A_int_v1__muse__op60__s2.md) | `3f9685b9285e` | 11 | 原件假设138小节，位置需复核 |
| `SRC-muse-int-3` | [A-int__A_int_v1__muse__op60__s3.md](D:/musicclaude/music_work_since_1008v3_20261009/runs/run37_pool_novelty/outputs/A-int__A_int_v1__muse__op60__s3.md) | `2a8ad809cd68` | 9 | 原件假设138小节，位置需复核 |
| `SRC-luna-int-1` | [A-int__A_int_v1__luna_noweb__op60__s1.md](D:/musicclaude/music_work_since_1008v3_20261009/runs/run08_final_models/outputs/A-int__A_int_v1__luna_noweb__op60__s1.md) | `2b762cda34b0` | 7 | 原文连续匹配；模型证据层级见JSON |
| `SRC-luna-int-2` | [A-int__A_int_v1__luna_noweb__op60__s2.md](D:/musicclaude/music_work_since_1008v3_20261009/runs/run08_final_models/outputs/A-int__A_int_v1__luna_noweb__op60__s2.md) | `6beecfa90cc3` | 7 | 原文连续匹配；模型证据层级见JSON |
| `SRC-luna-int-3` | [A-int__A_int_v1__luna__op60__f1.md](D:/musicclaude/_bead_auto_20261016/research_fill/outputs/A-int__A_int_v1__luna__op60__f1.md) | `875b25efb585` | 10 | 实际联网；不可计为第三轮离线 |
| `SRC-gpt56w-int-2` | [A-int__A_int_v1__gpt56w__op60__f1.md](D:/musicclaude/_bead_auto_20261016/research_fill/outputs/A-int__A_int_v1__gpt56w__op60__f1.md) | `13f5739f52bb` | 21 | 原文连续匹配；模型证据层级见JSON |
| `SRC-gpt56w-int-3` | [A-int__A_int_v1__gpt56w__op60__f2.md](D:/musicclaude/_bead_auto_20261016/research_fill/outputs/A-int__A_int_v1__gpt56w__op60__f2.md) | `b889422b0809` | 13 | 原文连续匹配；模型证据层级见JSON |
| `SRC-gpt6w-int-1` | [A-int__A_int_v1__gpt6w__op60__f1.md](D:/musicclaude/_bead_auto_20261016/research_fill/outputs/A-int__A_int_v1__gpt6w__op60__f1.md) | `15113c9f8c95` | 12 | 原文连续匹配；模型证据层级见JSON |
| `SRC-gpt6w-int-2` | [A-int__A_int_v1__gpt6w__op60__f2.md](D:/musicclaude/_bead_auto_20261016/research_fill/outputs/A-int__A_int_v1__gpt6w__op60__f2.md) | `9f2c016528ef` | 10 | 原文连续匹配；模型证据层级见JSON |
| `SRC-gpt6w-int-3` | [A-int__A_int_v1__gpt6w__op60__f3.md](D:/musicclaude/_bead_auto_20261016/research_fill/outputs/A-int__A_int_v1__gpt6w__op60__f3.md) | `d565dc8d47a2` | 10 | 原文连续匹配；模型证据层级见JSON |
| `SRC-gflash-web-1` | [A-web__A_web_v2__gflash_web__op60__s1.md](D:/musicclaude/music_work_since_1008v3_20261009/runs/run08_final_models/outputs/A-web__A_web_v2__gflash_web__op60__s1.md) | `3348fb17f674` | 11 | 原文连续匹配；模型证据层级见JSON |
| `SRC-gflash-web-2` | [A-web__A_web_v2__gflash_web__op60__s2.md](D:/musicclaude/music_work_since_1008v3_20261009/runs/run08_final_models/outputs/A-web__A_web_v2__gflash_web__op60__s2.md) | `850ca028be19` | 8 | 原文连续匹配；模型证据层级见JSON |
| `SRC-gflash-web-3` | [A-web__A_web_v2__gflash_web__op60__s3.md](D:/musicclaude/music_work_since_1008v3_20261009/runs/run37_pool_novelty/outputs/A-web__A_web_v2__gflash_web__op60__s3.md) | `9498fa00ae16` | 8 | 原文连续匹配；模型证据层级见JSON |
| `SRC-muse-web-1` | [A-web__A_web_v2__muse_web__op60__s1.md](D:/musicclaude/music_work_since_1008v3_20261009/runs/run08_final_models/outputs/A-web__A_web_v2__muse_web__op60__s1.md) | `a925a2019f94` | 8 | 原文连续匹配；模型证据层级见JSON |
| `SRC-muse-web-2` | [A-web__A_web_v2__muse_web__op60__s2.md](D:/musicclaude/music_work_since_1008v3_20261009/runs/run08_final_models/outputs/A-web__A_web_v2__muse_web__op60__s2.md) | `c4e5d9e1c4f6` | 9 | 原文连续匹配；模型证据层级见JSON |
| `SRC-muse-web-3` | [A-web__A_web_v2__muse_web__op60__s3.md](D:/musicclaude/music_work_since_1008v3_20261009/runs/run37_pool_novelty/outputs/A-web__A_web_v2__muse_web__op60__s3.md) | `00f552333bd7` | 9 | 原文连续匹配；模型证据层级见JSON |
| `SRC-luna-web-1` | [A-web__A_web_v2__luna__op60__s1.md](D:/musicclaude/music_work_since_1008v3_20261009/runs/run05_saturation/outputs/A-web__A_web_v2__luna__op60__s1.md) | `572b6c477370` | 11 | 原文连续匹配；模型证据层级见JSON |
| `SRC-luna-web-2` | [A-web__A_web_v2__luna__op60__s2.md](D:/musicclaude/music_work_since_1008v3_20261009/runs/run05_saturation/outputs/A-web__A_web_v2__luna__op60__s2.md) | `0ceeec5ba5ea` | 12 | 原文连续匹配；模型证据层级见JSON |
| `SRC-luna-web-3` | [A-web__A_web_v2__luna__op60__s3.md](D:/musicclaude/music_work_since_1008v3_20261009/runs/run05_saturation/outputs/A-web__A_web_v2__luna__op60__s3.md) | `848ed054c23d` | 13 | 原文连续匹配；模型证据层级见JSON |
| `SRC-gpt56w-web-2` | [A-web__A_web_v2__gpt56w__op60__f1.md](D:/musicclaude/_bead_auto_20261016/research_fill/outputs/A-web__A_web_v2__gpt56w__op60__f1.md) | `ede4ea27125c` | 17 | 原文连续匹配；模型证据层级见JSON |
| `SRC-gpt56w-web-3` | [A-web__A_web_v2__gpt56w__op60__f2.md](D:/musicclaude/_bead_auto_20261016/research_fill/outputs/A-web__A_web_v2__gpt56w__op60__f2.md) | `791a2f45f4d2` | 11 | 原文连续匹配；模型证据层级见JSON |
| `SRC-gpt6w-web-1` | [A-web__A_web_v2__gpt6w__op60__f1.md](D:/musicclaude/_bead_auto_20261016/research_fill/outputs/A-web__A_web_v2__gpt6w__op60__f1.md) | `5bd46a3b77b7` | 22 | 原文连续匹配；模型证据层级见JSON |
| `SRC-gpt6w-web-2` | [A-web__A_web_v2__gpt6w__op60__f2.md](D:/musicclaude/_bead_auto_20261016/research_fill/outputs/A-web__A_web_v2__gpt6w__op60__f2.md) | `000d58faf54d` | 15 | 原文连续匹配；模型证据层级见JSON |
| `SRC-gpt6w-web-3` | [A-web__A_web_v2__gpt6w__op60__f3.md](D:/musicclaude/_bead_auto_20261016/research_fill/outputs/A-web__A_web_v2__gpt6w__op60__f3.md) | `0ebaf4cbfde3` | 19 | 原文连续匹配；模型证据层级见JSON |
| `SRC-gpt56w-int-r1` | [response.txt](D:/musicclaude/gpt2agent-safechain/runs/yi-cookie-repair-20261006/job-2ee58aaae2e043a7a531b3dd4047022d/response.txt) | `20ff2e27bd7b` | 12 | 历史真5.6补位，新UID |
| `SRC-gpt56w-web-r1` | [response.txt](D:/musicclaude/gpt2agent-safechain/runs/yi-cookie-repair-20261006/job-3da49a4b00a34e89b9cf83236bc36645/response.txt) | `d6c2de25e3e4` | 12 | 历史真5.6补位，新UID |


## 11. 本子任务实际改动文件

仅创建/维护本目录的 `SOURCE_POOL_AUDIT.md`、`SOURCE_POOL_MANIFEST.json`、`REPLACEMENT_CANDIDATES.json`、`REPLACEMENT_UNITS.json`、`audit_source_pool.py`。未改旧文件、未调用模型、未生成珠子、未改 production manifest/Pool。新 Pool 的集成属于主 agent 操作。



## 12. 最终审计限定与处置决定

用户阅读本报告后确认以下边界，本审计据此完成，不继续扩大搜索：

- **实验输入保留冻结。** 已运行的 pilot28 和正式模型比较使用各自冻结的输入；不把后来发现的继承标题补回旧输入，不回写旧实验。两份同 Pool 的 pilot28 对照仍按原条件报告，不事后改称 formal30。
- **上下文修复另立版本。** `title_inherited` 缺失是真实的上下文遗漏。主 agent 将另建 `production_context30` 修复版，保留原实验输入和哈希。本审计只证实原快照存在遗漏，未声称未来修复版已经建立、核验或用于已有实验。
- **Luna 条件如实纠正。** `SRC-luna-int-3` 请求模型为 `gpt-6-luna`，实际发生 web_search；保留为用户允许的质量材料，显式披露采样条件，不能作为第三份同条件离线证据。不为凑严格 int 再调用 A。
- **表达参照止于三个 V2A 原句。** 它们独立于生产 Pool，不补轮次、不进入既有输入。
- **本子任务到此结束。** 两份历史 Thinking 替补及其原文索引已交付；剩余模型返回后的主编辑由主 agent 负责。本子任务不生成珠子、不新增模型调用、不修改生产或实验输入。

