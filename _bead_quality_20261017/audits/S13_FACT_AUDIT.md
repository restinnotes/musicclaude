# S13 原始音乐事实与表达审计

审计日期：2026-10-17。共同裁决版本：S13-v2（按最终来源身份审计修订）。适用于新 Pool 及各写作试验，不生成新 A 研究、不重写旧 beads。

**结论：S13 固定为 mm.103–110。新读者主线采用“强奏范围内继续维持张力，m.106 再推进，m.110 冲突未在本段内完成解决”。退潮体验不全部判错：明指 Rubinstein 1962 或收势传统时，可作为附条件的竞争解释；未指明演奏而声称谱面要求本段自然持续渐弱，则不成立。不同录音的过程不得混写成同一次演奏同时发生。**

## 1. 范围、证据及追溯

固定 PTNA 十四段不动：S13＝mm.103–110「第2主題前半（再現）」，S14 自 m.111 开始。边界来源：[朝山奈津子／PTNA](https://enc.piano.or.jp/musics/543)。分析者是否称这里为 coda，不决定移动本项目的边界。

已读旧 [STEP4_prompt_S13.txt](D:/musicclaude/_bead_auto_20261016/out/STEP4_inputs_v3/STEP4_prompt_S13.txt) 与 [STEP4_S13.md](D:/musicclaude/_bead_auto_20261016/step4_out/beads/STEP4_S13.md)，回查 [A36_units.json](D:/musicclaude/_bead_auto_20261016/out/A36_units.json)、[A36_LEDGER.json](D:/musicclaude/_bead_auto_20261016/out/A36_LEDGER.json) 所指原始 A 文件。排除 gpro、Grok、Opus 等禁用来源；未读取 T/H/History/Thread/WHY/Outer/E7。旧 prompt、旧珠子中出现的 gpro 只作为旧成品污染记录，不作事实或体验的采样依据。

S13 旧附件排除 gpro 后的 **46 个 UID、旧名义30份原始 A（含2份Sol，非生产30）** 均逐字命中原文件，文件 SHA256 与旧 ledger 一致。这只证明旧材料的逐字追溯，不证明身份合格或音乐事实正确。完整原文、原路径、行号和核对结果见 [A_source_verification.json](D:/musicclaude/_bead_quality_20261017/audits/evidence_S13/A_source_verification.json)。同一 Kopp 论点被多份 A 转述，仍只算同一证据链，不作多数票。

**生产身份纠正：`SRC-gpt56w-int-1`、`SRC-gpt56w-web-1` 实为 Sol，所有下属 UID 均已排除生产，本文中若出现只属旧成品诊断／风险追溯，绝不作新 Pool 体验或事实证据。**当前生产30以 [SOURCE_MANIFEST.json](D:/musicclaude/_bead_quality_20261017/sources/SOURCE_MANIFEST.json) 为准；同prompt真实5.6w替代源为 `SRC-gpt56w-int-r1`、`SRC-gpt56w-web-r1`，见 [REPLACEMENT_UNITS.json](D:/musicclaude/_bead_quality_20261017/audits/REPLACEMENT_UNITS.json)。本轮已对齐身份与排除规则，未将旧名义30的核对冒充对新生产30的逐条音乐审计，也未自动继承旧Sol的UID或体验。

## 2. 谱面定位：把“力度”“织体”“张力”“演法”拆开

本地 [op60_score.pdf](D:/musicclaude/op60_score.pdf) 共 13 个 PDF 页，印刷页码与 PDF 页序相同；首页署 ©2021 Eric Tran，含法／德／英来源异文注释。它是现代校订谱，不冒充肖邦手稿、初版或 Henle 版。已目读 p.12–13，并与本地 [kopp.html](D:/musicclaude/kopp.html) 的版本说明交叉核对。

| 位置 | 本地谱实际可见 | 裁决边界 |
|---|---|---|
| m.102 → m.103，p.12 第一系统 | 前一小节有 ff、局部渐弱与 ritenuto；m.103 为 **Tempo primo、f** | 相较前段，速度／音响表面可以回收；不能因此推定之后八小节连续卸力。m.102 本身不属于 S13。 |
| mm.103–105，p.12 | 左手反复回到低音 F♯、分解伴奏；右手为歌唱性双音／和弦线条；**m.104 末有局部渐弱楔形** | “下方不肯离开、上方回落”有可见基础；不是八小节完全无细节，也不是八小节皆为从高处消散的右手琶音。 |
| m.106，p.12 第三系统左 | **四组颤音及长渐强楔形** | “这里只写 sempre f、没有起伏”不成立；m.106 是可确指的再推进位置。 |
| mm.107–109，p.12 | m.107 **sempre f**；反复低音上有较密的半音变化与声部摩擦 | 持续压力有谱面基础；“第107小节开始存在性黑暗”仍是解释，不是表情记号。 |
| m.110，p.13 第一系统 | 起始重音 **(fz)**，快速花饰由低处升向高处，再下落；该小节未标 calando | 可写冲击／悬而未解，不能把单向“水滴下落”当作本段全部音型。括号重音带版本条件。 |
| m.111，p.13 第二系统 | **fz p、calando**；后续有 dim.，m.113 有 pp | 这些记号在 S14；不得回填成 S13 自 m.103 起的谱面规定。 |

**主音持续低音不是脚踏板不松。** p.12–13 可见多处 Ped. 与释放星号；“一直踩在主音上”只能作为固定低音的比喻，不能转成八小节不换延音踏板的指令。

Kopp 的直接短引文：“The trills and crescendo of measure 106 clearly intensify”（[24]，PDF p.8）。其注23列出初版异文：法版 m.103 f、m.106 渐强、m.107 sempre f；英德版把 sempre f 放在 m.103，同样有 m.106 渐强。故不能统一声称所有版本在 m.103 都印有同一记号。[Kopp 正文及注23](https://www.mtosmt.org/issues/mto.14.20.4/mto.14.20.4.kopp.html)；[PDF p.8、p.13](https://www.mtosmt.org/issues/mto.14.20.4/mto.14.20.4.kopp.pdf)。

m.110 起始增六度及 m.111 的解决，属于 Kopp 的和声／对位解释；可据此保留 m.110 冲突，却不能在本段宣告到达已经完成。m.110／111 的 sf、fp、fz 等落点和写法存在版本差别；本地谱与 Kopp 注27不应强行抄成同一记号系统。

## 3. 冲突落在原始 A 的哪里

### A. “m.103 起自然平息”：必须限定演法，不能作为无条件谱面事实

`SRC-gflash-int-1-U19` · [原始 A](D:/musicclaude/music_work_since_1008v3_20261009/runs/run05_saturation/outputs/A-int__A_int_v1__gflash__op60__s1.md:62)：

> 奔腾的音符如飞溅的浪花迅速退去，璀璨的光芒开始黯淡，热度退散。

`SRC-gflash-web-1-U08` · [原始 A](D:/musicclaude/music_work_since_1008v3_20261009/runs/run08_final_models/outputs/A-web__A_web_v2__gflash_web__op60__s1.md:61)：

> 狂暴的海浪骤然平息（m. 103）。音乐重新回到轻柔的摇晃，一连串如水滴般冰凉清澈的半音阶琶音从高处缓缓滑落（mm. 103–111）；

**裁决：拆分。** “热度退散／退潮”作为听者体验不能被谱面一票否定；但原句未注明录音，不能当作谱面自然持续渐弱的证明。后一引文还把 mm.103–109 的织体、m.110 的大幅花饰与 m.111 的收势合并，属于时间／音型概括失准。若新稿采用收势读法，必须显式标“在某些收势演法中”，不能声称原 A 已亲证某特定录音。

### B. “八小节全无起伏”：维护张力不需要删掉谱面细节

`SRC-muse-web-3-U08` · [原始 A](D:/musicclaude/music_work_since_1008v3_20261009/runs/run37_pool_novelty/outputs/A-web__A_web_v2__muse_web__op60__s3.md:71)：

> 他写了整整8小节钉在原地，谱上只写`sempre f`，一直强，没有以前那种细腻的起伏。

`SRC-muse-web-2-U08` · [原始 A](D:/musicclaude/music_work_since_1008v3_20261009/runs/run08_final_models/outputs/A-web__A_web_v2__muse_web__op60__s2.md:59)：

> 但谱上写的是`sempre f`，一直强，而且没有任何细腻的表情记号，跟全曲形成反差。

**裁决：保留强奏背景，撤回“只写／没有任何”的绝对化事实。** m.106 有明确渐强；本地版本还见 m.104 末局部渐弱。不能从“持续张力”推导每一拍音量都递增、不能呼吸或不能轻巧。

### C. “钉住／踩住”与“这里绝非尾声”：术语误读、分析立场混写

`SRC-muse-web-1-U08` · [原始 A](D:/musicclaude/music_work_since_1008v3_20261009/runs/run08_final_models/outputs/A-web__A_web_v2__muse_web__op60__s1.md:75)：

> mm.103有个大终止，很多人以为完了。但肖邦写了八小节 sempre f，一直踩在主音上不放，节奏一小节一重复，和声越来越密、越来越 chromatic。

`SRC-muse-web-3-U08` · [原始 A](D:/musicclaude/music_work_since_1008v3_20261009/runs/run37_pool_novelty/outputs/A-web__A_web_v2__muse_web__op60__s3.md:73)：

> 但研究者Samson和Kopp都提醒：这里不是尾声，是主体还在继续。是第二次高潮，一次对位的到达在mm.110-111。

**裁决：**反复的主音低音可以保留，踏板动作不能据此指定。“不是尾声”须标为分析选择；Kopp 注24同时指出 Samson 后来改变了早期分析，不能伪装为稳定共识。m.110–111 的完成点跨界；在 S13 只准使用 m.110 一侧。[Kopp [24]、注24–25](https://www.mtosmt.org/issues/mto.14.20.4/mto.14.20.4.kopp.html)。

### D. “玩心／原谅／看透”：保留体验之前先检验定位

`SRC-muse-int-1-U09` · [原始 A](D:/musicclaude/music_work_since_1008v3_20261009/runs/run08_final_models/outputs/A-int__A_int_v1__muse__op60__s1.md:41)：

> 尾声 mm.103-111 特别轻，像水花、碎光在跳。不是胜利，是玩心回来了。

`SRC-muse-int-2-U10` · [原始 A](D:/musicclaude/music_work_since_1008v3_20261009/runs/run08_final_models/outputs/A-int__A_int_v1__muse__op60__s2.md:52)：

> 轻，现在是落地的轻，是原谅。

`SRC-muse-int-3-U08` · [原始 A](D:/musicclaude/music_work_since_1008v3_20261009/runs/run37_pool_novelty/outputs/A-int__A_int_v1__muse__op60__s3.md:53)：

> 这里的温柔比开头深：开头是“我要好好珍惜”，这里是“我知道留不住，还是觉得美”。接受了一点，但不是和解，只是累了以后的诚实。

**裁决：**U09 的范围到 m.111，“特别轻”不得无条件分配给 mm.103–110；“玩心”可以附于明确的轻巧／收势演法，不能由“有 A 来源”升级成全段共同事实。Muse-int-2 原始全文另有“138小节、6/8”的基础错误（详见 S07 补充审计），其 U10 不能继续担任可靠定位证据。Muse-int-3 的比喻可作为可追溯主观体验，但来源范围为 mm.103–113，不能据此断言 S13 已完成原谅／和解，也不自动把这段话迁往 S14。

### E. 情感过载、苦笑、哀诉：可留，但属于哪一层必须说清

`SRC-gpt56w-int-2-U11` · [原始 A](D:/musicclaude/_bead_auto_20261016/research_fill/outputs/A-int__A_int_v1__gpt56w__op60__f1.md:279)：

> 所以 mm. 104–110 给我的精神状态更接近：
> 
> **彻底暴露。**

`SRC-muse-web-2-U08` · [原始 A](D:/musicclaude/music_work_since_1008v3_20261009/runs/run08_final_models/outputs/A-web__A_web_v2__muse_web__op60__s2.md:63)：

> 波兰学者Tomaszewski说得更狠：这里是“苦笑”，一下打碎了前面营造的无边轻盈，告诉你“事情可能根本不是那样”。

**裁决：**“彻底暴露”“幸福与疼痛并存”有本段内原始 A 锚点，可保留为体验；不据此宣布全曲唯一高潮或肖邦真实心理。直接谈 mm.103–110 的“苦笑”文献在本轮核到的是 **Maria Piotrowska**，英文短语为 “a grimace of irony”（USC 网页正文、注52前一段；网页无页码）。不可把 A 的 Tomaszewski 署名直接续用为这段话的直接出处；即便另有转引，也必须标二手链条。[Piotrowska 原文](https://polishmusic.usc.edu/research/publications/polish-music-journal/vol3no1/late-chopin-last-works/)。

Szklener 对 mm.103–111 的论述确实联系固定低音、半音内声部与下行叹息，p.92 用词为 “tyglem emocji, niezwykle silnym przeżyciem, lamentoso”。这是作者的情感解释，不是谱上的 lamentoso 指示。p.92–93／例10确实讨论手稿修改；作者也承认涂改不能全部精确读出，本轮未独立校勘原手稿。对应 A：`SRC-gpt6w-web-3-U16`、`SRC-gpt6w-web-2-U13`、`SRC-luna-web-1-U10`、`SRC-luna-web-3-U12`。[作者上传全文，pp.91–93](https://www.researchgate.net/publication/272665783_Chopin%27s_Barcarole_in_F_sharp_major_Op_60_A_Sentimental_Song_or_a_Romantic_Poem)；[DOI](https://doi.org/10.2478/v10075-008-0015-7)。

## 4. 演奏分歧：须保留的条件，不等于两种谱面事实

Kopp [24] 承认 Rubinstein 1962 的收势处理；[25]提出自己的持续能量方案，并提及 Larrocha 1995 接近这一效果；[28]明确限制为自己的演奏选择。**不能拿 Kopp 否定所有退潮体验，更不能把他写成唯一正确演法的裁判。**本轮核实的是其文献记述，未亲听这两份录音。[Kopp [24]–[25]、[28]，PDF pp.8–9](https://www.mtosmt.org/issues/mto.14.20.4/mto.14.20.4.kopp.html)。

新 Pool 的使用规则：

- **默认读者主线：**按谱面写持续张力与 m.106 的推进，容许局部呼吸、相较前段的音响回收；不把持续张力等同于单调渐强。
- **另列竞争演法：**“在 Rubinstein 1962 所代表的收势处理中，可以听成逐步退潮／释放。”必须显式带演奏条件，并注明录音事实来自 Kopp 的记述。
- **不得融合：**不能把“这一演奏已经退潮”与“另一演奏持续顶住”写成同一次聆听的连续心理事实。主观悲喜并存可以保留；不同录音的动态进程必须分开。
- 未指明录音的原始 A 仍保留原文；不能倒填一个演奏者名字，伪造其取样来源。只能在新 Pool 的裁决层限定它的可用性。

## 5. 旧珠子的具体问题与范围污染

旧 [S13 第9行](D:/musicclaude/_bead_auto_20261016/step4_out/beads/STEP4_S13.md:9) 写“**音乐表面出现了退潮的迹象，内部却仍有一种执拗、不肯让步、甚至继续增长的压力。**”；[第105行](D:/musicclaude/_bead_auto_20261016/step4_out/beads/STEP4_S13.md:105) 无演奏条件地展开“浪花退下去”及“玩心”。这些话未必构成不可能的听感，问题在于把不同 A／不同演法的条件省略，写成全段已确认的共同过程。新稿应先标明采用哪条演奏主线。

范围污染须逐条截断，不能靠 CROSS 标签自动放行：

| 污染类别 | 原 UID 例子 | 共同处理 |
|---|---|---|
| m.111 的 calando／p 与之后的消散前移 | `SRC-gflash-web-1-U08/U09`、`SRC-muse-int-1-U09`、`SRC-muse-int-2-U10` | 不作 S13 已发生的谱面收束；原文存档。 |
| mm.110–111 的到达被压成 m.110 已解决 | `SRC-muse-web-3-U08`、`SRC-luna-web-2-U11`、`SRC-gpt56w-web-2-U14` | 本段只到 m.110，解决留作边界备注。 |
| 只在 m.103 接触前段，却支持整段情感时间线 | `SRC-gpt56w-int-2-U10`、`SRC-gpt56w-int-3-U10`（均 mm.94–103） | 只可说明边界附近，不外推至 m.110；另有 mm.104–110 原 A 的体验须独立引用。 |
| 结尾和弦、上岸、最终承担一切 | `SRC-gpt56w-int-1-U10`、`SRC-gpt6w-int-1-U11`、`SRC-gpt6w-int-2-U09`、`SRC-gpt6w-int-3-U09` | 不借宽范围标题将终局结果提前放入 S13。 |
| 原先只有 WIDE 头行 | 例如 `SRC-gflash-int-3-U13` | 本次回原文仅用于诊断；不因审计看到了正文就自动扩增新 Pool 的许可。 |

## 6. 不能裁决、必须降级的部分

1. **m.107 精确的“发问般黑暗”及 Klein 署名。**对应 `SRC-gpt6w-web-1-U20`。本地 [klein.pdf](D:/musicclaude/klein.pdf) 实为单页“Enable JavaScript and cookies to continue”，没有论文正文；本轮未得到可核对原段／页码。可保留该 UID 的主观暗影体验，不能把精确起点或 Klein 权威背书当已证实。
2. **Parakilas 的“幻觉般怀旧”及 Ravel 的“强烈绝望”原文、确切页码和适用范围。**对应 `SRC-gpt56w-web-1-U13`、`SRC-gpt56w-web-2-U14`、`SRC-muse-web-2-U08`。未完成原版文本核对；不从转述或非权威镜像升级为事实。尚未核实不等于已经证伪。
3. **唯一正确演法、绝对音量、听众必有的幸福／痛苦、肖邦因疾病导致某次演奏变弱。**谱面和本文献不足裁决。1848 演奏记述本轮不扩作史实审计，也不能让整个 S13 的 f 自动失效。
4. **手稿每项修改、所有版本的局部力度归属。**只确认本地现代校订谱可见内容及已注明的文献说明；不将本地 m.104 渐弱武断宣布为所有初版相同。

## 7. 可插入 Pool 的短裁决与补充项

共用 [facts_S13.txt](D:/musicclaude/_bead_quality_20261017/facts_S13.txt)；补充定位审计见 [S07_DOLCE_SFOGATO_AUDIT.md](D:/musicclaude/_bead_quality_20261017/audits/S07_DOLCE_SFOGATO_AUDIT.md) 与 [facts_S07.txt](D:/musicclaude/_bead_quality_20261017/facts_S07.txt)。四份文件适用于同一批试验，不能各自挑选互相矛盾的事实层。原文及旧材料不改，错段意象不迁移。
