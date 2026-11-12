# Bead 优先：独立结构分段 + A/T/H 贡献检验（2026-10-15）

**把本包的 `00_CLAUDE_MASTER_TASK.md` 直接交给在 `D:\musicclaude` 工作的 Claude 主 Agent。** 其他文件是它必须读取并实际使用的分工提示词、实验安排和数据契约；不是空的方案清单。

## 这次唯一要完成的事

针对可以泛化到不同作品的机制，先独立找**听得出来的完整音乐段落**，据此建立逐段 Pool；把已有的 A/T/H 原始研究完整、可追溯地关联到这些段落；**逐分支、逐模型验证是否真正帮助 Bead**，然后生成有限数量的、可以让人直接审阅的高质量珠子。**用户读过珠子、确认它有用以后，才开始 Thread / History / Outer / E7。**

```text
                          音乐作品（谱面/录音/权威结构分析）
                                       │
                         独立结构分析：宏观乐段边界
                                       │
  已有 A-int/A-web 原文 ─┐             │
  已有 T-int/T-web 原文 ─┼─────→ 固定乐段 ID / 时间范围 ←─────（不由珠子生成器重切）
  已有 H1–H5 原文 ──────┘             │
                                       ▼
                         每段独立 A/T/H 来源 Pool
                                       │
                                       ▼
                            A-only 珠子基线
                                       │
                  ┌────────────────────┴────────────────────┐
                  ▼                                         ▼
        T 内容做独立增量测试                      H1–H5 各自做增量测试
                  │                                         │
                  └────────────────────┬────────────────────┘
                                       ▼
                      每一模型 × 每个分支的增益/损害检查
                                       │
                                       ▼
                        只保留经证实有价值的珠子内容
                                       │
                                       ▼
                             人工阅读与验收停止
```

## 本包文件

- `00_CLAUDE_MASTER_TASK.md`：给执行 Agent 的完整指令，限定范围、执行顺序、产物和停止条件。
- `01_SOURCE_EVIDENCE_AND_CAUTION.md`：核实过的 run126/127/129 实验事实；不要把过往模型统计当作这次已通过。
- `02_ABLATION_AND_MODEL_MATRIX.md`：逐研究分支、逐模型检验的对照设计。
- `prompts/01_STRUCTURAL_RESEARCH_WEB.txt`：**通用**、独立外部结构研究提示词；不允许读 A/T/H。
- `prompts/02_STRUCTURAL_LISTEN_OR_SCORE.txt`：**通用**、独立谱面/实际聆听边界核查提示词；不允许伪称已经听过录音。
- `prompts/03_STRUCTURAL_ADJUDICATION.txt`：在独立分析之间选择完整的宏观段落，保留少数次级边界。
- `prompts/04_POOL_ALIGNMENT.txt`：把原始 A/T/H 按段落映射，不随意拆文本、不改写来源。
- `prompts/05_BEAD_A_BASELINE.txt`：仅 A 研究、固定段落的珠子基线。
- `prompts/06_T_BEAD_ABLATION.txt`：单独检验 T 对 Bead 是否有增量。
- `prompts/07_H_BEAD_ABLATION.txt`：单独检验各 H 分支、各来源模型，不强制混合。
- `prompts/08_BEAD_CONSOLIDATION.txt`：只统合有证据支持的内容，不允许重切音乐。
- `prompts/09_BLIND_BEAD_REVIEW.txt`：匿名审阅实际珠子、对照原始素材与质量损失。
- `examples/OP60_HISTORICAL_SEGMENTS_REFERENCE.json`：只用于实验对照的 Op.60 历史九段，**不属于通用结构提示词的例子或固有规则**。
- `schemas/STRUCTURE_OUTPUT_CONTRACT.json`：结构结果字段模板（不是模型会自动保证的事实）。

## 两个重要约束

**“有独立研究结果”≠“已证实能改善珠子”。** 历史 run127 发现 H 混入会损失 A 核心，而 T 从来不是理所当然应当直接写进【此刻】。本次通过消融来回答，不先断言。

**“分段有效”≠“每段都必须上屏”。** 这一轮只定可复用的音乐段落与好的内容珠子，屏幕更新及 Thread 是下一阶段。不要为了 30 字上屏而压坏研究素材。
