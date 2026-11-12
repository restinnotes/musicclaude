"""前 4 段自查：选中的转折条数、主体验 B1 因池子太窄留空的颗数，以及（P4e）有没有说出"对方/两人之间"。"""
import json, sys, re
T, w = sys.argv[1], sys.argv[2]
pool_tag = "P27" if T in ("P4a", "P4c") else ("P28t" if T.startswith("P6") else "P27t")
turns = whole = 0; b1 = []; rel = 0
for s in ("S01", "S02", "S03", "S04"):
    try: d = json.load(open(f"evaluations/synth/{T}_{w}/{s}.json", encoding="utf-8"))
    except Exception: print(s, "还没接完"); continue
    pool = {m["id"]: m for m in json.load(open(f"evaluations/pool/{pool_tag}/{w}/{s}.json", encoding="utf-8"))["mechs"]}
    for c in d["chosen"]:
        for i in c.get("from") or []:
            if "#t" in pool.get(i, {}).get("rep", {}).get("src", ""): turns += 1
            else: whole += 1
        rel += bool(re.search(r"对方|那个人|两个人|两人|回应|心意", c["text"]))
    b1 += [u["id"] for u in d["check"].get("unexplained") or [] if u["id"].endswith("-B1") and u.get("why") == "池子太窄"]
print(f"{T} {w} 前4段：选中整段 {whole} 条、转折 {turns} 条；B1 因池子太窄留空 {b1 or '无'}；提到对方/两人的解释 {rel} 条")
