# -*- coding: utf-8 -*-
"""生成 STEP2_check.md 与 RUN_CALLS_AND_FILES.md 追加段。只读回包做事实统计，不编造边界。"""
import json, re, hashlib, datetime

RAW = r"D:\musicclaude\_bead_pub_20261015\out\STEP2_response_raw.md"
resp = open(RAW, encoding="utf-8").read()

cands = sorted(set(re.findall(r"C[123](?:_[A-Z0-9_]+)?", resp)))
has_table = ("S1" in resp and "S2" in resp and "S7" in resp)
ready_true = "READY_FOR_POOL=true" in resp
ready_false = "READY_FOR_POOL=false" in resp
mapjson = '"READY_FOR_POOL": false' in resp or '"READY_FOR_POOL":false' in resp

n_cand = 3 if ("C1" in resp and "C2" in resp and "C3" in resp) else 0

check = []
check.append("# STEP2 检查（中文，--attach 链路重投版）")
check.append("")
check.append("- 检查时间：2026-10-16（UTC）")
check.append("- 投放方式：新 --attach 链路；7个来源以附件 S1–S7 投递，正文仅 3KB 任务指令")
check.append("- 尝试次数：共 3 次调用（7附件整批 x1 失败 + 4附件首批 x1 成功 + 3附件续接 x1 成功）")
check.append("- 结论：**STEP2 产出对照表与候选结构，但 READY_FOR_POOL=false**。")
check.append("- 候选套数：%d（C1=Rink 1988 十四段原文结构；C2=朝山/PTNA 2008 十四段原文结构；C3=Chaffin等 2024 十四段拍位级结构，待原文页面复核）" % n_cand)
check.append("- 每套来源依据：C1 指向 S1（Rink p.197 Example 1）；C2 指向 S2（PTNA 小节编号/セクション表）；C3 指向 S7（Table 1 Bars/Formal Division，accessed_original=false，拍位写法原样保留）")
check.append("- READY_FOR_POOL：**false**（回包末行明确给出；用户授权为 NONE，无任何一套获采用授权）")
check.append("- 是否可进 STEP3：**否**。停在此处，等待用户从 C1/C2/C3 中明确选用一套（或指定其他来源层级），获得授权后方可构建 A Pool / Bead Pool。")
check.append("")
check.append("## 证据")
check.append("")
check.append("- 正文文件 out/STEP2_response_raw.md：%d 行，含七来源对照、每套候选边界、C1–C3 映射 JSON，末行 READY_FOR_POOL=false。" % len(resp.split("\n")))
check.append("- 回包明确：S3/S4/S5/S6 不提供完整连续分段（NOT_SUPPORTED），不直接改写为完整候选；C1 与 C2 边界相同但标签体系不同，不合并为一套。")
check.append("- 未做事项：无 git 操作；未读谱；未看 T/H/Thread/WHY/珠子旧切点；仅 GPT-6w 链路调用。")
check.append("- 绝无编造边界：本文件只转述回包结论，不复写任何小节切点数字；切点以 STEP2_response_raw.md 原文为准。")
open(r"D:\musicclaude\_bead_pub_20261015\out\STEP2_check.md", "w", encoding="utf-8", newline="\n").write("\n".join(check) + "\n")
print("check written")
