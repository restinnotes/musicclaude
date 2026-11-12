> **先读 `STATUS.md`（现在在哪、下一步）**，再按需读：`THREAD_SPEC.md`（用户要什么）· `DAG.md`（新作品 → 珠子 + 线的生产流程，和 THREAD_SPEC 同等地位）· `开发规范.md`（怎么干活）· `VERSIONS.md`（版本登记表，`python versions.py` 重建）。下面是 10-20 的旧交付说明。

# Thread 提示词自进化 · 交付包（2026-10-20）

先读：`FINAL_REPORT.md`（结论与证据）→ `showcase/`（直接读样本，尤其请对照 00_B0 与 01/03）→ `FINAL_INPUT_PROTOCOL.md`（怎么用）→ `SEGMENTATION.md`（小节分段上游机制）。

- 最终提示词：`FINAL_PROMPT_TEMPLATE.txt`（模板）/ `FINAL_PROMPT.txt`（Op.60 渲染版）；第二遍：`FINAL_REDRAFT_PROMPT.txt`
- 全部盲评表：`RESULTS.md`；逐次调用：`runs/<run-id>/`（prompt/input/output/call.log）；`EXPERIMENT_LOG.tsv`
- 提示词谱系：`prompt_versions/CHANGELOG.md`
- 机器可读分段：`works/*/segmentation.json`；Thread 输出转逐段 JSON：`python segcheck.py --export <run> out.json`

未打包：同目录里另一会话早期留下的 `logs/ pkg/ tools/ segmentation/`（与本交付无关；其 13 篇 r1 生成已复制进 `runs/r1_*`）。
