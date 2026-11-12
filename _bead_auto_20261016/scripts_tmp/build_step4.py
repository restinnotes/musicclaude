import re, json, os

BASE = "D:/musicclaude/music_work_since_1008v3_20261009/runs"
OUT = "D:/musicclaude/_bead_auto_20261016/out/STEP4_inputs"
os.makedirs(OUT, exist_ok=True)

pool = json.load(open("D:/musicclaude/_bead_auto_20261016/out/A_POOL_MAP.json", encoding="utf-8"))
template = open("D:/musicclaude/_bead_auto_20261016/music_bead_published_structure_only_20261015/prompts/04_固定乐段Aonly珠子.txt", encoding="utf-8").read().strip()

SRC = {
 "A01": ("run106_gpt56_material/outputs/A-int__A_int_v1__gpt56w__op60__s1.md", "gpt56w/int", r"^### mm\. ",
         [(1,4),(5,20),(21,38),(39,56),(57,77),(78,85),(86,92),(93,104),(105,116)]),
 "A03": ("run115_facts/outputs/A-int__A_int_v1f__gflash__op60__s1.md", "gflash/int", r"^### 第",
         [(1,3),(4,16),(16,35),(35,61),(61,83),(84,102),(103,116)]),
 "A04": ("run115_facts/outputs/A-int__A_int_v1f__muse__op60__s1.md", "muse/int", r"^\*\*mm\.",
         [(1,3),(4,13),(14,16),(16,23),(24,35),(35,40),(39,61),(61,70),(71,77),(78,83),(84,92),(93,102),(103,110),(110,111),(111,116)]),
 "A05": ("run32_opus_sol/outputs/A-int__A_int_v1__opus__op60__s1.md", "opus/int", r"^## \d+\. ",
         [(1,3),(4,5),(6,16),(17,34),(35,71),(72,83),(84,92),(93,102),(103,116)]),
 "A06": ("run40_grok/outputs/A-int__A_int_v1__grok__op60__s1.md", "grok/int", r"^\*\*mm\. ",
         [(1,3),(4,16),(17,23),(24,39),(40,71),(72,83),(84,93),(93,102),(103,116)]),
}
srcs = {}
for axx, (rel, who, pat, ranges) in SRC.items():
    txt = open(f"{BASE}/{rel}", encoding="utf-8").read()
    lines = txt.split("\n")
    idx = [i for i, l in enumerate(lines) if re.match(pat, l.strip())]
    assert len(idx) == len(ranges), f"{axx}: {len(idx)} != {len(ranges)}"
    secs = []
    for k, i in enumerate(idx):
        end = idx[k+1] if k+1 < len(idx) else len(lines)
        secs.append({"range": ranges[k], "head": lines[i].strip(), "text": "\n".join(lines[i:end]).strip()})
    srcs[axx] = {"who": who, "path": "music_work_since_1008v3_20261009/runs/" + rel,
                 "sha": pool["_meta"]["sources"][axx]["sha256"],
                 "preamble": "\n".join(lines[:idx[0]]).strip(), "secs": secs}

SEGS = [("S01","1-3","序奏"),("S02","4-16","第1主題"),("S03","17-23","間句"),("S04","24-34","第1主題（確保）"),
        ("S05","35-39","間句"),("S06","40-50","第2主題前半"),("S07","51-61","第2主題前半（確保）"),
        ("S08","62-71","第2主題後半"),("S09","72-77","間句"),("S10","78-83","挿入句"),
        ("S11","84-92","第1主題（再現）"),("S12","93-102","第2主題後半（再現）"),
        ("S13","103-110","第2主題前半（再現）"),("S14","111-116","終結句")]

CTX = {
 "S01": "C2标签：序奏。C1（Rink 1988 p.197）边界一致。C3（Gerling 2014）：Introduction 1–4，终点m.4落在S02内（cross-boundary）；C2引子终点为m.3。",
 "S02": "C2标签：第1主題。C1边界一致。C3支点之一：m.4（落在S02起点）。",
 "S03": "C2标签：間句。C1标签：‘Development’（边界一致，标签保留不统一）。",
 "S04": "C2标签：第1主題（確保）。C1边界一致。",
 "S05": "C2标签：間句。C1标签：Transition。C3：m.39落在S05内（cross-boundary；C3中区39–83起点）。",
 "S06": "C2标签：第2主題前半。C1边界一致。C3中区39–83起点落在S05/S06一带，本段在其内。",
 "S07": "C2标签：第2主題前半（確保）。C1边界一致。S7拍位51.1待复核，不吸附为整数边界。",
 "S08": "C2标签：第2主題後半。C1边界一致。S7拍位71.0待复核，不吸附为整数边界。",
 "S09": "C2标签：間句。C1标签：Transition（边界一致）。",
 "S10": "C2标签：挿入句。C1标签：‘Dolce sfogato’。C3：dolce sfogato 78–83与C2数值一致。",
 "S11": "C2标签：第1主題（再現）。C3：theme A′ 84–92与C2数值一致；支点m.84；后外围起点86落在S11内（cross-boundary）。",
 "S12": "C2标签：第2主題後半（再現）。C1边界一致。",
 "S13": "C2标签：第2主題前半（再現）。C1标签：Coda (B(1)″)。103–111为多源明确分歧区（Damschroder整段coda自103起／Kopp以111为coda起点／S7拍位102.1–111.1待复核），全部审计留存，不改动C2冻结边界。",
 "S14": "C2标签：終結句。C1标签：Coda。103–111分歧区说明见S13；C2冻结111–116为終結句。",
}
WORK = "肖邦《船歌》升F大调 Op.60（Frederic Chopin – Barcarolle in F-sharp major, Op. 60；116小节，单乐章）"

def verbatim(e):
    return e.get("原文") or e.get("原文摘句") or "（本条在A_POOL_MAP中无逐字原文，见第四部分同来源交集节全文）"

manifest = {}
for s, rng, label in SEGS:
    a, b = int(rng.split("-")[0]), int(rng.split("-")[1])
    seg = pool[s]
    L = []
    L.append(f"【STEP4·本段A Pool附件 · {s} mm.{rng} {label} · 机械摘录，未改一字】")
    L.append("来源：A_POOL_MAP.json（归段7件：A01/A03/A04/A05/A06为int通道五件，A07/A08为web两件；缺口4件A02(gpt56w/web半成品)/A09(opus_web)/A10(sol61_cx_web)/A11(V2A基线)无条目）。")
    L.append("UNRESOLVED 11条、LONG_RANGE 29条不进读者正文，本附件未收录。")
    if not seg["PRIMARY"]:
        L.append(f"【段事实】本段PRIMARY为空（已核实A_POOL_MAP，{s}无PRIMARY条目），仅以下CROSS_SEGMENT／UNCERTAIN材料；仍按同一模板投一轮。")
    for cat, title in (("PRIMARY","一、本段PRIMARY逐条"),("CROSS_SEGMENT","二、本段CROSS_SEGMENT逐条"),("UNCERTAIN","三、本段UNCERTAIN（仅供内部台账参考，归属不确定；读者正文慎用）")):
        L.append(f"\n===== {title}（共{len(seg[cat])}条） =====")
        for e in seg[cat]:
            L.append(f"\n[{e['UID']}｜{e['来源模型']}/{e['通道']}｜{e['归类']}]原始小节范围：{e.get('原始小节范围','（未记录）')}")
            if e.get("判定说明"): L.append(f"判定说明：{e['判定说明']}")
            L.append(verbatim(e))
    L.append(f"\n===== 四、int五件与本段（mm.{rng}）有小节交集的源文件节，全文verbatim =====")
    L.append("（小节有交集≠STEP3单元切分；各UID的归类以A_POOL_MAP为准；每节后附本段Pool中来自该来源的候选UID清单）")
    overlap_count = 0
    for axx in ("A01","A03","A04","A05","A06"):
        cand = [e["UID"]+":"+e["归类"] for cat in ("PRIMARY","CROSS_SEGMENT","UNCERTAIN") for e in seg[cat] if e["UID"].startswith(axx+"-")]
        hits = [sec for sec in srcs[axx]["secs"] if sec["range"][0] <= b and a <= sec["range"][1]]
        if not hits: continue
        for sec in hits:
            overlap_count += 1
            ra, rb = sec["range"]
            L.append(f"\n[来源{axx}｜{srcs[axx]['who']}]本节原始范围mm.{ra}–{rb}（与本段mm.{rng}交集mm.{max(a,ra)}–{min(b,rb)}）｜本段Pool中来自该来源的候选UID：{('、'.join(cand)) if cand else '无'}")
            L.append(f"路径：{srcs[axx]['path']}")
            L.append(sec["text"])
    L.append("\n===== 五、各来源preamble全文（全局底色，跨段，不进读者正文） =====")
    for axx in ("A01","A03","A04","A05","A06"):
        L.append(f"\n[来源{axx}｜{srcs[axx]['who']} preamble全文]")
        L.append(srcs[axx]["preamble"])
    attach = "\n".join(L)
    open(f"{OUT}/ATTACH_{s}_Apool.txt", "w", encoding="utf-8").write(attach)

    segline = f"{s} mm.{rng} {label}（C2冻结十四段之一，S01–S14连续覆盖1–116无重叠）"
    p = template.replace("{{WORK}}", WORK).replace("{{SEGMENT_ID_AND_RANGE}}", segline)
    p = p.replace("{{A_POOL}}", "见随附附件ATTACH_"+s+"_Apool.txt（全文附后以备核对）：\n\n" + attach)
    p = p.replace("{{PUBLISHED_STRUCTURE_CONTEXT}}", "C2=朝山奈津子／PTNA(2008)セクション（https://enc.piano.or.jp/musics/543；Rink 1988 p.197 Example 1已交叉核对边界一致）。" + CTX[s])
    open(f"{OUT}/STEP4_prompt_{s}.txt", "w", encoding="utf-8").write(p)
    manifest[s] = {"range": rng, "label": label, "PRIMARY": len(seg["PRIMARY"]),
                   "CROSS": len(seg["CROSS_SEGMENT"]), "UNCERTAIN": len(seg["UNCERTAIN"]),
                   "int_overlap_secs": overlap_count, "prompt_chars": len(p), "attach_chars": len(attach)}

json.dump(manifest, open(f"{OUT}/STEP4_manifest.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for s, m in manifest.items():
    print(s, m["range"]+m["label"], "P=%d C=%d U=%d" % (m["PRIMARY"], m["CROSS"], m["UNCERTAIN"]),
          "ovsecs=%d prompt=%d attach=%d" % (m["int_overlap_secs"], m["prompt_chars"], m["attach_chars"]))
