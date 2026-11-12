---
name: style-matters-for-model-choice
description: "Model selection must weigh language style (concrete human scenes vs abstract state words), not only content; user finds GPT Sol/Luna \"not human speech\""
metadata:
  node_type: memory
  type: feedback
  originSessionId: 5b7665db-3470-493f-ac79-b22c507fb7f0
  modified: 2026-09-30T02:16:56.717Z
---

选模型不能只看内容（饱和池之外的新增），语言风格同样重要（user, 2026-09-29）。用户判断 GPT 系 Sol、Luna"不说人话"：提示词反复要求鲜活，它们仍爱写"悬着""站住"这类抽象状态词，而不是具体的人、动作、场景。

**Why:** 用户读材料的直接感受；run34 评审理由也反复说 Sol/Luna"薄、概括、少具体画面"。但简单数套话词（悬着/站住/落定/长出来…每千字）各家差不多（Sonnet 2.7 最高、Gemini 0.6 最低），所以问题在整体写法抽象，不在个别词——不要拿词频当风格证据。

**How to apply:** 任何模型取舍报告都要单列语言风格；量化时用"每段是具体场景/动作还是抽象状态"这类判断，而非词表计数。关键决策前让用户自己读原文样本（run47 审阅页太累，偏好打包给外部模型研讨）。相关：[[drama-not-a-flaw]]、[[stop-when-conclusive]]。
