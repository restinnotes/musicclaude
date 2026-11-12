"""Generic verbatim patch (10-27): for every segment a judge named as worse than package 3 in final_line.json, add package
3's own bullets of that segment that the line does not yet contain (verbatim; bullet -> feel, its "→" line -> why; counted
as 包3; nothing newly written). Then the package-3 comparison again. usage: python patch3.py <T> <work> <tag>"""
import json, re, shutil, sys
import covjudge, finalize3, tidy3


def pkg3_bullets(w):
    t = finalize3.PKG3[w].read_text(encoding="utf-8-sig"); out = {}
    for blk in re.split(r"\n(?=S\d\d ｜)", t):
        m = re.match(r"(S\d\d) ｜", blk)
        if not m:
            continue
        items = []
        for line in blk.splitlines():
            if line.startswith("• "):
                items.append({"feel": line[2:].strip(), "why": "", "src": "包3"})
            elif line.startswith("→ ") and items:
                items[-1]["why"] = (items[-1]["why"] + " " + line[2:].strip()).strip()
        out[m.group(1)] = items
    return out


T, w, tag = sys.argv[1], sys.argv[2], sys.argv[3]
d, st = finalize3.load(T, w)
shutil.copy(d / "final_line.json", d / f"final_line_{tag}_before.json")
line = json.loads((d / "final_line.json").read_text(encoding="utf-8"))
worse = {x["sec"] for r in (line.get("regression") or {}).values() if "退步" in str(r.get("verdict")) for x in r.get("worse") or []}
pk = pkg3_bullets(w); added = 0
for s in line["sections"]:
    if s["sec"] in worse:
        have = " ".join(it["feel"] + it.get("why", "") for it in s["items"])
        new = [b for b in pk.get(s["sec"], []) if b["feel"][:15] not in have]
        s["items"] += new; added += len(new)
txt = tidy3.render(w, line)
old = finalize3.PKG3[w].read_text(encoding="utf-8-sig")
reg = {j: finalize3.call(f"td{T}_{w}_R{tag}_{j}", finalize3.R.format(NAME=covjudge.NAME[w], OLD=old, NEW=txt), j) for j in ("g6", "g56")}
n = {k: sum(k in it.get("src", "新") for s in line["sections"] for it in s["items"]) for k in ("新", "补", "包3")}
line.update(sources=n, regression=reg, patched_back=sorted(worse))
(d / "final_line.json").write_text(json.dumps(line, ensure_ascii=False, indent=1), encoding="utf-8")
fin = json.loads((d / "final.json").read_text(encoding="utf-8"))
ann = finalize3.render(w, st, fin, fin["center"], with_annex=True, cov=fin["beads"])
(d / "final_line.txt").write_text(txt + "\n\n———\n来源：独立稿池子 " + str(n["新"]) + " 条，补缺 " + str(n["补"]) + " 条，包3 " + str(n["包3"])
                                  + " 条（同一条可同时计入两处）\n与包3 对照：" + "；".join(f"{j} {r.get('verdict')}" for j, r in reg.items())
                                  + "\n\n" + ann[ann.find("听感去处"):], encoding="utf-8")
print(w, f"patched3 {sorted(worse)} +{added} | sources", n, "| regression", {j: r.get("verdict") for j, r in reg.items()}, "| chars", len(txt), flush=True)
