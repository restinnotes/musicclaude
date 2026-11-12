import json
pool = json.load(open("D:/musicclaude/_bead_auto_20261016/out/A_POOL_MAP.json", encoding="utf-8"))
template = open("D:/musicclaude/_bead_auto_20261016/music_bead_published_structure_only_20261015/prompts/04_固定乐段Aonly珠子.txt", encoding="utf-8").read().strip()
CTX = {
 "S01": "C2标签：序奏。C1（Rink 1988 p.197）边界一致。C3（Gerling 2014）：Introduction 1–4，终点m.4落在S02内；C2引子终点为m.3。",
}
WORK = "肖邦《船歌》升F大调 Op.60（Frederic Chopin – Barcarolle in F-sharp major, Op. 60；116小节，单乐章）"
segline = "S01 mm.1-3 序奏（C2冻结十四段之一，S01–S14连续覆盖1–116无重叠）"
p = template.replace("{{WORK}}", WORK).replace("{{SEGMENT_ID_AND_RANGE}}", segline)
p = p.replace("{{A_POOL}}", "见随附附件（本段A Pool机械附件ATTACH_S01_Apool.txt，含PRIMARY/CROSS_SEGMENT/UNCERTAIN逐条与int五件交集节全文；UNRESOLVED/LONG_RANGE未收录）：")
p = p.replace("{{PUBLISHED_STRUCTURE_CONTEXT}}", "C2=朝山奈津子／PTNA(2008)セクション（https://enc.piano.or.jp/musics/543；Rink 1988 p.197 Example 1已交叉核对边界一致）。" + CTX["S01"])
open("D:/musicclaude/_bead_auto_20261016/out/STEP4_inputs/STEP4_short_S01.txt", "w", encoding="utf-8").write(p)
print("short prompt chars:", len(p))
