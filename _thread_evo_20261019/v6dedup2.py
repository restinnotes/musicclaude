"""10-30 w32: w31 (this file's first prompt) cut the words (1437/1588) but lost v6's form: items merged into run-on sentences up to
108 chars joined by '；', arrows exploded (72/73 vs v6 26/31, up to 5 on one item), and some items said nothing alone
("他这回知道自己为什么迟疑", the reason left to the arrows). Same in-order pass from w24, plus v6's form as hard limits:
one item = one thing in one sentence of at most ~40 chars, merging means dropping the repeated part (not joining sentences),
each item readable without its arrows, at most one cross-segment arrow per item and usually two per segment, no body/sound/image.

10-30: w30 (plan causes -> write short) halved the length but lost coverage (Op.60 36/50 both judges vs w24 44/44) and got MORE
abstract (blind 人话 8:6 vs w24 12-14:0-2): compressing a segment into a few causes produces dense, abstract sentences.
Here: keep w24's concrete wording and only remove what is really waste — a cause already said in an earlier segment is not said
again (arrow instead), one thing split over several items is merged, half-sentences that only describe a feeling go. Written IN
ORDER, each segment seeing the new line so far; no beads shown. Each new item names the w24 items it comes from, and inherits
their bead claims. ids: dd_<w>_<sec>_<out>.  usage: python v6dedup.py <base> <out>"""
import json, os, sys
import covjudge, draft10, evo, v6fix as V

P = """下面是肖邦{NAME}的一条“线”（Thread，一个人在这首曲子里经历的一件事，按段写成关系图）。前面各段已经整理好了；请整理第 {SEC} 段（第 {BARS} 小节）。

这条线会和另一批人写的听感记录并排展示；线负责用他自己的经历说出他此刻为什么会这样。现在的问题是有些地方啰嗦。只删真正多余的东西：
- 前面各段已经说过的原因，这里又说了一遍的：删掉重述，条目里只留此刻新的东西；如果读者需要知道它接着前面哪一条，就加一个跨段箭头指回那一条（from 写它的编号，rel 取 提供理由、说明、限制、动摇、唤起、改写、失效、仍在起作用 之一）；
- 一件事被拆成了好几条的：合成一条——合并是删掉重复的部分，不是把几句用分号接成一长句；
- 只是在描写一种感受、画面、身体感觉，本身没说出原因的半句：删掉。
其余的尽量保留原话。不要为了短把话改得更概括、更抽象——具体的说法比概括的说法好；不新增内容；用第三人称“他”。

形式（和原来的 v6 一样）：
- 每条一句话，只说一件事，一般不超过四十个字；条数不超过这一段现在的条数；
- 每一条自己读就要能懂：他此刻在想什么、为什么。不要写成“他知道了为什么”而把原因全留给箭头；
- 箭头只给读者真正需要的前因：一条最多一个跨段箭头，一段一般不超过两个；拿不准的就不连。条目前的 → 表示由上一条引出（follows: true）。
这一段他和整件事的关系：{REL}。

【已经整理好的前面各段】（方括号里是条目编号）
{PREV}

【第 {SEC} 段现在的样子】（方括号里是条目编号）
{CUR}

只输出 json，每一条用 src 写它来自现在这一段的哪几条：
```json
{{"items": [{{"id": "{SEC}-1", "text": "……", "key": "两到八个字，取自这一条原文", "follows": false, "src": ["{SEC}-1", "{SEC}-2"]}}],
 "because": [{{"from": "S02-3", "to": "{SEC}-1", "rel": "提供理由"}}]}}
```"""


def main(base, out):
    def piece(w):
        g = V.graph_of(w, base); segs = {s["id"]: s for s in draft10.segs(w)}
        done = {"center": g["center"], "segments": []}; rows = json.loads((V.OUT / f"{w}_{base}.json").read_text(encoding="utf-8"))["rows"]
        for s in g["segments"]:
            sec = s["sec"]; old = {it["id"]: it for it in s["items"]}
            # earlier-segment arrows of the current segment point at base ids; show them by text so the model can re-point them
            prev = V.view(done, ids=True, center=False) if done["segments"] else "（这是第一段）"
            cur = V.view({"center": "", "segments": [s]}, ids=True, center=False, head=False)
            rid = f"dd2_{w}_{sec}_{out}"
            if not evo.done(rid):
                evo.call(rid, P.format(NAME=covjudge.NAME[w], SEC=sec, BARS=s["bars"], REL=s.get("relation"), PREV=prev, CUR=cur),
                         model=evo.G6, meta={"stage": "v6-dedup2"})
            e = V.parse(rid) or {}
            if not isinstance(e.get("items"), list) or not e["items"]:
                print(w, sec, "没有结果，保留原样", flush=True); done["segments"].append(s); V.tidy(done); continue
            ns = V.seg_graph(e, sec, segs[sec]); ns["relation"] = s.get("relation")
            for it, raw in zip(ns["items"], e["items"]):
                it["explains"] = sorted({b for i in raw.get("src") or [] for b in old.get(i, {}).get("explains", [])})
            done["segments"].append(ns); V.tidy(done)
            print(f"{w} {sec}: {len(s['items'])} 条 → {len(ns['items'])} 条 | {sum(len(x['text']) for x in s['items'])} 字 → "
                  f"{sum(len(x['text']) for x in ns['items'])} 字 | 箭头 {len(s['because'])} → {len(ns['because'])}", flush=True)
        json.dump({"graph": done, "rows": rows, "base": f"{base} 去重复（守 v6 形式）"}, open(V.OUT / f"{w}_{out}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        (V.OUT / f"{w}_{out}.md").write_text(f"# {'Op.60' if w == 'op60' else 'Op.61'}｜关系图（在 v6 上修补，{out}）\n\n" + V.view(done), encoding="utf-8")
    evo.run_parallel([(w, (lambda w=w: piece(w))) for w in ("op60", "op61")], 2)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
