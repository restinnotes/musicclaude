"""10-31 (user: the line reads like blind back-and-forth in a maze — "一会关心一会又放下" — not like DFS, where each way is
followed to its end, found not to work for a reason, and that knowledge is carried back into the next try; "去再修一版你
认为更好的"). Rewrite of the new-form line (f5) so the exploration shows: each stage he tries a way of living with the Center,
finds where it stops working (or what it gives him), and takes that into the next; a return to an earlier place says what
is different now; "又" only for real returns; 没在想 segments are lived in, not deliberated; no closing list of principles;
pure self-calibration items with nothing new are dropped. Also the line-alone judges' remaining notes on f5. Beads not shown.
ids: df_<w>_<out>.  usage: python v6dfs.py <base> <out>"""
import json, sys
import covjudge, evo, v6fix as V

P = """下面是肖邦{NAME}的一条“线”（Thread）：一个人在这首曲子里经历的一件事，按段写成条目，每段标了小节和他此刻与整件事（Center）的关系。线会和听感记录放在一起读，作用是把那些听感串起来；它自己也要读得通。

现在的问题：读起来像在迷宫里盲走——一会儿关心，一会儿放下，一会儿又在意，同一个两难来回调。其实细看，他每一段多半是在试一种新的办法、碰到新的限制；只是写法把“又回到原处”摆在了前面，把“这次学到了什么”埋掉了。
请改写成一场有方向的探索，像沿着一条路走到头、确认为什么走不通、带着这个认识退回来再试下一条：
1. 每一个阶段，读者要看得出：他这回在试什么办法（怎样对待这份关系、怎样对待自己），走下去发现了什么——它在哪里不管用了，或者给了他什么——然后带着这个进入下一段。不要用“试”“发现”这种标签，用他自己的话说出来。
2. 回到以前到过的地方时，要说出这次和上次哪里不一样、他现在多知道了什么；“又”只用在真的回到原处的时候。
3. 只在给自己定规矩、却没有新认识的条目（例如“他不把对方的温柔当成暗示，也不根据回应多少决定要不要关心”这种），删掉或并进别处。
4. 标“没在想”的段落，他是真的没在权衡：写他沉在什么里、在做什么，前因照样要接得上，但不要替他想道理。
5. 结尾不要收成一串原则（不催、不押、不判……），而是写他走到这里时，手里实际剩下了什么、还不知道什么。
6. 下面这些是只读线的评委对现在这一版指出的缺口，改写时一并补上：
{NOTES}

写法不变：像一个人平平常常讲自己的事，句子完整自然、用口语；一条只说一件事，一般二三十字、最多五十字，一段通常两到四条；某条因为前面某一条才这样，就在句子里直接提，并在 cite 写那一条的编号；不用关系标签；不写声音、画面、身体感受；不新增线里没有的事件、人物、背景；第三人称“他”。段落、小节、每段与 Center 的关系都不变。全文不超过 {N} 个字。
编号规则：条目按你写出的顺序编号，第 1 段是 S01-1、S01-2……；cite 只能写前面段落里你写出的条目编号。

Center：{CENTER}

【现在的线】（方括号里是条目编号，〔〕里是引用的前文）
{LINE}

只输出 json（全部段落）：
```json
{{"segments": [{{"sec": "S01", "items": [{{"text": "……", "cite": []}}]}}]}}
```"""


ANCHOR = """
另外，这一版有一个大问题必须改：Center 里的“旧梦”和“向外行动”被改窄了。现在的线把旧梦写成了“亲近别人、重新靠近人”，把向外行动写成了“眼前的事”，读起来像一个人忙于做事、没空交朋友——这不是原意。
按原来那一版（v6）的意思：
- 旧梦是他曾真心相信过的一种生活：人与人不必时时防备，珍贵的东西不必靠争夺才能留下；不必反复证明自己值得被爱、被接纳，付出可以只因喜欢，靠近也不必先做好受伤的准备。这样的相信确实给过他快乐。“亲近”只是其中一面，不要把旧梦缩成“亲近别人”。
- 向外行动是他先认下自己能做的那一份、去争取；他当初不肯再等，是不愿看着重要的东西继续受损——光靠怀念改变不了让那种生活难以存在的事情。
- 两者的牵制：为了护住那种生活而去争取，争取本身又可能把温柔耗尽，最后只剩意志；只守着那份安宁，又护不住正在受损的东西。
请把全线里“亲近别人 / 靠近别人 / 眼前的事”这类窄化的说法，按上面的意思改回来；其余的结构（每一步试什么、在哪里走不通、带走什么）保留。下面附原来那一版作参照，只用来对齐“旧梦”和“向外行动”指什么，不要照抄它的句子。

【原来那一版（v6），只作参照】
{V6}
"""


def main(base, out, only=None):
    al = json.loads((V.OUT / f"alone_{base}.json").read_text(encoding="utf-8"))

    def piece(w):
        g = V.graph_of(w, base); bars = {s["sec"]: s["bars"] for s in g["segments"]}
        notes = [f"- {x[0]}（{bars.get(x[0], '')} 小节）：{x[2]}" for k, v in al.items() if k.startswith(w) for x in v.get("weak_secs") or []]
        notes += [f"- 整体：{v.get('main_problem', '')}" for k, v in al.items() if k.startswith(w)]
        C = sum(len(i["text"]) for s in g["segments"] for i in s["items"])
        rid = f"df_{w}_{out}"
        if not evo.done(rid):
            evo.call(rid, P.format(NAME=covjudge.NAME[w], NOTES="\n".join(notes), N=int(C * 1.05 // 100 * 100), CENTER=g["center"],
                                   LINE=V.view(g, ids=True, center=False)), model=evo.G6, meta={"stage": "v6-dfs"})
        e = V.parse(rid) or {}
        got = {s.get("sec"): s for s in e.get("segments") or []}
        G = {"center": g["center"], "segments": []}
        for s in g["segments"]:
            n = got.get(s["sec"])
            if not n or not n.get("items"):
                print(w, s["sec"], "没有结果，保留原样", flush=True); G["segments"].append(json.loads(json.dumps(s))); continue
            seen = {it["id"] for x in G["segments"] for it in x["items"]}
            items = [{"id": f"{s['sec']}-{k}", "text": it["text"], "key": it["text"][:8], "follows": False, "explains": [],
                      "cite": [c for c in it.get("cite") or [] if isinstance(c, str)]} for k, it in enumerate(n["items"], 1)]
            links = [{"from": c, "to": it["id"], "rel": "引用"} for it in items for c in it["cite"] if c in seen]
            G["segments"].append({"sec": s["sec"], "bars": s["bars"], "relation": s.get("relation"), "items": items, "because": links})
        rows = json.loads((V.OUT / f"{w}_{base}.json").read_text(encoding="utf-8"))["rows"]
        json.dump({"graph": G, "rows": rows, "base": f"{base} 改成有方向的探索"}, open(V.OUT / f"{w}_{out}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        W = "Op.60" if w == "op60" else "Op.61"
        (V.OUT / f"{w}_{out}.md").write_text(f"# {W}｜线（新写法：不标关系，前文在句中直接提，〔〕里是出处：小节和第几条）\n\n" + V.view(G), encoding="utf-8")
        T = [i["text"] for s in G["segments"] for i in s["items"]]
        print(w, out, "条目", len(T), "字数", sum(map(len, T)), f"（原 {C}）", "含“又”", sum("又" in t for t in T), flush=True)
    evo.run_parallel([(w, (lambda w=w: piece(w))) for w in ("op60", "op61")], 2)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3].split(",") if len(sys.argv) > 3 else None)
