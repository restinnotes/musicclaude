# 肖邦《船歌》Op.60：结构来源核验与自动冻结

<badge color="success">结构基线选定成功</badge>

**本轮正式采用 C2：朝山奈津子／PTNA（2008）的十四段「セクション」结构表。**

这是本次 A-only Pool → Bead 流程的固定操作基线，而不是对七位作者曲式观点的优劣裁决。C2 的十四段具有直接可核查的机构原文，按整数小节完整、连续、不重叠地覆盖第 1–116 小节，因此满足自动选定条件。

<text color="secondary" weight="medium">SELECTED_SOURCE_ID = C2</text>

<text color="secondary" weight="medium">SELECTED_HIERARCHY = セクション</text>

<text color="secondary" weight="medium">READY_FOR_POOL = true</text>

## 1. 七来源核验对照

这里区分两种完整性：一是论文是否讨论整部作品，二是**是否提供同一层级、互不重叠、可直接运行的完整分段表**。只有后者才能直接充当 `frozen_segments`。

| 来源及精确出处 | 是否提供完整可执行划分 | 原文层级 | 边界可用性 |
|---|---|---|---|
| **S1 / C1** Rink 1988, p.197, Example 1 <Link url="https://people.bu.edu/dako/BUHF/Kopp%20BUHF%20Chopin%20talk%20and%20examples.pdf" title="转载原表"/> | **是，14段** | Formal Division | 整数小节，完整可用；已核对转载表及论文文本 |
| **S2 / C2** 朝山／PTNA 2008,「小節番号／セクション／調」<Link url="https://enc.piano.or.jp/musics/543" title="机构原文"/> | **是，14段** | セクション | 整数小节，完整可用；直接核对原网页 |
| **S3 / C3** Gerling 2014, pp.57–60, Figure 4 <Link url="https://periodicos.ufrn.br/artresearchjournal/article/download/5364/4425/0" title="期刊PDF"/> | 否；整体讨论完整，但分段重叠 | two outer sections / middle section；局部主题及调性支点 | 宏观区域可引用，不能直接冻结为互斥区间 |
| **S4** Damschroder 2015, 第10章 pp.233–252 <Link url="https://www.cambridge.org/core/books/abs/harmony-in-chopin/barcarollein-f-major-op-60/38F995F2DD28ABF6C3CB1B6233D0F147" title="出版社"/> | 否；章节讨论范围覆盖全曲，但有重叠 | 章节分节标题、A1/B/A2/C/A3/coda | 起点及章节范围可用，单独单元终点不足 |
| **S5** Kopp 2014, [17], [22]–[26] <Link url="https://www.mtosmt.org/issues/mto.14.20.4/mto.14.20.4.kopp.html" title="期刊原文"/> | 否；局部结构讨论 | Theme A、B(1)″、coda 等 | 指定位置可用，不构成独立全曲表 |
| **S6** Aziz 2015, §1.5 <Link url="https://mtosmt.org/issues/mto.15.21.4/mto.15.21.4.aziz.html" title="期刊原文"/> | 否；局部句法论证 | grand antecedent、consequent、S₁/S₂ | 两个句法范围明确，S₁/S₂ 无精确范围 |
| **S7** Chaffin、Gerling、Demos 2024, Table 1 <Link url="https://musiclab.media.uconn.edu/wp-content/uploads/sites/290/2024/11/Memory-and-Expression-11-18-24.pdf" title="作者稿件PDF"/> | 位置表覆盖全曲，未完成完整原页核验 | Formal Division | 拍位级范围可保留；原文查阅标志为 `false`，不宜直接转换成整数段 |

**版本与编号核验：** S1、S2、S5、S6、S7 未确认所有边界专属的乐谱版本；S3 说明学习时使用 1984 年华沙版，S4 提及 National Edition，但这不能证明七来源使用了完全相同的印次与拍位定义。本轮仅确认 C1、C2 在第 1–116 小节范围上的整数编号一致，不推定所有版本的拍位和小节内部衔接一致。

核验依据包括 Rink 原表的明确转载、PTNA 原始机构网页以及 Gerling、Kopp、Aziz 的期刊正文。<Cite refs={["turn862436view1","turn862436view0","turn862436view2","turn862436view3","turn862436view4"]}/>

## 2. 正式选定来源与完整冻结边界

<box gap={1}>
  <title size="lg">C2 — 朝山奈津子／PTNA</title>
  **精确出处：** 朝山奈津子，〈舟歌 嬰ヘ長調 Op.60〉，《ピティナ・ピアノ曲事典》，2008 年 7 月 1 日更新。「解説」中「各セクションは、次のように区分できる。」之后的「小節番号／セクション／調」表。

  <Link url="https://enc.piano.or.jp/musics/543" title="查看 PTNA 原始十四段结构表"/> <Cite ref="turn862436view0"/>
</box>

以下是冻结后的完整结构，全部标签保持作者日文原样；小节起止均包含端点。

| 段号 | 小节范围 | 原文标签 |
|---|---|---|
| 01 | 1–3 | 序奏 |
| 02 | 4–16 | 第1主題 |
| 03 | 17–23 | 間句 |
| 04 | 24–34 | 第1主題（確保） |
| 05 | 35–39 | 間句 |
| 06 | 40–50 | 第2主題前半 |
| 07 | 51–61 | 第2主題前半（確保） |
| 08 | 62–71 | 第2主題後半 |
| 09 | 72–77 | 間句 |
| 10 | 78–83 | 挿入句 |
| 11 | 84–92 | 第1主題（再現） |
| 12 | 93–102 | 第2主題後半（再現） |
| 13 | 103–110 | 第2主題前半（再現） |
| 14 | 111–116 | 終結句 |

<box gap={2}>
  <row align="center" justify="between">
    **连续性检查**
    <text color="success" weight="medium"><icon name="check-circle" inline/> 通过</text>
  </row>
  <box background="surface-secondary" padding={3} radius="lg" gap={2}>
    <row height="14px" gap="2px">
      {#each [3,13,7,11,5,11,11,10,6,6,9,10,8,6] as n,i}
        <box flex={n} background={i%2===0?"#64748b":"#a5b4c4"} radius="xs"/>
      {/each}
    </row>
    <row justify="between">
      <caption>m.1</caption>
      <caption>14 个连续区间 · 116 小节</caption>
      <caption>m.116</caption>
    </row>
  </box>
</box>

这张表是唯一进入本轮 `frozen_segments` 的结构。PTNA 正文虽然还讨论三部形式、「中間部」与「再現部」，但没有为其提供另一张带逐段起止小节的高层级表。因此不自行新增父层级，也不将十四段压缩为九段。

另须注意：PTNA 表格将 103–110 标记为「第2主題前半（再現）」，其后正文又将该区域描述为「ここはすでにコーダの領域」。本轮保存表格标签，不把这一解释差异改写成新边界。

## 3. 选取依据及自动决策记录

| 规则 | C2 核验结果 |
|---|---|
| 完整覆盖 | 从 1–3 开始，至 111–116 结束，覆盖全部116小节 |
| 边界明确 | 每行均有明确整数小节范围 |
| 同一层级 | 全部属于 PTNA 的「セクション」列 |
| 原始出处可查 | 已直接核对 PTNA 原始日文网页 |
| 编号一致 | 与 C1 的14段整数边界完全一致 |
| 无重复、无空缺 | 14段首尾连续 |
| 粒度适用 | 可作为完整段落的文献级单位，不必自行合并 |
| 优先条件 | 在 C1、C2 同样满足完整性时，采用公开机构完整结构表 |

**决策：C2 胜出是操作配置结果，不是学术权威排名。**

C1 也完全合格。如果 PTNA 原表无法核验，C1 足以成为替代基线。但本轮 PTNA 的原始十四行已经确认，因此无需回退，也无需借助 S3 的宏观描述创造另一套更少段数的边界。

十四个 `セクション` 不代表必须产生十四次视频切屏。分段边界、素材映射单位、最终视频切屏频率应分别记录，不能相互替代。

## 4. 未选中来源的完整结构对照与差异存档

### 4.1 C1 / Rink：原始十四段与 C2 的逐项比较

原始出处：John Rink, “The Barcarolle: Auskomponierung and Apotheosis,” *Chopin Studies*, 1988, p.197, Example 1, “Formal synopsis of the Barcarolle”。

核验载体：[Rink 论文文本](https://www.scribd.com/document/437975319/276733164-Chopin-Barcarolle-Analysis)；[Kopp 转载原表，第13页](https://people.bu.edu/dako/BUHF/Kopp%20BUHF%20Chopin%20talk%20and%20examples.pdf)。<Cite refs={["turn615337view1","turn862436view1"]}/>

| 小节 | C1：Formal Division 原文 | C2：セクション 原文 |
|---|---|---|
| 1–3 | Introduction | 序奏 |
| 4–16 | Theme A | 第1主題 |
| 17–23 | ‘Development’ | 間句 |
| 24–34 | Theme A′ | 第1主題（確保） |
| 35–39 | Transition | 間句 |
| 40–50 | Theme B(1) | 第2主題前半 |
| 51–61 | Theme B(1)′ | 第2主題前半（確保） |
| 62–71 | Theme B(2) | 第2主題後半 |
| 72–77 | Transition | 間句 |
| 78–83 | ‘Dolce sfogato’ | 挿入句 |
| 84–92 | Theme A′ | 第1主題（再現） |
| 93–102 | Theme B(2)′ | 第2主題後半（再現） |
| 103–110 | Coda (B(1)″) | 第2主題前半（再現） |
| 111–116 | Coda | 終結句 |

**边界差异：0处。** C1 与 C2 的13个内部段落起点完全相同，只有标签与分析解释存在差异。

值得保留的非单纯语言差异：

- **17–23：** C1 称 ‘Development’，C2 称「間句」。
- **35–39、72–77：** C1 均称 Transition，C2 均称「間句」。
- **78–83：** C1 用 ‘Dolce sfogato’ 的演奏表达标记命名；C2 使用「挿入句」。
- **103–110：** C1 在结构表中归入 Coda (B(1)″)，C2 表格保留「第2主題前半（再現）」，但 C2 正文也承认其已进入尾声领域。
- **111–116：** C1 称 Coda，C2 称「終結句」。

其余主題 A/B、前半／後半、確保／再現等术语可以作对应阅读，但不把两名作者的术语系统改写成一套统一名称。

### 4.2 C3 / Gerling：原始宏观与局部层级

原始出处：Cristina Capparelli Gerling, “F. Chopin’s Barcarolle op. 60: Learning Strategies,” *Art Research Journal* 1(2), 2014, pp.57–60，特别是 p.58 的调性区域、p.59 Figure 4、p.60 的整体段落描述。<Cite ref="turn862436view2"/>

**A. 整体调性区域，原始范围**

| 原文层级 / 标签 | 小节 |
|---|---|
| two outer sections（第一外围区域，F♯ major） | 4–39 |
| middle section（A） | 39–83 |
| two outer sections（后一外围区域，F♯ major） | 86–116 |

**B. 局部与复合范围**

| 原文标签 | 小节 |
|---|---|
| Introduction | 1–4 |
| theme A′ | 84–92 |
| dolce sfogato section | 78–83 |
| final apotheosis A + Coda | 84–116 |

**C. Figure 4 的调性支点（不是完整区间）**

| 原文调性标记 | 位置 |
|---|---|
| F♯ Major | m.4 |
| A Major | m.39 |
| F♯ Major | m.84 |

与 C2 的逐项边界差异如下。

| C3 原始位置 | 相对于 C2 | 处理决定 |
|---|---|---|
| Introduction 1–4 | C2 序奏结束于3；C3 包含第4小节 | 保留 `introduction_end: 3 vs 4` 冲突 |
| 外围区域 4–39 | 覆盖 C2 第02–05段 | 不将四段合并 |
| 中间区域自39开始 | m.39 落在 C2 第05段35–39内部；C2 下段始于40 | 标记 `cross-boundary` |
| middle section 39–83 | 涉及 C2 第05–10段 | 仅保留宏观区域映射 |
| 后一外围区域自86开始 | C2 再现段始于84；86落在84–92内部 | 标记 `cross-boundary` |
| theme A′ 84–92 | 与 C2 第11段数值相同 | 边界一致，标签不同 |
| dolce sfogato section 78–83 | 与 C2 第10段数值相同 | 边界一致，标签不同 |
| final apotheosis A + Coda 84–116 | 跨越 C2 第11–14段 | 仅作复合区域证据，不改变边界 |
| Figure 4 支点 m.84 | 与 C2 第11段起点相同 | 记录为调性支点，不新增切点 |

特别说明：C3 的第一外围区域与中间区域都包含 m.39，而其后一外围区域起于 m.86，Figure 4 却在 m.84 标出 F♯ Major。这里存在不同分析尺度的重叠及位置区别，不能将其擅自修正成互不重叠的三段式边界。

### 4.3 S4–S7：其余原始结构记录

这些资料进入审计档案，但不参与修改 C2 的冻结边界。

**S4 — Damschroder 2015，第10章**

原始章节标题与范围：

| 小节 | 原文标题 |
|---|---|
| 1–16 | The introduction and the A1 section |
| 17–34 | The B and A2 sections |
| 35–103 | The C and A3 sections |
| 103–116 | The coda |

正文中明确指出的各形式单元起点：

| 原文标签 | 起点 | 独立终点 |
|---|---|---|
| introduction | m.1 | 未注明 |
| A1 section | m.4 | 未注明 |
| B section | m.17 | 未注明 |
| A2 section | m.24 | 未注明 |
| C section | m.35 | 未注明 |
| A3 section | m.84 | 未注明 |
| coda | m.103 | 章节范围至116 |

出处为 *Harmony in Chopin*, pp.233–252。出版社确认书目，公开文本转载提供章节标题，但本轮无法从出版社页面直接核对完整付费章节原页。<Cite refs={["turn862436view6","turn723911search0"]}/>

需保留的分歧是 **coda 始于103**；且 35–103 与 103–116 的章节标题范围在 m.103 重叠。它不是一份可以原样转为互斥区间的曲式表。

**S5 — Kopp 2014，[17]、[22]–[26]**

| 原文标签 / 陈述 | 明确位置 |
|---|---|
| Theme A（return） | 起于24 |
| dolce sfogato section | 起于78 |
| themes A（return） | 起于84 |
| theme B(2)（return） | 起于93 |
| theme B(1)″；主要结构的延续，而非 coda material | 103–110 |
| coda / second coda | 起于111，独立终点未注明 |

原文：[Music Theory Online, 20(4)](https://www.mtosmt.org/issues/mto.14.20.4/mto.14.20.4.kopp.html)。<Cite ref="turn862436view3"/>

Kopp 支持将 103–110 理解为主要结构的延续，并引用 Samson 将111作为 coda 起点的观点。这里必须区分 **Kopp 的正文判断**与他在文章中转载的 **Rink 原始表**，不能把后者另算作一份 Kopp 独立结构表。

**S6 — Aziz 2015，§1.5**

| 原文层级 | 原文标签 | 小节 |
|---|---|---|
| 句法功能 | grand antecedent | 4–15 |
| 句法功能 | consequent | 24–34 |
| 奏鸣曲理论主题代号 | S₁ | 未提供 |
| 奏鸣曲理论主题代号 | S₂ | 未提供 |

原文：[Music Theory Online, 21(4), §1.5](https://mtosmt.org/issues/mto.15.21.4/mto.15.21.4.aziz.html)。<Cite ref="turn862436view4"/>

Aziz 将 4–15 视为 grand antecedent，C2 第1主題则为4–16。二者属于不同分析粒度。不得将 Aziz 的 S₁、S₂ 擅自配上 C2 的小节范围。

**S7 — Chaffin、Gerling、Demos 2024，Table 1**

以下是所附 S7 索引转录的完整十四行，保留原始 `小节.拍位` 位置和名称，不取整、不修复：

| 原始 Bars | 原文 Formal Division |
|---|---|
| 1.1–3.4 | Introduction |
| 4.1–16.1 | Theme A |
| 16.2–24.2 | Continuation (b) |
| 24.3–35.1 | Theme A´ |
| 35.2–38.4 | Transition |
| 39.1–51.1 | Theme B |
| 51.1–61.1 | Theme B´ |
| 61.2–70.4 | Theme C |
| 71.0–78.1 | Transition |
| 78.2–84.1 | Dolce sfogato |
| 84.2–93.1 | Theme A´´ |
| 93.2–101.4 | Theme C´ |
| 102.1–111.1 | Coda B´´ |
| 111.1–116.4 | Coda |

出处：*Musicae Scientiae*, 28(4), Table 1, “Barcarolle Op. 60 Formal Structure and Harmonic Plan”。[期刊正式页面](https://journals.sagepub.com/doi/10.1177/10298649241241405)；[2024年11月作者稿件](https://musiclab.media.uconn.edu/wp-content/uploads/sites/290/2024/11/Memory-and-Expression-11-18-24.pdf)。搜索索引与较早公开稿支持所附转录，但未能直接查阅指定11月PDF原页。<Cite refs={["turn615337search0","turn723911search23","turn723911search21"]}/>

`accessed_original = false`。

保留以下待复核点：`71.0` 的特殊写法、相邻两行重复的 `51.1` 与 `111.1`，以及稿件版本与期刊排印版的一致性。S7 在16、24、35、39、51、61、71、78、84、93、102、111附近提供的拍位级定位与 C2 的整小节划分不能直接视作同精度边界。

### 4.4 边界冲突审计结论

需要重点标记的分歧集中在：

- **m.4：** Gerling 的引子终点与 C2 不同。
- **m.39–40：** Gerling 的调性区域交界与 C2 的相邻段界线不同。
- **m.84–86：** Gerling 的调性支点、外围区域起点使用不同位置。
- **m.103、m.111：** 多位作者对于尾声起点及103–110的性质有不同表述。
- **拍位级位置：** S7 不能直接吸附到 C2 整数边界。

上述差异全部进入审计，不迁移到 `frozen_segments`，也不据此删除跨边界的 A 素材。

## 5. run102 九段：选定之后的差异报告

run102 只参与以下事后比较。没有任何一个 C2 小节边界是根据 run102 选择或修改的。

| run102 历史九段 | 与选定 C2 的关系 | 对应 C2 段号 |
|---|---|---|
| 1–3 | 完全一致 | 01 |
| 4–16 | 完全一致 | 02 |
| 17–34 | 合并了相邻两段 | 03 + 04 |
| 35–39 | 完全一致 | 05 |
| 40–61 | 合并了相邻两段 | 06 + 07 |
| 62–77 | 合并了相邻两段 | 08 + 09 |
| 78–83 | 完全一致 | 10 |
| 84–102 | 合并了相邻两段 | 11 + 12 |
| 103–116 | 合并了相邻两段 | 13 + 14 |

对照统计：

<grid columns={3} gap={2}>
  <grid-item>
    <box background="surface-secondary" radius="lg" padding={3} align="center" gap={1}>
      <title size="2xl" color="default" tabularNums>4</title>
      <caption>完全一致段</caption>
    </box>
  </grid-item>
  <grid-item>
    <box background="surface-secondary" radius="lg" padding={3} align="center" gap={1}>
      <title size="2xl" color="default" tabularNums>5</title>
      <caption>相邻两段合并</caption>
    </box>
  </grid-item>
  <grid-item>
    <box background="surface-secondary" radius="lg" padding={3} align="center" gap={1}>
      <title size="2xl" color="default" tabularNums>0</title>
      <caption>发生位移的边界</caption>
    </box>
  </grid-item>
</grid>

也就是说，run102 的九段恰好可以表示为 C2 十四段的五次相邻合并，消失的内部段界位于第23、50、71、92、110小节之后。

**这只是选后差异结果。** 本轮正式结构仍是 PTNA 的十四段，不反向将其压缩为九段。

## 6. `structure.json`：可直接消费的冻结配置

已生成并验证三个文件：

<box border radius="lg" padding={3} gap={3}>
  <row align="center" gap={3}>
    <icon name="file-json" size="lg" color="secondary"/>
    <box flex="1" gap={1}>
      **[structure.json](sandbox:/mnt/data/structure.json)**
      <caption>正式冻结结构，14段，READY 状态已设置</caption>
    </box>
    <icon name="check-circle" color="success"/>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={3}>
    <icon name="file-json" size="lg" color="secondary"/>
    <box flex="1" gap={1}>
      **[structure_audit.json](sandbox:/mnt/data/structure_audit.json)**
      <caption>七来源结构转录、差异、来源链接和 run102 对照档案</caption>
    </box>
    <icon name="check-circle" color="success"/>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={3}>
    <icon name="file-json" size="lg" color="secondary"/>
    <box flex="1" gap={1}>
      **[pool_bead_handoff.json](sandbox:/mnt/data/pool_bead_handoff.json)**
      <caption>STEP3 / STEP4 的14段结构锚点及跨边界映射规则</caption>
    </box>
    <icon name="check-circle" color="success"/>
  </row>
</box>

以下为 `structure.json` 完整内容，可直接复制：

<CodeBlock language="json" editable>
{
  "work": "Frédéric Chopin — Barcarolle in F-sharp major, Op. 60 (116 measures, single movement)",
  "selected_source_id": "C2",
  "selected_hierarchy": "セクション",
  "evidence": {
    "source_id": "S2",
    "author": "朝山奈津子",
    "title": "舟歌 嬰ヘ長調 Op.60",
    "publication": "ピティナ・ピアノ曲事典 (PTNA)",
    "updated": "2008-07-01",
    "precise_location": "解説 (2); 「各セクションは、次のように区分できる。」以下の「小節番号／セクション／調」表",
    "original_url": "https://enc.piano.or.jp/musics/543",
    "accessed_original": true,
    "score_edition": "unknown",
    "coverage": "measures 1–116, fourteen consecutive non-overlapping sections",
    "crosschecked_against": "S1 / John Rink (1988), p.197 Example 1, via Kopp PDF p.13",
    "note": "Original Japanese labels and exactly the published measure boundaries; no inferred parent hierarchy."
  },
  "unit": "measure (bar), 1-based, inclusive",
  "frozen_segments": [
    ["1-3", "序奏"],
    ["4-16", "第1主題"],
    ["17-23", "間句"],
    ["24-34", "第1主題（確保）"],
    ["35-39", "間句"],
    ["40-50", "第2主題前半"],
    ["51-61", "第2主題前半（確保）"],
    ["62-71", "第2主題後半"],
    ["72-77", "間句"],
    ["78-83", "挿入句"],
    ["84-92", "第1主題（再現）"],
    ["93-102", "第2主題後半（再現）"],
    ["103-110", "第2主題前半（再現）"],
    ["111-116", "終結句"]
  ],
  "ready_for_pool": true
}
</CodeBlock>

程序验证结果：14段、116小节、没有空缺或重叠，C1 与 C2 的全部整数小节边界一致。三个 JSON 文件均通过解析检查。

## 7. STEP3 → STEP4 执行交接

结构选择流程不再等待用户批准。

**STEP3 — A-only Pool：** 已建立14个固定结构槽位，使用 `C2-01` 至 `C2-14` 作为段落 ID。素材进入时，以所选边界建立映射；任何跨界素材保留原始记录，同时标注涉及的所有 C2 段号，不为适配分段而删除或强行拆改 A 素材。

**STEP4 — Bead：** 已准备14个对应的结构锚点，各自携带原文标签、小节范围与 PTNA 出处。Bead 的结构单位与最终视频切屏单位保持独立。

需要明确区分完成状态：本轮七份附件是 STEP1 的结构资料，没有包含实际 A-only 原始素材。因此已经完成结构冻结和 STEP3/STEP4 交接配置，但**不能声称已经生成基于真实 A 素材的语义 Bead**。交接文件中的14个 Bead 目前是来源可追溯的结构锚点，而不是虚构的内容成品。指定的外部模型分工也未在此会话中实际运行。

这不构成结构选择的 STOP 条件，更不需要重新选择 C1/C2/C3。

## 8. 本轮最终判定

**选中来源：** C2，朝山奈津子／PTNA（2008）

**选中层级：** セクション

**冻结粒度：** 14个原始结构段

**完整覆盖：** 1–116小节

**其他来源：** 保留原始边界和标签，分歧已存档

**run102：** 只完成事后对照，未参与选定

**后续执行：** 以 `structure.json` 为唯一固定结构骨架，继续 A-only Pool → Bead 流程。

**READY_FOR_POOL=true**
