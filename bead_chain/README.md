# Op.60 A Pool → Bead / STRUCT 可复用链路

所有内容生成与审稿都通过本机 `gpt3`（GPT Web，GPT-6 Thinking / max，Temporary + Unpersonalized）完成；脚本只负责调用、缓存、逐字引文核对、范围与引用一致性检查和交付拼接，**不改写任何模型产出**。

## 一条命令

```powershell
python chain.py all --tag <名字> --segs all --targets short,v1,<名字>
```

`--segs` 可以写 `S02,S07` 这样的子集；已完成的段落按阶段缓存（`runs/<tag>/<stage>/<seg>.parsed.json`），中断后重跑只补缺失部分。失败的调用自动重试一次。

## 阶段

| 阶段 | 提示词 | 做什么 | 脚本检查 |
|---|---|---|---|
| pool | `prompts/pool_v2.md` | 逐份读 24 份 A 原稿，为本段登记每条体验（原话、原稿范围、判断后的精确小节、邻段排除） | 引文逐字命中；24 份原稿均已登记 |
| synth | `prompts/synth_v4.md` | Pool → STRUCT + 读者珠子 | 账本每条都有去向；facet 小节都在本段内；引文逐字；时间关系方向；读法锚定原稿确实支持所挂 facet；正文引用的 facet 存在 |
| audit | `prompts/audit_v1.md` | 独立审稿：先自己从原稿列出本段全部不同体验，再对匿名版本（顺序随机）评覆盖、错误、异质性、可读性 | 审稿引文逐字核对；按与本段重叠的体验计算覆盖率 |
| report / build | — | 汇总指标（`audit_summary.txt`、`checks.json`）；拼出 `deliverable/` | — |

当前冻结版本写在 `chain_config.json`。改提示词时新建 `*_vN.md` 并改配置，用新的 `--tag`，旧结果保留可比。

## STRUCT 设计（synth 输出）

- `timeline`：本段内部按音乐事件分步（`basis`: stated / inferred），每步挂相关 facet——供视频对时。
- `facets`：每个真正不同的体验。`measures` + `source_range` + `placement`（stated / inferred / segment_wide，不允许比证据更精确）；`dimensions`（身体与动作 / 感官质地 / 情绪色调 / 动因与心理 / 场景与画面 / 人物与关系 / 时间与变化 / 聆听与演奏差异）；`claim`、`image`；`validity`（solid / plausible）；`salience`（core / secondary）；`support`（原稿逐字引文）；`relations`（after / before / contrasts / intensifies / alternative_to / coexists）。
- `readings`：完整的不同听法，必须写 `anchor_sources`，只挂这些原稿支持的 facet；不同原稿的动因只能并列，不能写成因果链。
- `carryover`：原稿范围主要在邻段、无法确认发生在本段的体验——保留但不算 facet、不进正文。
- `ledger`：Pool 每一条的去向（facet / merged / carryover / rejected + 理由）。
- `reader_bead`：给普通听者的一种呈现（约短版 1.2–1.5 倍），列出所用 facet。
- `diff_vs_short`：与旧短版的真实差异（模型自述）。

## 输入

`inputs/A/`：24 份非 Muse 历史 A 原稿（Muse 原稿按用户要求不用；脚本里有断言）。`inputs/structure.json`：冻结十四段。`inputs/short_beads_ref.json`：旧短版（仅作语言/篇幅参考）。`inputs/baselines/v1/`：上一轮单步生成结果，仅作审计对照。

## 迭代记录（三段试点 S02/S07/S13，独立审计）

| 版本 | 改动 | 正文覆盖 | 总覆盖 | 可读性 | 错误/段 | 主要问题 |
|---|---|---|---|---|---|---|
| v2a | pool v1 | — | — | — | — | Pool 过碎（S07 254 条），模型改输出下载文件 |
| v2b | pool v2 + synth v1 | 58% | 100% | 4.33 | 5.3 | 宽范围被定得过窄；读法把不同原稿接成因果；关系方向写反 |
| v2c | synth v2 | 43% | 97% | 4.33 | 2.7 | 拼接降为 0；邻段延续仍做成 facet；正文偏密 |
| v2d | synth v3 | 40% | 95% | 4.67 | 2.3 | 读法挂错 facet；少数听感被当错误排除 |
| v2e | synth v4（冻结） | 38% | 96% | 4.33 | 2.3 | 与 v2d 持平，差异在审稿波动内，停止迭代 |

（各轮的覆盖率由各自那次审稿列出的体验清单计算，跨轮只宜比较同一次审稿内的版本。）
