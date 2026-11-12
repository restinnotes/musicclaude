"""10-30 w34 (w33 aborted after 6 segments: "one thing per item" made it chop items into fragments, Op.60 S04 3 -> 11 items;
now: one complete thought per item, 20-45 chars, at most v6's item count for the segment).
10-30 w33: w31 (in-order dedup of w24) kept coverage (Op.60 41/40, Op.61 50/46, checklist 0 lost) and won 啰嗦/人话 against v6
(11-14 : 0-2), but 3/4 blind judges still preferred v6: 9-10 "lost" each, concentrated in the late segments (the closing insights
were cut thin). Its form also drifted from v6 (run-on items up to 108 chars, 72/73 arrows), and Op.61 still retold beads
(pure retell 5-8 items, own reasons 11-13/38).
Here, per segment with notes: give back the content the blind judges named as lost (both judges, union), in short plain items;
turn items flagged as pure bead retelling into his own reason (or drop them when the reason is already in the line); and hold
v6's form (one thing per item, ~40 chars, at most one cross-segment arrow per item). Beads are NOT shown.
Written IN ORDER (each segment sees the changed earlier ones). Segments without notes still get the form pass only when they break the form (an item over 60 chars or >1 arrow on an item).
ids: rs_<w>_<sec>_<out>.  usage: python v6restore.py <base> <out>"""
import json, sys
import covjudge, draft10, evo, v6fix as V

P = """下面是肖邦{NAME}的一条“线”（Thread，一个人在这首曲子里经历的一件事，按段写成关系图）。请修改第 {SEC} 段（第 {BARS} 小节）。

这条线会和另一批人写的听感记录并排展示：那些记录写此刻听到、感到的样子；线只负责用他自己的经历说出他此刻为什么会这样。只读这条线也要能读通。
我们的目标是用最少的、像人说话的句子，把每段他为什么这样说清楚。
{TASKS}
形式（和原来的 v6 一样）：
- 用第三人称“他”；每条是一个完整的想法：他想到什么、为什么，连同它此刻带来的变化，写成一句话，一般二十到四十五个字；
- 不要用分号把好几件事接成一长句，也不要把一个想法拆成好几条碎句；这一段最多 {MAXN} 条（原来的 v6 这一段是 {MAXN} 条）；
- 每一条自己读就要能懂：他此刻在想什么、为什么；不要把原因全留给箭头；
- 前面各段已经说过的原因不要再说一遍；读者需要知道它接着前面哪一条时，加一个跨段箭头（from 写它的编号，rel 取 提供理由、说明、限制、动摇、唤起、改写、失效、仍在起作用 之一）。一条最多一个跨段箭头，一段一般不超过两个；拿不准的就不连；
- 由上一条直接引出的，follows 写 true；
- 不写声音、画面、身体感受的描写；不写总结句、整齐的对照句，不由作者替他宣布“他终于明白”；
- 其余的保留原话，具体的说法比概括的说法好；不新增前史、外部事件、人物。
这一段他和整件事的关系：{REL}。

【线已经改好的前面各段】（方括号里是条目编号）
{LINE}

【第 {SEC} 段现在的样子】
{CUR}

只输出 json，每一条用 src 写它来自现在这一段的哪几条（新补的写 []）：
```json
{{"items": [{{"id": "{SEC}-1", "text": "……", "key": "两到八个字，取自这一条原文", "follows": false, "src": ["{SEC}-1"]}}],
 "because": [{{"from": "S02-3", "to": "{SEC}-1", "rel": "提供理由"}}]}}
```"""

T_LOST = """
1. 两位评委把这一段和原来的 v6 比，指出下面这些 v6 说清了、现在这一段丢了或说薄了的内容。请找回来：用他自己的平常话，写成短句，能并进现有条目的就并进去；意思已经在了的就不用重复。
{LOST}
"""
T_RETOLD = """
{N}. 下面几条被指出只是在说他此刻的感受或状态，没说他为什么会这样（像在转述听感记录）。请改成说出原因：原因来自线前面的经历，或这一段新发生的心理变化；感受本身最多留几个字。原因前面已经说过、这条也没有新东西的，就删掉。
{RETOLD}
"""
T_FORM = """
{N}. 这一段有的条目太长、或者挂了太多箭头，请按下面的形式整理。
"""


def notes(base):
    bl = json.loads((V.OUT / f"blind_{base}.json").read_text(encoding="utf-8"))
    al = json.loads((V.OUT / f"alone_{base}.json").read_text(encoding="utf-8"))
    lost, retold = {}, {}
    for v in bl.values():
        for sec, x in v.get("lost_new") or []:
            lost.setdefault(v["w"], {}).setdefault(sec, []).append(x["what"])
    for k, v in al.items():
        w = k.split("_")[0]
        for r in v.get("retold") or []:
            if r[1] == "复述珠子":
                retold.setdefault(w, {}).setdefault(r[0].split("-")[0], set()).add(r[0])
    return lost, retold


def main(base, out):
    lost, retold = notes(base)

    def piece(w):
        g = V.graph_of(w, base); segs = {s["id"]: s for s in draft10.segs(w)}
        rows = json.loads((V.OUT / f"{w}_{base}.json").read_text(encoding="utf-8"))["rows"]
        done = {"center": g["center"], "segments": []}; g6 = V.v6(w)

        def one(s):
            sec = s["sec"]; L = lost.get(w, {}).get(sec) or []; R = sorted(retold.get(w, {}).get(sec) or [])
            nlink = {}
            for b in s["because"]:
                nlink[b["to"]] = nlink.get(b["to"], 0) + 1
            badform = any(len(it["text"]) > 60 for it in s["items"]) or any(n > 1 for n in nlink.values())
            if not (L or R or badform):
                return sec, None
            tasks, n = "", 1
            if L:
                tasks += T_LOST.format(LOST="\n".join(f"- {x}" for x in L)); n += 1
            if R:
                txt = {it["id"]: it["text"] for it in s["items"]}
                tasks += T_RETOLD.format(N=n, RETOLD="\n".join(f"- [{i}] {txt.get(i, '')}" for i in R)); n += 1
            if not tasks:
                tasks = T_FORM.format(N=1)
            cur = V.view({"center": "", "segments": [s]}, ids=True, center=False, head=False)
            rid = f"rs_{w}_{sec}_{out}"
            if not evo.done(rid):
                evo.call(rid, P.format(NAME=covjudge.NAME[w], SEC=sec, BARS=s["bars"], REL=s.get("relation"), TASKS=tasks, MAXN=len(g6["segments"][[x["sec"] for x in g6["segments"]].index(sec)]["items"]),
                                  LINE=V.view(done, ids=True, center=False) if done["segments"] else "（这是第一段）", CUR=cur),
                         model=evo.G6, meta={"stage": "v6-restore"})
            e = V.parse(rid) or {}
            if not isinstance(e.get("items"), list) or not e["items"]:
                return sec, None
            old = {it["id"]: it for it in s["items"]}
            ns = V.seg_graph(e, sec, segs[sec]); ns["relation"] = s.get("relation")
            for it, raw in zip(ns["items"], e["items"]):
                it["explains"] = sorted({b for i in raw.get("src") or [] for b in old.get(i, {}).get("explains", [])})
            return sec, (ns, e, len(L), len(R))
        newsegs = done["segments"]
        for s in g["segments"]:            # in order: arrows only point back, so each segment sees the already-changed earlier ones
            got = one(s)[1]
            if not got:
                newsegs.append(s); V.tidy(done); continue
            ns, e, nl, nr = got; newsegs.append(ns); V.tidy(done)
            rows[s["sec"]] = {"edit": e, "check": None, "notes": [], "revised": False}
            print(f"{w} {s['sec']}: 找回 {nl} 处 改复述 {nr} 条 | {len(s['items'])} 条 → {len(ns['items'])} 条 | "
                  f"{sum(len(x['text']) for x in s['items'])} 字 → {sum(len(x['text']) for x in ns['items'])} 字 | 箭头 {len(s['because'])} → {len(ns['because'])}", flush=True)
        G = V.tidy({"center": g["center"], "segments": newsegs})
        json.dump({"graph": G, "rows": rows, "base": f"{base} 找回丢失 + 改复述 + 守 v6 形式"}, open(V.OUT / f"{w}_{out}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        (V.OUT / f"{w}_{out}.md").write_text(f"# {'Op.60' if w == 'op60' else 'Op.61'}｜关系图（在 v6 上修补，{out}）\n\n" + V.view(G), encoding="utf-8")
    evo.run_parallel([(w, (lambda w=w: piece(w))) for w in ("op60", "op61")], 2)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
