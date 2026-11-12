import json

pool = json.load(open("D:/musicclaude/_bead_auto_20261016/out/A_POOL_MAP.json", encoding="utf-8"))
template = open("D:/musicclaude/_bead_auto_20261016/music_bead_published_structure_only_20261015/prompts/04_固定乐段Aonly珠子.txt", encoding="utf-8").read().strip()
WORK = "肖邦《船歌》升F大调 Op.60（Frederic Chopin – Barcarolle in F-sharp major, Op. 60；116小节，单乐章）"
CTX = {
 "S01": "C2标签：序奏。C1（Rink 1988 p.197）边界一致。C3（Gerling 2014）：Introduction 1–4，终点m.4落在S02内；C2引子终点为m.3。",
 "S02": "C2标签：第1主題。C1边界一致。C3支点之一：m.4（落在S02起点）。",
 "S03": "C2标签：間句。C1标签：‘Development’（边界一致，标签保留不统一）。",
 "S04": "C2标签：第1主題（確保）。C1边界一致。",
 "S05": "C2标签：間句。C1标签：Transition。C3：m.39落在S05内（C3中区39–83起点）。",
 "S06": "C2标签：第2主題前半。C1边界一致。C3中区39–83起点落在S05/S06一带，本段在其内。",
 "S07": "C2标签：第2主題前半（確保）。C1边界一致。S7拍位51.1待复核，不吸附为整数边界。",
 "S08": "C2标签：第2主題後半。C1边界一致。S7拍位71.0待复核，不吸附为整数边界。",
 "S09": "C2标签：間句。C1标签：Transition（边界一致）。",
 "S10": "C2标签：挿入句。C1标签：‘Dolce sfogato’。C3：dolce sfogato 78–83与C2数值一致。",
 "S11": "C2标签：第1主題（再現）。C3：theme A′ 84–92与C2数值一致；支点m.84；后外围起点86落在S11内。",
 "S12": "C2标签：第2主題後半（再現）。C1边界一致。",
 "S13": "C2标签：第2主題前半（再現）。C1标签：Coda (B(1)″)。103–111为多源明确分歧区（Damschroder整段coda自103起／Kopp以111为coda起点／S7拍位102.1–111.1待复核），全部审计留存，不改动C2冻结边界。",
 "S14": "C2标签：終結句。C1标签：Coda。103–111分歧区说明见S13；C2冻结111–116为終結句。",
}
SEGS = [("S01","1-3","序奏"),("S02","4-16","第1主題"),("S03","17-23","間句"),("S04","24-34","第1主題（確保）"),
        ("S05","35-39","間句"),("S06","40-50","第2主題前半"),("S07","51-61","第2主題前半（確保）"),
        ("S08","62-71","第2主題後半"),("S09","72-77","間句"),("S10","78-83","挿入句"),
        ("S11","84-92","第1主題（再現）"),("S12","93-102","第2主題後半（再現）"),
        ("S13","103-110","第2主題前半（再現）"),("S14","111-116","終結句")]
for s, rng, label in SEGS:
    segline = f"{s} mm.{rng} {label}（C2冻结十四段之一，S01–S14连续覆盖1–116无重叠）"
    p = template.replace("{{WORK}}", WORK).replace("{{SEGMENT_ID_AND_RANGE}}", segline)
    p = p.replace("{{A_POOL}}", f"见随附附件（本段A Pool机械附件ATTACH_{s}_Apool.txt，含PRIMARY/CROSS_SEGMENT/UNCERTAIN逐条与int五件交集节全文；UNRESOLVED/LONG_RANGE未收录）：")
    p = p.replace("{{PUBLISHED_STRUCTURE_CONTEXT}}", "C2=朝山奈津子／PTNA(2008)セクション（https://enc.piano.or.jp/musics/543；Rink 1988 p.197 Example 1已交叉核对边界一致）。" + CTX[s])
    open(f"D:/musicclaude/_bead_auto_20261016/out/STEP4_inputs/STEP4_short_{s}.txt", "w", encoding="utf-8").write(p)
    print(s, len(p))
