## STEP3·A｜批1/2：A-int 五件原文归段

**本批处理范围：A01–A05，仅 int 通道。**

已完成输入文件的字节数和 SHA-256 核验，五件均与 A_RAW_MANIFEST 完全一致。`structure.json` 也与给定 C2 十四段一致，未作任何结构修改。

| 核验项 | 结果 |
|---|---|
| A01–A05 原文 | 5/5 完整匹配 |
| C2 结构 | S01–S14，1–116 小节，冻结 |
| A06–A11 | 本批不处理 |
| 谱面、录音及其他研究层 | 不读取 |
| 归段依据 | 原始小节号、上下文语义、冻结段界 |
| 错配原则 | 保留原句和原始范围，不替来源校正 |

特别需要区分：**归入某段只代表原文可追溯地指向该段，不代表该研究的音乐判断已经核实。** 各模型互相矛盾的描述也不通过多数票决定真伪。

### 本批交付文件

<box gap={2}>
  <row align="center" gap={3}>
    <icon name="file-json" color="secondary" size="lg"/>
    <box flex="1" gap={1}>
      **[A_POOL_MAP_batch1.json](sandbox:/mnt/data/A_POOL_MAP_batch1.json)**

      <caption>完整机器版：17个 Pool、原文摘录、全部来源元数据、106条唯一语义单元及去向台账</caption>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={3}>
    <icon name="file-text" color="secondary" size="lg"/>
    <box flex="1" gap={1}>
      **[A_POOL_REVIEW_batch1.md](sandbox:/mnt/data/A_POOL_REVIEW_batch1.md)**

      <caption>中文复核版：S01–S14三级原文列表、UNRESOLVED处理理由、逐件逐条去向台账</caption>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={3}>
    <icon name="file-json" color="secondary" size="lg"/>
    <box flex="1" gap={1}>
      **[POOL_MAP_batch1_only.json](sandbox:/mnt/data/POOL_MAP_batch1_only.json)**

      <caption>纯POOL_MAP：仅17个指定键；每段条目直接携带原文、UID、模型、通道、原始范围、路径、SHA-256</caption>
    </box>
  </row>
  <divider color="subtle"/>
  <row align="center" gap={3}>
    <icon name="file-json" color="secondary" size="lg"/>
    <box flex="1" gap={1}>
      **[BATCH1_SELF_CONTAINED_COPYABLE.json](sandbox:/mnt/data/BATCH1_SELF_CONTAINED_COPYABLE.json)**

      <caption>便于人工复制、续接的规范化版本：SOURCES、UNITS、POOL_MAP通过唯一ID关联</caption>
    </box>
  </row>
</box>

## 1. S01–S14 归段结果

<text color="secondary" size="sm">下表计数为 Pool 内引用次数，并非独立研究事实数。每个来源语义单元使用固定的 Axx-Uxxx 标识；CROSS_SEGMENT 在相关段重复引用时不生成新单元。</text>

| 冻结段 | PRIMARY | CROSS_SEGMENT | UNCERTAIN |
|---|---:|---:|---:|
| S01 · 1–3 序奏 | 4 | 2 | 0 |
| S02 · 4–16 第1主題 | 7 | 7 | 0 |
| S03 · 17–23 間句 | 1 | 8 | 0 |
| S04 · 24–34 第1主題（確保） | 1 | 6 | 0 |
| S05 · 35–39 間句 | 0 | 8 | 2 |
| S06 · 40–50 第2主題前半 | 1 | 4 | 5 |
| S07 · 51–61 第2主題前半（確保） | 0 | 8 | 6 |
| S08 · 62–71 第2主題後半 | 0 | 8 | 4 |
| S09 · 72–77 間句 | 0 | 5 | 2 |
| S10 · 78–83 挿入句 | 3 | 3 | 3 |
| S11 · 84–92 第1主題（再現） | 5 | 5 | 1 |
| S12 · 93–102 第2主題後半（再現） | 4 | 7 | 3 |
| S13 · 103–110 第2主題前半（再現） | 3 | 6 | 3 |
| S14 · 111–116 終結句 | 5 | 2 | 6 |

**没有 PRIMARY 的段落保留为空。** 例如，S05、S07、S08、S09 虽然存在大量跨段描述，但本批没有足够依据把那些宽泛描述改写成只属于该段的独立研究判断。

下面是各段的代表性原句。全部条目，包括原始范围、模型、通道和来源行号，均保留在交付的 JSON 与 Markdown 中。

<box gap={3}>
  <box gap={1}>
    **S01 · 序奏**

    <text size="sm">PRIMARY · A03-U002 · muse/int · mm.1–3</text>

    > 低音先试探一下 C#，跳到 G#，高音又往下散开，最后 A# 一个人悬在那儿。

    <text size="sm">CROSS_SEGMENT · A01-U002 · gpt56w/int · mm.1–4，关联 S01/S02。</text>
  </box>
  <divider color="subtle"/>
  <box gap={1}>
    **S02 · 第1主題**

    <text size="sm">PRIMARY · A04-U005 · opus/int · mm.6–16</text>

    > 主旋律进来，大部分时候是两个声部并行，像两个人一起低声哼。

    <text size="sm">A01-U003/U004 以 mm.5–20 跨 S02/S03；A02-U004 等原文跨第16/17小节段界。</text>
  </box>
  <divider color="subtle"/>
  <box gap={1}>
    **S03 · 間句**

    <text size="sm">PRIMARY · A05-U007 · grok/int · mm.17–23</text>

    > 一句说完，心里会空出一点位置，风就从这里进来。

    <text size="sm">其余关联主要为 A01 的 mm.5–20、21–38，及 A02/A03 的 mm.16–23。</text>
  </box>
  <divider color="subtle"/>
  <box gap={1}>
    **S04 · 第1主題（確保）**

    <text size="sm">PRIMARY · A02-U006 · gflash/int · mm.24</text>

    > 当 mm. 24 主题再次回来时，织体变厚、颤音变多，这是一种“试图重新点燃热情”的心理补偿——想要用力抓住刚才的美好。

    <text size="sm">A02-U007、A03-U006 所述34–35小节断裂同时关联S05。</text>
  </box>
  <divider color="subtle"/>
  <box gap={1}>
    **S05 · 間句**

    <text size="sm">CROSS_SEGMENT · A03-U007 · muse/int · mm.35–40</text>

    > 伴奏脉搏没了，只剩一条单线，然后慢慢找回节拍，从升F大调转向A大调。

    <text size="sm">原始范围跨 S05/S06；把 m.39 直接称为第二主题起点的 A02-U008、A03-U008 没有硬塞进本段。</text>
  </box>
  <divider color="subtle"/>
  <box gap={1}>
    **S06 · 第2主題前半**

    <text size="sm">PRIMARY · A03-U009 · muse/int · mm.42</text>

    > mm.42 那种向上冲的快速音型，后面还来几次。

    <text size="sm">A05-U010/U011/U012 的“先是／中间某处／再往后”仅有40–71宽范围，保留为 UNCERTAIN。</text>
  </box>
  <divider color="subtle"/>
  <box gap={1}>
    **S07 · 第2主題前半（確保）**

    <text size="sm">CROSS_SEGMENT · A01-U009 · gpt56w/int · mm.57–77</text>

    > 接下来并不是简单地“走出阴影”。

    <text size="sm">该原文覆盖 S07/S08/S09，不能只凭阶段叙述认为情绪变化发生在第61或62小节。</text>
  </box>
  <divider color="subtle"/>
  <box gap={1}>
    **S08 · 第2主題後半**

    <text size="sm">CROSS_SEGMENT · A02-U011 · gflash/int · mm.61–70</text>

    > 内心的渴望在加速，像是不顾一切地摇桨往前赶，但到了第 70 小节，旋律停在半空——现实没有给他答案。

    <text size="sm">第61小节仍属于S07，因此保持跨段引用。</text>
  </box>
  <divider color="subtle"/>
  <box gap={1}>
    **S09 · 間句**

    <text size="sm">CROSS_SEGMENT · A03-U012 · muse/int · mm.71–77</text>

    > 希望感没了，变成慢慢下坠的担心。

    <text size="sm">原始范围包含第71小节（S08）；A05-U013 将72–83称为第一主题返回，归入 UNRESOLVED。</text>
  </box>
  <divider color="subtle"/>
  <box gap={1}>
    **S10 · 挿入句**

    <text size="sm">PRIMARY · A03-U013 · muse/int · mm.78–83</text>

    > 时间感松了，人是软的、半透明的，既安慰又有点凄凉：美，但抓不住。

    <text size="sm">A01-U011/U012 的 mm.78–85 必须跨 S10/S11，不能把第84–85小节提前纳入挿入句。</text>
  </box>
  <divider color="subtle"/>
  <box gap={1}>
    **S11 · 第1主題（再現）**

    <text size="sm">PRIMARY · A03-U014 · muse/int · mm.84–92</text>

    > 温柔变成了意志，里面有不服输，也有怕再飘走所以抓紧的紧张。

    <text size="sm">A05-U015 将84–93视为全曲音量顶点，因涉及跨界及模型分歧而列 UNCERTAIN。</text>
  </box>
  <divider color="subtle"/>
  <box gap={1}>
    **S12 · 第2主題後半（再現）**

    <text size="sm">PRIMARY · A02-U017 · gflash/int · mm.93–102</text>

    > 到了 mm. 93–102，情绪已经不是简单的激昂，而是一场**心理雪崩**。

    <text size="sm">A05-U017 却将93–102描述为“浪头过去以后的发抖”，两种解读并存而不合并。</text>
  </box>
  <divider color="subtle"/>
  <box gap={1}>
    **S13 · 第2主題前半（再現）**

    <text size="sm">PRIMARY · A03-U017 · muse/int · mm.103–110</text>

    > 心理上是死撑住一个中心，周围越乱，越不松手。

    <text size="sm">A01-U019、A04-U018 则从105或103小节开始描述高潮后的收束，归属为 UNCERTAIN。</text>
  </box>
  <divider color="subtle"/>
  <box gap={1}>
    **S14 · 終結句**

    <text size="sm">PRIMARY · A04-U019 · opus/int · mm.115–116</text>

    > 然后是最后两小节的**强奏八度**，干脆、坚定地收住。

    <text size="sm">A05-U019 的“最后一个和弦很轻”与其明显冲突，保留在 UNCERTAIN，未作胜负裁定。</text>
  </box>
</box>

## 2. UNRESOLVED / OUT_OF_RANGE / LONG_RANGE

<box gap={3}>
  <grid columns={3} gap={2}>
    <grid-item>
      <box border radius="lg" padding={3} gap={1}>
        <text color="secondary" weight="medium" size="xs">UNRESOLVED</text>
        <title size="xl" color="default" tabularNums>8</title>
      </box>
    </grid-item>
    <grid-item>
      <box border radius="lg" padding={3} gap={1}>
        <text color="secondary" weight="medium" size="xs">OUT_OF_RANGE</text>
        <title size="xl" color="default" tabularNums>0</title>
      </box>
    </grid-item>
    <grid-item>
      <box border radius="lg" padding={3} gap={1}>
        <text color="secondary" weight="medium" size="xs">LONG_RANGE</text>
        <title size="xl" color="default" tabularNums>12</title>
      </box>
    </grid-item>
  </grid>
</box>

### UNRESOLVED 八条

| 单元 | 原始范围 | 处理理由 |
|---|---|---|
| A02-U008 | 35–61，句内m.39 | 把m.39称为新主题起点；C2中m.39仍属S05 |
| A03-U008 | 39–61 | 新主题在39起展开的语义无法与C2严格对应 |
| A04-U006 | 17–34 | 把17–34整体说成主题再出现；17–23是间句 |
| A04-U008 | 35–71 | 把整段起点说成新调及新速度，未能明确区别35–39间句 |
| A04-U009 | 约m.35起 | 新主题性质提前到C2间句，无法自行移至m.40 |
| A05-U008 | 24–39 | 声称“另一条更好开口的旋律出现了”，无法与S04确保/S05间句确切吻合 |
| A05-U013 | 72–83 | 声称“最初那条旋律回来了”，而C2第1主题再现始于84 |
| A05-U018 | 103–116 | 声称“第一条旋律最后一次回来”，与S13第2主题前半再现、S14终结句不合 |

这些是**来源文本与冻结结构的归属冲突**，不是未经核谱就宣布原作者的全部声音观察为假。无法拆分而保全其含义的句子完整留在未决区。

**OUT_OF_RANGE：空列表。** 五件文本未发现超出1–116小节的作品定位编号。

**LONG_RANGE：** A01-U001、U015、U021；A02-U001；A03-U001；A04-U001、U002、U021、U022；A05-U001、U002、U020。这里收纳全曲总论、后见性的心理曲线、可能带有未经证实传记推测的解释，以及对前文的总结重述。不再把它们下沉到局部 Pool 当作独立的即时 Affect。

## 3. 去向台账

106条唯一单元按来源分布如下：

| 来源 | 模型 / 通道 | 唯一单元 | PRIMARY | CROSS | UNCERTAIN | UNRESOLVED | LONG_RANGE |
|---|---|---:|---:|---:|---:|---:|---:|
| A01 | gpt56w / int | 21 | 2 | 13 | 2 | 0 | 3 |
| A02 | gflash / int | 24 | 8 | 6 | 5 | 1 | 1 |
| A03 | muse / int | 19 | 8 | 8 | 1 | 1 | 1 |
| A04 | opus / int | 22 | 8 | 3 | 3 | 3 | 5 |
| A05 | grok / int | 20 | 5 | 5 | 6 | 3 | 3 |

<text color="secondary" size="xs">注意：以上逐来源分类分布以源单元分类为口径；完整逐行台账请以交付JSON的 DESTINATION_LEDGER 为准，而非把各段重复引用加总。</text>

每件原文的每条 `Axx-Uxxx` 在 [A_POOL_REVIEW_batch1.md](sandbox:/mnt/data/A_POOL_REVIEW_batch1.md) 中都有明确的来源行、原始范围、分类和目标段；[A_POOL_MAP_batch1.json](sandbox:/mnt/data/A_POOL_MAP_batch1.json) 的 `DESTINATION_LEDGER` 则是对应机器版。跨段同一 `unit_id` 不增算研究数量。

## 4. 可直接复制的本批 POOL_MAP JSON

这里使用引用式 JSON：`POOL_MAP` 恰好包含指定的17个键，所有列表中的 ID 均指向同批 `UNIT_REGISTRY` 原句，来源 UID 再对应 `SOURCE_REGISTRY` 的模型、通道、路径及哈希。这样可以避免在多个 Pool 内复制原句造成事实身份丢失。**需要每个条目直接内嵌完整原句与来源元数据时，使用上方 `POOL_MAP_batch1_only.json`，它已完整生成。**

<CodeBlock language="json" editable>
{
  "S01": {
    "PRIMARY": ["A02-U002","A03-U002","A04-U003","A05-U004"],
    "CROSS_SEGMENT": ["A01-U002","A05-U003"],
    "UNCERTAIN": []
  },
  "S02": {
    "PRIMARY": ["A02-U003","A03-U003","A03-U004","A04-U004","A04-U005","A05-U005","A05-U006"],
    "CROSS_SEGMENT": ["A01-U002","A01-U003","A01-U004","A02-U004","A02-U005","A03-U005","A05-U003"],
    "UNCERTAIN": []
  },
  "S03": {
    "PRIMARY": ["A05-U007"],
    "CROSS_SEGMENT": ["A01-U003","A01-U004","A01-U005","A01-U006","A02-U004","A02-U005","A03-U005","A04-U007"],
    "UNCERTAIN": []
  },
  "S04": {
    "PRIMARY": ["A02-U006"],
    "CROSS_SEGMENT": ["A01-U005","A01-U006","A02-U004","A02-U007","A03-U006","A04-U007"],
    "UNCERTAIN": []
  },
  "S05": {
    "PRIMARY": [],
    "CROSS_SEGMENT": ["A01-U005","A01-U006","A01-U007","A01-U008","A02-U004","A02-U007","A03-U006","A03-U007"],
    "UNCERTAIN": ["A02-U009","A03-U010"]
  },
  "S06": {
    "PRIMARY": ["A03-U009"],
    "CROSS_SEGMENT": ["A01-U007","A01-U008","A03-U007","A05-U009"],
    "UNCERTAIN": ["A02-U009","A03-U010","A05-U010","A05-U011","A05-U012"]
  },
  "S07": {
    "PRIMARY": [],
    "CROSS_SEGMENT": ["A01-U007","A01-U008","A01-U009","A01-U010","A02-U011","A03-U011","A04-U010","A05-U009"],
    "UNCERTAIN": ["A02-U009","A02-U010","A03-U010","A05-U010","A05-U011","A05-U012"]
  },
  "S08": {
    "PRIMARY": [],
    "CROSS_SEGMENT": ["A01-U009","A01-U010","A02-U011","A02-U012","A03-U011","A03-U012","A04-U010","A05-U009"],
    "UNCERTAIN": ["A02-U010","A05-U010","A05-U011","A05-U012"]
  },
  "S09": {
    "PRIMARY": [],
    "CROSS_SEGMENT": ["A01-U009","A01-U010","A02-U012","A03-U012","A04-U011"],
    "UNCERTAIN": ["A02-U010","A05-U014"]
  },
  "S10": {
    "PRIMARY": ["A02-U013","A03-U013","A04-U012"],
    "CROSS_SEGMENT": ["A01-U011","A01-U012","A04-U011"],
    "UNCERTAIN": ["A02-U010","A04-U013","A05-U014"]
  },
  "S11": {
    "PRIMARY": ["A01-U013","A01-U014","A02-U016","A03-U014","A04-U014"],
    "CROSS_SEGMENT": ["A01-U011","A01-U012","A02-U014","A02-U015","A05-U016"],
    "UNCERTAIN": ["A05-U015"]
  },
  "S12": {
    "PRIMARY": ["A02-U017","A03-U016","A04-U015","A04-U017"],
    "CROSS_SEGMENT": ["A01-U016","A01-U017","A01-U018","A02-U014","A02-U015","A03-U015","A05-U016"],
    "UNCERTAIN": ["A04-U016","A05-U015","A05-U017"]
  },
  "S13": {
    "PRIMARY": ["A02-U018","A02-U021","A03-U017"],
    "CROSS_SEGMENT": ["A01-U016","A01-U017","A01-U018","A02-U019","A03-U015","A03-U018"],
    "UNCERTAIN": ["A01-U019","A02-U022","A04-U018"]
  },
  "S14": {
    "PRIMARY": ["A02-U020","A02-U023","A03-U019","A04-U019","A04-U020"],
    "CROSS_SEGMENT": ["A02-U019","A03-U018"],
    "UNCERTAIN": ["A01-U019","A01-U020","A02-U022","A02-U024","A04-U018","A05-U019"]
  },
  "UNRESOLVED": [
    "A02-U008","A03-U008","A04-U006","A04-U008",
    "A04-U009","A05-U008","A05-U013","A05-U018"
  ],
  "OUT_OF_RANGE": [],
  "LONG_RANGE": [
    "A01-U001","A01-U015","A01-U021","A02-U001",
    "A03-U001","A04-U001","A04-U002","A04-U021",
    "A04-U022","A05-U001","A05-U002","A05-U020"
  ]
}
</CodeBlock>

## 5. 待续说明

本批 A01–A05 的原文归段、去向台账、错配登记及机器文件已经生成。**A06–A10（web五件）与 A11（orig一件）尚未覆盖。**

下一批合并时应先复核本批8条 UNRESOLVED、跨段边界及相互矛盾的高潮与终结句表述；再接入A06–A11，保留当前稳定 `unit_id` 和冻结C2结构，形成11件完整合并版 `A_POOL_MAP.json` 与中文 `A_POOL_REVIEW.md`。本批没有提前对缺失六件做归属推断。
