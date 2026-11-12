from pathlib import Path
p=Path("STATUS.md"); t=p.read_text(encoding="utf-8")
i=t.index("## 主线"); j=t.index("## 基础设施")
new="""## 主线

- 成品 `qu`（`schemes/Q15.json`）：先想经历（不看珠子）→ 选路 → 珠子去掉画面情节 → 一次写完线。字数 1502/1528；覆盖 Op.60 49/50、Op.61 49/48；单独读成立 12/14、13/14、13/13、13/13。对原主线 `m6w` 盲比 6/8 选新版；净胜 单独 +5.0、啰嗦 +9.0、人话 +12.0、覆盖 −0.38。
- 分段、A 稿、珠子、Center 已定，不在迭代范围。

## 现在在哪（11-02 八小时自主迭代已结束，汇报已发，等用户读）

- 没到收敛：只是到点停下。还差的：Op.60 第 7 段“对方也曾需要自己”没有铺垫；单次抽样差异大，Best-of-N 没试；评委不查形态（`runs/_form_check.py` 只是我自己查）。
- 等用户决定：要不要把“每条一句、每段 2–4 条”加进判定线（判定线只有用户能改）；线这种偏长条目（`ql`）和每条一句（`qu`）到底要哪种。
- 工具：`pipe.py run schemes/<方案>.json <tag>`（跑流水线）、`runs/quick.sh <方案> <tag>`（生成加快筛）、`runs/meas.sh <tag>`（全部测量）、`verdict.py <tag> [base]`（判定）、`human_score.py <tag> ...`（给人看的评分）、`scoreboard.py`（进度表）、`advisor_followup2.py`（只改写线层时交回提出者）、`v6weave.py <tag>`（合写）。

"""
p.write_text(t[:i]+new+t[j:],encoding="utf-8")
