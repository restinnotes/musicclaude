"""Non-regression merge (PLAN_20261026.md step 6, 10-27). Both judges found the pool-only line clearer on the long-range
structure but missing local, moment-to-moment mechanisms the 10-25 package-3 line already had (sudden intrusions felt in
the body first, a breath that already senses leaving, holding oneself up making the longing sharper, ...). The plan says a
new line must not lose what an old one explained. So, per piece, one call:
M (g6): keep every new item as it is; where the judges named a lost package-3 mechanism for a segment, add that mechanism
   as one item in package-3's own words (lightly shortened), marked src=包3; no reason that neither version has; choose
   the Center between new and old with a reason;
R2 (g6, g56): the same non-regression comparison again, now merged vs package 3.
Items taken from package 3 are counted apart in the product (they are not from the bead-free pool).
usage: THREAD_ROUTE=gpt3s THREAD_ROUTE_G56=mimic python merge3.py <T> <work>  -> evaluations/synth/<T>_<work>/merged.*"""
import json, sys
import covjudge, evo, finalize3

M = """下面是肖邦{NAME}的两版 Thread，以及两位评委逐段比较后指出的、新版丢掉的旧版机制。

请合成最终版：
1. 新版每一段的每一条都原样保留（feel / why 不改字）。
2. 新版里标“（包3）”的条目也原样保留，并继续标 "src": "包3"。评委指出旧版在某一段有新版丢掉的具体机制时，把旧版那一层作为一条加到这一段：用旧版原话（可以删去铺陈，不换成概括词），写成 feel 一句、why 一两句，标 "src": "包3"。只加评委点名丢掉、而且确实能解释此刻感受的那一层；不要把旧版整段搬过来。
3. 新旧两条如果互相矛盾，保留更能解释“为什么此刻会这样”的那一条，在 note 里说明。评委指出新版把旧版已经说具体的同一个机制改写得更抽象（例如用“已有的满足”“全部需要”“这一部分”代替实际的处境）时，用旧版的具体说法替换新版那一条，标 "src": "包3"。
4. 不要加两版都没有的理由。
5. 从新版 Center 和旧版 Center 里选一个作为最终 Center（可以把两句合成一句，但不能加新内容），说明理由。

【新版】
{NEW}

【旧版】
{OLD}

【评委指出的新版丢失】
{LOST}

只输出 json：
```json
{{"sections": [{{"sec": "S01", "label": "还说不清", "items": [{{"feel": "……", "why": "……", "src": "新", "note": ""}}]}}], "center": "……", "center_why": "……"}}
```"""


def run(T, w, rnd=1):
    d, st = finalize3.load(T, w)
    fin = json.loads((d / "final.json").read_text(encoding="utf-8"))
    base = fin if rnd == 1 else json.loads((d / ("merged.json" if rnd == 2 else f"merged{rnd - 1}.json")).read_text(encoding="utf-8"))
    # round 2+: the previous merge is the new version; its （包3） marks stay in the text so they keep being counted
    new = finalize3.render(w, st, base, base["center"], with_annex=False)
    old = finalize3.PKG3[w].read_text(encoding="utf-8-sig")
    lost = "\n".join(f"{j}·{x['sec']}：{x['lost']}" for j, r in (base.get("regression") or {}).items() for x in r.get("worse") or [])
    sfx = "" if rnd == 1 else str(rnd)
    m = finalize3.call(f"mg{T}_{w}_M{sfx}", M.format(NAME=covjudge.NAME[w], NEW=new, OLD=old, LOST=lost), "g6")
    st_m = {s["sec"]: st.get(s["sec"]) or {} for s in m["sections"]}
    # render: new items keep their arrows by position; 包3 items are marked and carry no pool arrows
    for s in m["sections"]:
        for it in s["items"]:
            if it.get("src") == "包3" or it["feel"].startswith("（包3）"):
                it["src"] = "包3"; it["feel"] = "（包3）" + it["feel"].replace("（包3）", "")
            it["text"] = f"感受：{it['feel']} 为什么：{it['why']}"
        s["items"] = [it for it in s["items"] if it.get("src") != "包3"] + [it for it in s["items"] if it.get("src") == "包3"]
    txt = finalize3.render(w, st_m, m, m["center"], with_annex=False)
    reg = {j: finalize3.call(f"mg{T}_{w}_R{sfx}_{j}", finalize3.R.format(NAME=covjudge.NAME[w], OLD=old, NEW=txt), j) for j in ("g6", "g56")}
    n_old = sum(it.get("src") == "包3" for s in m["sections"] for it in s["items"])
    out = {"T": T, "work": w, "center": m["center"], "center_why": m.get("center_why"), "sections": m["sections"],
           "items_from_pkg3": n_old, "regression": reg, "coverage_before_merge": fin.get("coverage")}
    (d / f"merged{sfx}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    ann = finalize3.render(w, st, fin, fin["center"], with_annex=True, cov=fin["beads"])
    annex = ann[ann.find("———"):] if "———" in ann else ""
    (d / f"merged{sfx}.txt").write_text(txt + "\n\n" + annex + f"\n\n来自包3 的条目：{n_old} 条（标“（包3）”，不来自不看珠子的独立稿）\n"
                                  + "与包3 对照：" + "；".join(f"{j} {r.get('verdict')}" for j, r in reg.items()), encoding="utf-8")
    print(w, f"merged{sfx}: pkg3 items", n_old, "| regression", {j: r.get("verdict") for j, r in reg.items()}, flush=True)


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 1)
