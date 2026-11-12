---
name: baseline-anchor
description: "Every synthesis/article version must be compared blind against the original V2A-on-Gemini output (reference texts 02/05), not only against sibling variants"
metadata:
  node_type: memory
  type: feedback
  originSessionId: f5c661df-9026-436a-99d1-94c3c437c97f
  modified: 2026-09-25T18:28:49.047Z
---

综合稿（以及任何最终文章候选）必须和起点对照：V2A 原版提示词 + Gemini 联网的产出（reference 里 Op.52 文本 02、05；三首作品的补跑在 runs/run16_baseline_anchor）。只在变体之间互比，会看不出整体生动度已经掉下去。

**Why:** 2026-09-25 用户读了 SYN_v0 后说"相比最开始的 gemini 感觉差太多了"。我此前只在 SYN 变体之间、分支模型之间比较，从没把综合稿放回起点对照，漏掉了整体退化：开头免责、每段堆多个小比喻、"两种读法同时成立"式的对冲、每段套"因为前面……所以"的来路句，没有一个贯穿全篇的强判断和每段一个抓得住的核心意象。

**How to apply:** 每轮综合评审都把起点稿放进匿名盲评；标准判定表加"相对起点"一列；退化就先做逐句归因找原因，不以"更合宪法"为由接受生动度下降。相关：[[music-run-method]]、[[no-self-candidate]]。
