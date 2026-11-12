"""10-30 night: targeted fix of a new-form line (v6flow f4) from the line-alone judges only: the segments they called 勉强 /
不成立, with their one-line reason, plus each judge's main problem. Only those segments change; every other segment must
come back word for word (checked; a changed untouched segment is reverted). Same new form (plain speech, one thing per item,
in-sentence mention + item-level cite, no labels). Beads not shown.
ids: ff_<w>_<out>.  usage: python v6flowfix.py <base> <out>"""
import json, sys
import covjudge, evo, v6fix as V

P = """下面是肖邦{NAME}的一条“线”（Thread）：一个人在这首曲子里经历的一件事，按段写成条目。线会和听感记录放在一起读，作用是把那些听感串起来；它自己也要读得通：每段他为什么会这样，前因在线里看得出来。
写法已经定了：像一个人平平常常讲自己的事，句子完整自然、用口语；一条只说一件事，一般二三十字、最多五十字；某条因为前面某一条才这样，就在句子里直接提，并在 cite 写那一条的编号；不用关系标签；不写声音、画面、身体感受；不新增事件、人物、背景；第三人称“他”。

两位评委只读这条线（不看听感记录），指出下面几段的来龙去脉还不够顺：
{NOTES}

评委对整条线的主要意见：
{MAIN}

请只改上面点到的段落，把缺的那一步前因补上、把前后说法对齐（例如同一件事前后的说法要一致）；能并进现有条目就并，不要为了补前因写成长句。没点到的段落一字不改，照原样输出。
编号规则：条目按顺序编号，第 1 段是 S01-1、S01-2……；cite 只能写前面段落里的条目编号。

Center：{CENTER}

【现在的线】（方括号里是条目编号，〔〕里是引用的前文）
{LINE}

只输出 json（全部段落都要输出）：
```json
{{"segments": [{{"sec": "S01", "items": [{{"text": "……", "cite": []}}]}}]}}
```"""


def main(base, out, hand=None):
    H = json.loads(open(hand, encoding="utf-8").read()) if hand else None    # 10-31: notes written by hand {w: {sec: note}}

    def piece(w):
        g = V.graph_of(w, base)
        notes, main = {}, []
        if H is not None:
            notes = {sec: [x] for sec, x in (H.get(w) or {}).items()}; main = ["- （只改上面点到的段）"]
            if not notes:
                print(w, out, "没有要改的段，照抄", flush=True)
        else:
            al = json.loads((V.OUT / f"alone_{base}.json").read_text(encoding="utf-8"))
            for k, v in al.items():
                if k.startswith(w):
                    for x in v.get("weak_secs") or []:
                        notes.setdefault(x[0], []).append(f"{x[1]}：{x[2]}")
                    main.append(f"- {v.get('main_problem', '')}")
        bars = {s["sec"]: s["bars"] for s in g["segments"]}
        nt = "\n".join(f"- {sec}（{bars.get(sec, '')} 小节）：" + "；".join(xs) for sec, xs in sorted(notes.items()))
        rid = f"ff_{w}_{out}"
        if notes and not evo.done(rid):
            evo.call(rid, P.format(NAME=covjudge.NAME[w], NOTES=nt, MAIN="\n".join(main), CENTER=g["center"], LINE=V.view(g, ids=True, center=False)),
                     model=evo.G6, meta={"stage": "v6-flowfix"})
        e = V.parse(rid) or {}
        got = {s.get("sec"): s for s in e.get("segments") or []}
        G = {"center": g["center"], "segments": []}; reverted = []
        for s in g["segments"]:
            n = got.get(s["sec"])
            if not n or not n.get("items") or (s["sec"] not in notes and [i["text"] for i in n["items"]] != [i["text"] for i in s["items"]]):
                if n and s["sec"] not in notes:
                    reverted.append(s["sec"])
                G["segments"].append(json.loads(json.dumps(s))); continue
            seen = {it["id"] for x in G["segments"] for it in x["items"]}
            items = [{"id": f"{s['sec']}-{k}", "text": it["text"], "key": it["text"][:8], "follows": False, "explains": [],
                      "cite": [c for c in it.get("cite") or [] if isinstance(c, str)]} for k, it in enumerate(n["items"], 1)]
            links = [{"from": c, "to": it["id"], "rel": "引用"} for it in items for c in it["cite"] if c in seen]
            G["segments"].append({"sec": s["sec"], "bars": s["bars"], "relation": s.get("relation"), "items": items, "because": links})
        V.tidy(G)
        rows = json.loads((V.OUT / f"{w}_{base}.json").read_text(encoding="utf-8"))["rows"]
        json.dump({"graph": G, "rows": rows, "base": f"{base} 按单独读意见补过渡"}, open(V.OUT / f"{w}_{out}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        W = "Op.60" if w == "op60" else "Op.61"
        (V.OUT / f"{w}_{out}.md").write_text(f"# {W}｜线（新写法：不标关系，前文在句中直接提，〔〕里是出处：小节和第几条）\n\n" + V.view(G), encoding="utf-8")
        print(w, out, "改的段", sorted(notes), "未点到却被改、已还原", reverted, "字数", sum(len(i["text"]) for s in G["segments"] for i in s["items"]), flush=True)
    evo.run_parallel([(w, (lambda w=w: piece(w))) for w in ("op60", "op61")], 2)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
