# 小节分段：上游机制与机器可读格式

P0 里的 `1, 4, 17, …, 117` 不是手填参数，而是上游产物。本目录把它做成一个独立阶段，输出统一的
`works/<作品>/segmentation.json`；Thread 提示词里的分段句、评审提示词里的区间、音乐核查的总小节数都从这个文件渲染，不再手写任何小节号。

## 产出方式（seg.py）

| 命令 | 做什么 | 现状 |
|---|---|---|
| `python seg.py import-op60` | 把 bead 链路已冻结的结构（`bead_chain/inputs/structure.json`，PTNA/朝山 14 段，并与 Rink 1988 交叉核对）转成统一格式 | Op.60 正式使用这一份，因为 Bead 也按它分段 |
| `python seg.py research <work>` | 一次 GPT-6 Max（gpt3，联网）调用：逐来源提取**已发表**结构表（作者/页码/原文标签/层级），再按规则自动选定一套操作分段；脚本校验 | Op.60 复现、Op.61 新建 |

自动选定规则（`prompts/seg_published_v1.txt`）：完整覆盖第1小节到最后一小节、连续不重叠、整数小节、出处可核实、层级是“完整的自然音乐段落”（不是三四个大部，也不是逐个乐句）；不拼接多个来源；只有在找不到任何可用来源时才停。

脚本校验（`seg.validate` + `research`）：起点为 1、相邻段首尾相接、终点等于总小节数；所选分段必须**逐字来自同一个来源**（允许同一来源在各大部下分别列出的小段按顺序相接）；其余合格来源记入 `alternatives`。

## 验证

- **Op.60 复现**：`research op60` 独立检索到 PTNA（朝山奈津子）与 Kopp 2014 / Rink 1988 两套表，边界与 bead 链路冻结的 14 段完全一致（`works/op60_auto/segmentation.json`、`runs/seg_op60_v1/validation.json`）。
- **Op.61 新建**：选定 PTNA（塚田花恵 2010）三部内 13 段：1–23 序奏 / 24–65 A / 66–91 エピソード / 92–115 A / 116–147 B1 / 148–180 C / 181–205 B2 / 206–213 C / 214–215 序奏 / 216–225 B2 / 226–241 推移 / 242–253 A / 254–288 C。已用保存的 PTNA 原页面逐字核对。Rink 1993、Spicer 1994、Kremlev 的差异记在 `disagreements`（66/268 共用边界、92 vs 94、181 归属等）。
- 第一版校验过严（把 PTNA 三部分开列出的小段判为“非同一层级”），已改为允许同一来源各部小段顺序相接。

## 格式（schema）

```json
{
 "work": "Frédéric Chopin, Barcarolle in F-sharp major, Op. 60",
 "short_name": "肖邦船歌",
 "total_measures": 116,
 "boundaries": [1, 4, 17, 24, 35, 40, 51, 62, 72, 78, 84, 93, 103, 111, 117],
 "segments": [{"id": "S01", "start": 1, "end": 3, "label": "序奏"}, "..."],
 "source": {"author_or_institution": "...", "url": "...", "locator": "...", "level": "...", "disagreements": []},
 "method": "...",
 "alternatives": [{"source_id": "S2", "who": "...", "level": "...", "boundaries": []}]
}
```

`boundaries` 采用左闭右开：最后一个数是全曲结束后的边界，不是小节。Bead 的 `S01…S14` 与 `segments[].id` 一一对应，所以 Bead 材料、Thread 段落和视频时间轴都可以按 id 对齐。

## 分段句怎么写进提示词（实验结论）

`seg.clause(d, style)` 有三种渲染：

| style | 文本 | 结果 |
|---|---|---|
| `orig` | `按照小节数1, 4, …, 117 来分段`（与用户原 P0 逐字相同） | 基线；6 篇 D0 中有 2 篇把 117 当成一个小节另写一段（B0 也犯过） |
| `ranges` | `按照以下14个小节区间分段（全曲共116小节）：第1–3小节、…` | 117 误读归零，但 J2、J3 共 6 篇在三位评委下都明显更差（更像逐格填表） |
| `note` | `orig` + `（最后一个数117只是全曲结束的边界，不是一个小节；全曲共116小节）` | 117 误读归零，质量与 `orig` 持平（J3） → **采用** |

## 和“按 Thread 分段”的关系

记忆中用户 10-15 选择过“大段由 Thread/Center 决定、音乐纹理只校验边界”。本轮的分段仍沿用已发表结构（与现有 Bead 对齐），没有让 Thread 反过来改切点。如果以后要做 Thread 驱动的分段，可以在同一 schema 下加一个 `method: "thread_proposed"` 的生产者，`alternatives` 里保留文献分段作校验，下游消费方式不变。
