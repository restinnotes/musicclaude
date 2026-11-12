"""10-30 evening (user, after w38: "提出理由……我感觉很僵硬啊"; "s1 到 s2 他这个过渡是不是自然……让段之间的过渡更为紧密";
"关系图不一定需要'推出'……某一个段内想要提之前的时候就直接去提 然后标一下引用"; "'仍在起作用'什么的还是很没用";
"还是可以压缩"; "覆盖率差不多就够了"). New form: no relation labels, no ⟲; when an item rests on something earlier it says
so in its own words and carries a citation (the bars of that earlier segment); each segment's first item picks up from where
the previous segment ended (no fresh start); compressed. Whole piece in one call (transitions need the whole view); beads not
shown (the content is taken from w38, which already explains them).
f3 (10-30 night, user: "压缩不是文言体……能用一句话说的东西不要拆成好几句"; "线的作用就是把整个珠子能串起来 所以只要能相关就行";
"1-3 他里面有好几条 你这个应该要说到具体是哪一条"; "没有让他加自然 人话"): P3 = plain speech, merge meanings not words, relate don't explain,
citations to the item (stored as because rel "引用", rendered inline by v6fix.view).
ids: fl_<w>_<out>.  usage: python v6flow.py <base> <out>  -> evaluations/v6fix/<w>_<out>.json/.md (+ graph for the judges)"""
import json, sys
import covjudge, draft10, evo, v6fix as V

P = """下面是肖邦{NAME}的一条“线”（Thread）：一个人在这首曲子里经历的一件事，按段写成条目。每段标了小节和他此刻与整件事（Center）的关系。
这条线会和另一批人写的听感记录并排展示：那些记录写此刻听到、感到的样子；线只负责用他自己的经历说出他此刻为什么会这样。

请把它改写一遍，内容沿用，改的是写法：
1. 去掉所有“提供理由 / 说明 / 限制 / 唤起 / 仍在起作用”之类的关系标签。某一条确实是因为前面某件事才这样，就在这句话里用他自己的话直接提到那件事（几个字就够，比如“想起刚开始只想多留一会儿”），并在 cite 里写那件事所在段的编号；只是主题相近、没有因果的，不提。前面的事此刻还在、但没有新变化的，不用写。
2. 段与段要接得上：每段开头，要让读的人看得出他为什么从上一段走到这里——是上一段的哪件事、哪个念头把他带到此刻。用自然的因果说出来，不要靠重复上一段最后一句话来衔接（“不再盼这一刻停下来，他……”“被……打动后，他……”这种），也不要写“这时”“接着”这类空连接词，不要每段重新起头。
3. 压缩：全文不超过 {N} 个字（现在是 {C} 个字）。只留每段真正推动他的那几件事：意思相近的合并，可有可无的删掉，不要靠把几句接成长句来凑。珠子的感受不必条条都有原因，大多数有着落就够了；但每段他为什么会这样，要说清。
4. 每条一句话，一个完整的想法，一般不超过四十个字，像一个人在讲自己的事；一段通常两三条；不写总结句、整齐的对照句、哲理句，不由作者替他宣布“他终于明白”；不写声音、画面、身体感受。
5. 用第三人称“他”；不新增线里没有的事件、人物、背景。段落、小节、每段与 Center 的关系都不变。

Center：{CENTER}

【现在的线】（方括号里是条目编号；← 后面是旧写法的关系标签，改写时去掉）
{LINE}

只输出 json：
```json
{{"segments": [{{"sec": "S01", "items": [{{"text": "……", "cite": []}}, {{"text": "……", "cite": ["S01"]}}]}}]}}
```"""


P3 = """下面是肖邦{NAME}的一条“线”（Thread）：一个人在这首曲子里经历的一件事，按段写成条目。每段标了小节和他此刻与整件事（Center）的关系。
这条线会和另一批人写的听感记录（珠子）放在一起读：珠子写此刻听到、感到的样子；线讲他自己的经历，作用是把这些听感串起来——
线的意思和珠子大体接近，让读的人感受到那是一种什么样的处境就够了，不必逐条去“解释”某一种感受。

请把这条线改写一遍，内容沿用，改的是写法：
1. 说人话：像一个人平平常常地讲自己的事，句子完整、自然，有主语，用口语。不要提纲式、电报式、文言式的短句，不要为了省字把话压紧。
   比如“不再揣摩回应，他自在关心对方，也喜欢自己不计较”就太像压缩过的提纲，应当说成一个人会说的话。
2. 压缩靠合并意思，不靠删字：一件事能用一句话说清的，不要拆成好几句；几条在说同一件事的，合成一条；可有可无的删掉。
   但一条只说一件事：不同的事分成不同的条，不要用分号或“；”把几件事串进一条长句。每条一句话，一般二三十字、最多五十字；一段通常两到四条。全文不超过 {N} 个字（现在是 {C} 个字），不用硬凑。
3. 去掉所有“提供理由 / 说明 / 限制 / 唤起 / 仍在起作用”之类的关系标签。某一条确实是因为前面某一条才这样，就在这句话里用平常话直接提到那件事，并在 cite 里写那一条的编号（见下面编号规则）；只是主题相近、没有因果的，不提；前面的事此刻还在、但没有新变化的，不用写。
4. 段与段要接得上：每段开头，让读的人看得出他为什么从上一段走到这里——是上一段的哪件事、哪个念头把他带到此刻。用自然的因果说出来，不要靠重复上一段最后一句话来衔接，也不要写“这时”“接着”这类空连接词，不要每段重新起头。
5. 不写总结句、整齐的对照句、哲理句，不由作者替他宣布“他终于明白”；不写声音、画面、身体感受；用第三人称“他”；不新增线里没有的事件、人物、背景。段落、小节、每段与 Center 的关系都不变。

编号规则：你写出的条目按顺序编号，第 1 段是 S01-1、S01-2……，第 2 段是 S02-1……；cite 只能写前面段落里你写出的条目编号。

Center：{CENTER}

【现在的线】（方括号里是旧条目编号，只供参考；← 后面是旧写法的关系标签，改写时去掉）
{LINE}

只输出 json：
```json
{{"segments": [{{"sec": "S01", "items": [{{"text": "……", "cite": []}}]}}, {{"sec": "S02", "items": [{{"text": "……", "cite": ["S01-2"]}}]}}]}}
```"""


def render(g, W):
    out = [f"# {W}｜线（新写法：不标关系，前文在句中直接提，〔〕里是出处小节）", "", f"**Center：**{g['center']}", ""]
    bars = {s["sec"]: s["bars"] for s in g["segments"]}
    for s in g["segments"]:
        out += [f"### {s['sec']}｜{s['bars']} 小节　（{s.get('relation')}）", ""]
        for it in s["items"]:
            c = "".join(f"〔{bars[x]}〕" for x in it.get("cite") or [] if x in bars and x != s["sec"])
            out.append(f"- {it['text']}{(' ' + c) if c else ''}")
        out.append("")
    return "\n".join(out)


def main(base, out):
    def piece(w):
        g = V.graph_of(w, base); segs = {s["id"]: s for s in draft10.segs(w)}
        C = sum(len(i["text"]) for s in g["segments"] for i in s["items"])
        rid = f"fl_{w}_{out}"
        if not evo.done(rid):
            evo.call(rid, (P3 if out >= "f3" else P).format(NAME=covjudge.NAME[w], N=int(C * (0.7 if out == "f1" else 0.6 if out == "f2" else 0.75) // 100 * 100), C=C, CENTER=g["center"],
                                   LINE=V.view(g, ids=True, center=False)), model=evo.G6, meta={"stage": "v6-flow"})
        e = V.parse(rid) or {}
        got = {s.get("sec"): s for s in e.get("segments") or []}
        G = {"center": g["center"], "segments": []}
        for s in g["segments"]:
            n = got.get(s["sec"])
            if not n or not n.get("items"):
                print(w, s["sec"], "没有结果，保留原样", flush=True); G["segments"].append(s); continue
            items = [{"id": f"{s['sec']}-{k}", "text": it["text"], "key": it["text"][:8], "follows": False, "explains": [],
                      "cite": [c for c in it.get("cite") or [] if isinstance(c, str)]} for k, it in enumerate(n["items"], 1)]
            seen = {it["id"] for x in G["segments"] for it in x["items"]}
            links = [{"from": c, "to": it["id"], "rel": "引用"} for it in items for c in it["cite"] if c in seen] if out >= "f3" else []
            G["segments"].append({"sec": s["sec"], "bars": s["bars"], "relation": s.get("relation"), "items": items, "because": links})
        rows = json.loads((V.OUT / f"{w}_{base}.json").read_text(encoding="utf-8"))["rows"]
        json.dump({"graph": G, "rows": rows, "base": f"{base} 新写法（不标关系、句中引用、段间衔接、压缩）"},
                  open(V.OUT / f"{w}_{out}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        W = "Op.60" if w == "op60" else "Op.61"
        (V.OUT / f"{w}_{out}.md").write_text((f"# {W}｜线（新写法：不标关系，前文在句中直接提，〔〕里是出处：小节和第几条）\n\n" + V.view(G)) if out >= "f3" else render(G, W), encoding="utf-8")
        print(w, out, "条目", sum(len(s["items"]) for s in G["segments"]), "字数", sum(len(i["text"]) for s in G["segments"] for i in s["items"]), f"（原 {C}）", flush=True)
    evo.run_parallel([(w, (lambda w=w: piece(w))) for w in ("op60", "op61")], 2)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
