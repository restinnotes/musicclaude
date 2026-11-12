---
name: stop-when-conclusive
description: Gemini quota is plentiful — spend freely on anything possibly meaningful; only skip clearly useless work (e.g. re-measuring a conclusion that is already settled)
metadata:
  node_type: memory
  type: feedback
  originSessionId: 92476755-b11c-4869-8156-9f3da1650d78
  modified: 2026-09-26T08:40:56.763Z
---

Gemini 额度很多，但凡可能有意义的调用都可以放开用、放开并行；只有明显没用的才不烧——典型是一项测量的结论已经大概率成立，还为了把数字算精确而跑完全量。

**Why:** 2026-09-26 用户先问"这烧的有价值吗……能达成很大概率的结论就可以不继续烧了"（当时新内容统计重算 20/120 已足够下结论），随后补充"其实我们 gemini 额度可以有非常多，只是如果极其没有用的东西我就不是特别想烧额度了，但是但凡有可能有意义的就可以随便烧"。

**How to apply:** 不要因为省额度而压缩有意义的工作（更多样本、更多模型对照、Gemini 做覆盖率/审计辅助判断都可以）。只在"结果不会改变任何决定"时停手；停手前先用已有部分结果确认结论已稳。受限的是代理并发（见 [[music-run-cli-invocation]] 的 Gemini 12 并发上限），不是额度。相关：[[music-run-method]]。
