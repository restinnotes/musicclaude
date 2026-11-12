"""Final tidy (10-27): the merged line is complete but long and repetitive (package-3 items overlapping each other and the
new ones; one fill item in the first person). Per piece:
T (g6): within each segment drop an item whose mechanism another item already fully carries (keep the more concrete one),
   join items that say the same thing by deleting words only, 我->他, at most 4 items, keep every distinct mechanism and
   the source tags (新 / 补 / 包3);
K (g56): compare before/after per segment, list segments that lost a mechanism -> those segments fall back to before;
R (g6, g56): non-regression against package 3 once more.
usage: THREAD_ROUTE=gpt3s THREAD_ROUTE_G56=mimic python tidy3.py <T> <work> <merged-file>  -> final_line.{json,txt}"""
import json, sys
import covjudge, finalize3

TT = """下面是肖邦{NAME}的一条 Thread 定稿前的版本。它完整，但太长、有重复：同一段里几条说的是同一件事，或者一条已经被另一条完全包含。

请整理每一段：
1. 一条的机制已经被另一条完全说到时，删掉较空泛的那条，保留更具体的那条；
2. 两条说的是同一件事时，合成一条，只许删字和调换原句顺序，不许换成新的说法；
3. 第一人称“我”改成“他”；
4. 每一段最多 4 条；每一种不同的机制都要留下（宁可多一条，也不要丢掉一个原因）；
5. 保留每条的来源 src（新 / 补 / 包3）；两条合并时 src 写成两者，例如 "新+包3"；
6. label（还说不清 / 正在面对 / 没在想）和 Center 不改。

【定稿前】
{TEXT}

只输出 json：
```json
{{"sections": [{{"sec": "S01", "label": "还说不清", "items": [{{"feel": "……", "why": "……", "src": "新"}}]}}]}}
```"""
KK = """下面是一条 Thread 每段整理前后的对照。请逐段判断：整理后是否丢掉了整理前有的某一种机制（某个原因、某个前因，或某种感受的来源）？只删重复、合并同义不算丢。

{PAIRS}

只输出 json：
```json
{{"lost": [{{"sec": "S03", "what": "……"}}]}}
```"""


def items_text(s):
    return "\n".join(f"- [{it.get('src', '新')}] {it['feel']} → {it['why']}" for it in s["items"])


def run(T, w, merged):
    d, st = finalize3.load(T, w)
    m = json.loads((d / merged).read_text(encoding="utf-8"))
    for s in m["sections"]:
        for it in s["items"]:
            if it["feel"].startswith("（包3）"):
                it["feel"] = it["feel"][4:]; it["src"] = "包3"
            if it.get("feel", "").startswith("（补）"):
                it["feel"] = it["feel"][3:]
        added = [c for c in (st.get(s["sec"]) or {}).get("chosen") or [] if c.get("added")]
        for it in s["items"]:                      # fill items are the 补 ones the product marked; tag them by text
            if any(it["why"][:12] in c["text"] for c in added):
                it["src"] = "补"
    text = f"Center：{m['center']}\n\n" + "\n\n".join(f"### {s['sec']}（{s.get('label', '')}）\n{items_text(s)}" for s in m["sections"])
    t = finalize3.call(f"td{T}_{w}_T", TT.format(NAME=covjudge.NAME[w], TEXT=text), "g6")
    before = {s["sec"]: s for s in m["sections"]}
    pairs = "\n\n".join(f"### {s['sec']}\n【整理前】\n{items_text(before[s['sec']])}\n【整理后】\n{items_text(s)}" for s in t["sections"] if s["sec"] in before)
    k = finalize3.call(f"td{T}_{w}_K", KK.format(PAIRS=pairs), "g56")
    lost = {x["sec"] for x in k.get("lost") or []}
    secs = [before[s["sec"]] if s["sec"] in lost else dict(s, label=before.get(s["sec"], s).get("label", s.get("label"))) for s in t["sections"]]
    final = {"sections": secs, "center": m["center"]}
    txt = render(w, final)
    reg = {j: finalize3.call(f"td{T}_{w}_R_{j}", finalize3.R.format(NAME=covjudge.NAME[w], OLD=finalize3.PKG3[w].read_text(encoding="utf-8-sig"), NEW=txt), j)
           for j in ("g6", "g56")}
    n = {k2: sum(k2 in it.get("src", "新") for s in secs for it in s["items"]) for k2 in ("新", "补", "包3")}
    fin = json.loads((d / "final.json").read_text(encoding="utf-8"))
    out = dict(final, sources=n, reverted_segments=sorted(lost), regression=reg, coverage_before_merge=fin.get("coverage"))
    (d / "final_line.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    ann = finalize3.render(w, st, fin, fin["center"], with_annex=True, cov=fin["beads"])
    (d / "final_line.txt").write_text(txt + "\n\n———\n来源：独立稿池子 " + str(n["新"]) + " 条，补缺 " + str(n["补"]) + " 条，包3 " + str(n["包3"])
                                      + " 条（同一条可同时计入两处）\n与包3 对照："
                                      + "；".join(f"{j} {r.get('verdict')}" for j, r in reg.items()) + "\n\n" + ann[ann.find("听感去处"):], encoding="utf-8")
    print(w, "tidy: sources", n, "| reverted", sorted(lost), "| regression", {j: r.get("verdict") for j, r in reg.items()},
          "| chars", len(txt), flush=True)


def render(w, f):
    segs = {x["id"]: x for x in finalize3.draft10.segs(w)}
    out = ["肖邦" + covjudge.NAME[w], f"Center：{f['center']}", ""]
    for s in f["sections"]:
        x = segs[s["sec"]]
        out += [f"{s['sec']} ｜ {x['start']}–{x['end']}小节 ｜ {s.get('label', '')}", ""]
        for it in s["items"]:
            tag = "" if it.get("src", "新") == "新" else f"〔{it['src']}〕"
            out += [f"• {it['feel']}{tag}"] + ([f"  → {it['why']}"] if it.get("why") else [])
        out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2], sys.argv[3])
