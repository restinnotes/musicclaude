"""11-02: export every review prompt used in experiments (迭代准则.md) verbatim to 迭代准则_评审提示词.md for the user to read.
{…} are filled at run time. usage: python exp_export.py"""
import os
os.environ["JV"] = "2"
from pathlib import Path
import v6cov, v6alone, v6fix, line_dag, lang_open, e2e_open, prompt_advisor

L = [("覆盖 v6cov（JV=2，11-02 对齐标准）", v6cov.COV2),
     ("覆盖和盲比里填入 {WHAT} 的线说明（v6fix.WHAT2）", v6fix.WHAT2),
     ("单独读 v6alone · 逐段讲不讲得通（JV=2）", v6alone.ALONE2),
     ("单独读 v6alone · 是不是复述珠子（JV=2）", v6alone.TRANS2),
     ("盲比 v6fix blind（JV=2，四个维度）", v6fix.BLIND2),
     ("四维开放评审 e2e_open（找问题）", e2e_open.P),
     ("语言开放评审 lang_open v2（找问题；DAG 的 N09 也用）", lang_open.P2),
     ("挑稿 line_dag.JUDGE（DAG 的 N05c）", line_dag.JUDGE),
     ("提示词顾问 prompt_advisor（找改法；材料部分运行时填入）", prompt_advisor.P)]
md = ["# 迭代准则用到的评审提示词（原文）", "", "由 `python exp_export.py` 生成，不要手改。{…} 是运行时填入的内容。用户过目后，有问题的地方改代码、再导出。", ""]
for n, p in L:
    md += [f"## {n}", "", "```text", p, "```", ""]
Path(__file__).with_name("迭代准则_评审提示词.md").write_text("\n".join(md), encoding="utf-8")
print("ok", len(L))
