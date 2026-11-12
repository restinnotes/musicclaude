import json

out = "D:/musicclaude/_bead_auto_20261016/out"
pool = json.load(open(f"{out}/A_POOL_MAP.json", encoding="utf-8"))
meta = pool["_meta"]["sources"]

L = []
L.append("# A_POOL_REVIEW（STEP3·A原文归段中文复核）")
L.append("")
L.append("作品：肖邦《船歌》升F大调 Op.60（116小节）。冻结段：C2＝朝山奈津子／PTNA 2008 セクション十四段（S01–S14），本轮未改动。")
L.append("")
L.append("## 一、去向台账（S01–S14，条目数为含跨段重复的引用数）")
L.append("")
L.append("| 段 | 范围/标签 | PRIMARY | CROSS | UNCERTAIN | 有无PRIMARY |")
L.append("|---|---|---:|---:|---:|---|")
for s in [f"S{i:02d}" for i in range(1, 15)]:
    seg = pool[s]
    p, c, u = len(seg["PRIMARY"]), len(seg["CROSS_SEGMENT"]), len(seg["UNCERTAIN"])
    L.append(f"| {s} | {seg['range']} {seg['label']} | {p} | {c} | {u} | {'有' if p else '无'} |")
L.append("")
L.append("UNRESOLVED 11条（A02-U008、A03-U008、A04-U006、A04-U008、A04-U009、A05-U008、A05-U013、A05-U018、A07-U002、A08-U004、A08-U019）；OUT_OF_RANGE 0条；LONG_RANGE 29条。唯一语义单元170个（A01 21、A02 24、A03 19、A04 22、A05 20、A07 38、A08 26）。")
L.append("")
L.append("UNRESOLVED属来源文本与冻结结构归属冲突（如m.39新主题起点、17–34整体主题说、72–83第一主题返回说、103–116第一主题末返说等），完整原句保留在A_POOL_MAP.json对应清单中，不硬塞、不改写原意。LONG_RANGE收纳全曲总论与后见性心理曲线，不下沉为局部Affect。")
L.append("")
L.append("## 二、错配处理")
L.append("")
L.append("- 凡原始小节范围跨冻结段界的一律在相关各段保留引用，不剪断原句（如mm.1–4跨S01/S02、mm.78–85跨S10/S11、mm.103–116跨S13/S14）。")
L.append("- 与C2边界冲突的判断（如把m.39当新主题起点、把72–83当第一主题再现）一律进UNRESOLVED并注明理由，不替来源校正、不按相邻段硬塞。")
L.append("- 各模型互相矛盾的描述（如S14终结句强收 vs 轻收、S12雪崩 vs 发抖）并存保留，不以多数票裁决。")
L.append("- 超出1–116的编号：本轮8件中未发现，OUT_OF_RANGE为空。")
L.append("")
L.append("## 三、覆盖缺口声明（未编造部分）")
L.append("")
L.append("- 已完整归段8件：A01 gpt56w/int、A02 gflash/int、A03 muse/int、A04 opus/int、A05 grok/int、A07 gflash_web/web、A08 luna/web。")
L.append("- 未归段3件：A06 gpt56w/web（只拿到部分示例回包，无完整归段）、A09 opus_web、A10 sol61_cx_web、A11 orig V2A基线（均未取得可用归段回包）。上述3件在A_POOL_MAP.json中无任何条目，后续补齐后按A09-Uxxx/A10-Uxxx/A11-Uxxx、A06-Uxxx编号续接，不改动既有UID与C2边界。")
L.append("- A01–A05条目为ID引用式（原文全句存于模型侧交付文件，本机存代表句与去向台账）；A07、A08条目内嵌完整原文摘句、原始小节范围与判定说明。凡无原文依据的一律未写。")
L.append("")
L.append("## 四、先复核后生成声明")
L.append("")
L.append("本Pool为复核后方可消费的归段台账：归入某段只代表原文可追溯地指向该段，不代表该研究的音乐判断已经核实。后续任何生成（Bead等）必须先实际应用本复核后Pool（以A_POOL_MAP.json为准，UNRESOLVED/LONG_RANGE不得当作段落PRIMARY使用），才允许生成；未补齐的3件不得默认已覆盖。")
L.append("")
L.append("## 五、来源清单")
L.append("")
for uid in ["A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08", "A09", "A10", "A11"]:
    m = meta[uid]
    done = "已归段" if uid in ("A01", "A02", "A03", "A04", "A05", "A07", "A08") else "未归段"
    L.append(f"- {uid} {m['model']}/{m['channel']} {done} bytes={m['bytes']} sha256={m['sha256']} 路径={m['path']}")
L.append("")
L.append("链路：仅GPT-6w（gpt-6-thinking）。批1（A-int五件＋SEG，6附件）exit=0耗时992秒；批2续接（6附件）pre_submit秒拒；A07/A08/A06单附件各一次成功（A06仅部分示例）。未做git、未读谱、未看T/H/Thread/WHY/珠子旧切点。")

open(f"{out}/A_POOL_REVIEW.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
print("review lines:", len(L))
