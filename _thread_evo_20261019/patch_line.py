"""Put named segments of the tidied line back to their merged-round version (both judges had found those not worse than
package 3), then re-run the package-3 comparison. usage: python patch_line.py <T> <work> <merged-file> <tag> S08 S09 ...
-> final_line.json / final_line.txt rewritten (the pre-patch files are kept as final_line_<tag>_before.*)"""
import json, shutil, sys
import covjudge, finalize3, tidy3

T, w, merged, tag, secs = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], set(sys.argv[5:])
d, st = finalize3.load(T, w)
for ext in ("json", "txt"):
    shutil.copy(d / f"final_line.{ext}", d / f"final_line_{tag}_before.{ext}")
line = json.loads((d / "final_line.json").read_text(encoding="utf-8"))
m = {s["sec"]: s for s in json.loads((d / merged).read_text(encoding="utf-8"))["sections"]}
for i, s in enumerate(line["sections"]):
    if s["sec"] in secs:
        items = []
        for it in m[s["sec"]]["items"]:
            src = "包3" if it["feel"].startswith("（包3）") or it.get("src") == "包3" else it.get("src", "新")
            items.append({"feel": it["feel"].replace("（包3）", "").replace("（补）", ""), "why": it["why"], "src": src})
        line["sections"][i] = dict(m[s["sec"]], items=items, label=s.get("label"))
txt = tidy3.render(w, line)
old = finalize3.PKG3[w].read_text(encoding="utf-8-sig")
reg = {j: finalize3.call(f"td{T}_{w}_R{tag}_{j}", finalize3.R.format(NAME=covjudge.NAME[w], OLD=old, NEW=txt), j) for j in ("g6", "g56")}
n = {k: sum(k in it.get("src", "新") for s in line["sections"] for it in s["items"]) for k in ("新", "补", "包3")}
line.update(sources=n, regression=reg, patched_back=sorted(secs))
(d / "final_line.json").write_text(json.dumps(line, ensure_ascii=False, indent=1), encoding="utf-8")
fin = json.loads((d / "final.json").read_text(encoding="utf-8"))
ann = finalize3.render(w, st, fin, fin["center"], with_annex=True, cov=fin["beads"])
(d / "final_line.txt").write_text(txt + "\n\n———\n来源：独立稿池子 " + str(n["新"]) + " 条，补缺 " + str(n["补"]) + " 条，包3 " + str(n["包3"])
                                  + " 条（同一条可同时计入两处）\n与包3 对照：" + "；".join(f"{j} {r.get('verdict')}" for j, r in reg.items())
                                  + "\n\n" + ann[ann.find("听感去处"):], encoding="utf-8")
print(w, "patched", sorted(secs), "| sources", n, "| regression", {j: r.get("verdict") for j, r in reg.items()}, "| chars", len(txt), flush=True)
