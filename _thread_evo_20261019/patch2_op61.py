"""10-27: S08/S09 of the Op.61 line get package 3's own sentences back (verbatim, counted as 包3; nothing newly written),
S08 from the tidied version (its 我 already turned into 他). Then the package-3 comparison again (tag p2)."""
import json, shutil
import covjudge, finalize3, tidy3
T, w = "P3a", "op61"
d, st = finalize3.load(T, w)
shutil.copy(d / "final_line.json", d / "final_line_p2_before.json")
line = json.loads((d / "final_line.json").read_text(encoding="utf-8"))
tidy = {s["sec"]: s for s in json.loads((d / "final_line_p1_before.json").read_text(encoding="utf-8"))["sections"]}
P8 = {"feel": "刚才安静敞开愿望的经历确实存在，突来的寒意不能把它抹去。", "why": "那份柔软仍在；再次碰到它时，他不只承受惊悸，也确实感到亲近和喘息。", "src": "包3"}
P9 = [{"feel": "挺立、温暖的刺痛和敞开愿望的经历，使最初无从安放的失落不再空无内容。", "why": "", "src": "包3"},
      {"feel": "他仍不知该如何继续，但这是认清牵挂之后仍无答案，不是又变回一无所知。", "why": "", "src": "包3"}]
for i, s in enumerate(line["sections"]):
    if s["sec"] == "S08":
        line["sections"][i] = dict(tidy["S08"], items=[P8] + tidy["S08"]["items"])
    if s["sec"] == "S09":
        line["sections"][i] = dict(s, items=[P9[0]] + s["items"] + [P9[1]])
txt = tidy3.render(w, line)
old = finalize3.PKG3[w].read_text(encoding="utf-8-sig")
reg = {j: finalize3.call(f"td{T}_{w}_Rp2_{j}", finalize3.R.format(NAME=covjudge.NAME[w], OLD=old, NEW=txt), j) for j in ("g6", "g56")}
n = {k: sum(k in it.get("src", "新") for s in line["sections"] for it in s["items"]) for k in ("新", "补", "包3")}
line.update(sources=n, regression=reg, patched_back=["S08", "S09"])
(d / "final_line.json").write_text(json.dumps(line, ensure_ascii=False, indent=1), encoding="utf-8")
fin = json.loads((d / "final.json").read_text(encoding="utf-8"))
ann = finalize3.render(w, st, fin, fin["center"], with_annex=True, cov=fin["beads"])
(d / "final_line.txt").write_text(txt + "\n\n———\n来源：独立稿池子 " + str(n["新"]) + " 条，补缺 " + str(n["补"]) + " 条，包3 " + str(n["包3"])
                                  + " 条（同一条可同时计入两处）\n与包3 对照：" + "；".join(f"{j} {r.get('verdict')}" for j, r in reg.items())
                                  + "\n\n" + ann[ann.find("听感去处"):], encoding="utf-8")
print(w, "patched2 | sources", n, "| regression", {j: r.get("verdict") for j, r in reg.items()}, "| chars", len(txt), flush=True)
