# Music Pipeline — A-only 珠子恢复实验（替代上一版 ZIP）

**直接把 `00_交给Claude_主任务.md` 发给当前负责 `D:\musicclaude` 的 Claude Agent。** 本包只做“独立音乐分段 → A-int/A-web Pool → 珠子合成 → 质量验收”，**停止在 Bead**。

旧包 `music_bead_structure_ablation_20261015.zip` 的 “A+T / A+H1–H5 混入珠子” 实验安排已撤回；不要按旧包执行，也不必修改已有历史 run。

## 本轮 DAG

```text
                    作品/乐章
                   /         \
     独立音乐结构证据          现存 A-int/A-web 原始研究
  (可靠外部分析/谱面/录音)     (不同模型、联网/内部、不同样本)
                   \         /
             冻结宏观乐段结构
                       ↓
           按乐段对齐 A 原文、保留完整来源
                       ↓
               各乐段 A-only Pool
                       ↓
             A-only Bead 生成与合并
                       ↓
       来源模型贡献审查 + 合成模型公平对照
                       ↓
            人能直接阅读的珠子 + 溯源
                       ↓
                 用户验收，停止
```

**T 和 H1–H5 不在本轮 Bead 输入里。** 不删除它们、不宣布它们无用：T、H3 等主要与后续 History/Thread 的关系候选有关；H4 期待、H5 重听等可能另有意义。H3 只是 HET 异质研究中的 H3 分支，不是 Affect 的必备输入。其他 H 是否值得未来保留/合并，是另一项独立任务。

注意：音乐结构研究可以为 Bead 提供少量真实的音乐锚点，但**不编写 Affect 情感文本**；A 的既有原文如果混入未来后见之明，必须标出，不因为它属于 A 就自动认定合法。

## 文件结构

- `00_交给Claude_主任务.md`：可执行完整任务，工作流、权限与停机条件。
- `01_历史依据_什么已验证.md`：此前 A/T/H、分段、写手测试的已知结论和限制。
- `02_实验矩阵_只比A模型.md`：按来源模型 / 写手模型分开的公平比较和产物验收标准。
- `prompts/01_独立外部结构分析.txt`：**通用**音乐结构研究提示词，不包含特定曲目、分段数量或历史九段。
- `prompts/02_谱面与聆听边界复核_可选.txt`：可选的独立乐谱/音频验证；无权限必须如实报告。
- `prompts/03_宏观切点裁决.txt`：按音乐证据裁决固定的宏观乐段。
- `prompts/04_A原文归段建Pool.txt`：只允许 A-int/A-web 进入 Bead Pool。
- `prompts/05_Aonly珠子生成.txt`：固定乐段、一段一颗主珠子、保留各类感受和原文来源。
- `prompts/06_Aonly双样本统合.txt`：比较/合并同一 A Pool 的两份珠子，防遗漏与抽象化。
- `prompts/07_A研究来源贡献评估.txt`：逐模型、逐 int/web 来源评估 A 原料贡献。
- `prompts/08_珠子写手匿名对照评审.txt`：同输入条件下比较 Bead 写手、旧文稿和基准。
- `schemas/structure_output.schema.json`：通用结构输出校验字段。
- `examples/OP60_RUN102_REFERENCE_ONLY.json`：旧九段**盲后对照材料，禁止传入结构分析生成提示词**。
- `examples/BEAD_RECORD_EXAMPLE.json`：仅为字段形状示范，不是作品文本示例。
- `MANIFEST_SHA256.json`：本包文件哈希。

**最终审核材料必须是实际的珠子全文和被丢失/保留的 A 原文，而不是“通过率”“覆盖率”或 Agent 的自评。**
