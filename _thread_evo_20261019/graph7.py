"""10-28 user: "按道理应该最后都是关系图吧 你这个太长了". THREAD_SPEC §十 4: the line's product is the relation graph (v4.3 form:
short items <= 45 chars, → inside a segment, ← only to real earlier causes, a relation per segment). The 10-27/28 synth + repair
chain wrote 感受/为什么 paragraphs instead (Op.60 11.4k chars and 228 per item, package 3 4.7k and 32 per step), and the repair
copied bead bar positions into the line. This turns the current best line (deliver_halfdone.pick per segment) into the graph
with tgraph4's v5 prompt (v4.3 + plain words) plus: no bar numbers, the checker's 待改 notes applied, earlier history as arrows.
Calls: build per piece (g6) -> audit per piece (g56: arrows, anything added or lost; 勉强/不支持 arrows dropped) -> two
regression judges per piece against package 3 (finalize3.R). 8 in all, 2 in flight.
ids: gr7_<work>, ga7_<work>, gj7_<work>_<judge>.  usage: THREAD_ROUTE=gpt3s python graph7.py [dry]
-> evaluations/graph7/ and deliver_20261028/半成品_关系图加珠子_Op60_Op61.md"""
import json, re, sys
import covjudge, deliver_halfdone as D, draft10, evo, finalize3, node2b, precise as P, stateinc, tgraph4

OUT = evo.ROOT / "evaluations" / "graph7"
DELIVER = evo.ROOT / "deliver_20261028" / "半成品_关系图加珠子_Op60_Op61.md"
ANCHOR = "\n只输出一个 ```json 代码块：{\"center\""
EXTRA = ("【这份原稿的特别说明】\n"
         "- 原稿每段有几条，每条分“感受”和“为什么”。图里要留下他此刻的感受，以及它此刻为什么会出现。"
         "“为什么”里说到前面段落的经历时，用 because 指回前面段落的条目，不要在条目里再复述一遍。\n"
         "- 原稿里为了防止误读而加的限定（“这不等于……”“不是……而是……”“并不意味着……”），只在它说出真实限制时保留，其余去掉。\n"
         "- 条目里不写小节号和音乐里的位置（“到了某某小节”“某某小节附近”这类），也不写音乐本身。\n"
         "- 有的条目后面附了［待改］：那是核对者指出的越界之处（多写了具体动作，或把音乐当成了心理原因）。整理时去掉越界的部分，只留下有依据的心理过程。\n"
         "- 每段标题括号里已经标了他和那件事的关系，relation 照用。\n")
BUILD = tgraph4.P5.replace(ANCHOR, "\n" + EXTRA + ANCHOR, 1)
assert BUILD != tgraph4.P5
AUDIT = (tgraph4.ARROWS42.split("只输出一个")[0]
         + "另外请看整张图：\n- added：图里有没有原稿没有的东西（新的原因、事件、动作），每处一句；\n"
           "- lost：原稿里哪一步重要的因果在图里丢了或说反了，每处写段和一句。原稿里标了［待改］的部分本来就该去掉，去掉不算丢。\n"
           "只输出一个 ```json 代码块：{\"A1\": \"支持\", \"A2\": \"不支持\", ..., \"notes\": {\"A2\": \"一句话说明\"}, "
           "\"added\": [\"…\"], \"lost\": [{\"seg\": \"17–23\", \"what\": \"…\"}]}\n\n")
BAR = re.compile(r"\d")


def source(w):
    fin, _ = P.t0(w); out = []
    for s in draft10.segs(w):
        e, _, _, flags = D.pick(w, s["id"])
        lab = next((x.get("label", "") for x in fin["sections"] if x["sec"] == s["id"]), "")
        out.append(f"### {s['start']}–{s['end']}（{lab}）")
        out += [f"{i}. 感受：{D.clean(x.get('feel', ''))} 为什么：{D.clean(x.get('why', ''))}" + (f"［待改：{D.note(flags[i])}］" if i in flags else "")
                for i, x in enumerate(e.get("items") or [], 1)]
        out.append("")
    return fin.get("center", ""), "\n".join(out)


def check(j, w, center):
    I = tgraph4.index(j); segs = j.get("segments") or []; texts = [it["text"] for _, it in I.values()]; bad, no_why = [], []
    for i, s in enumerate(segs):
        es = s.get("because") or []
        bad += [f"{s['bars']} {e.get('from')}→{e.get('to')}" for e in es
                if e.get("from") not in I or I[e["from"]][0] >= i or e.get("to") not in I or I[e["to"]][0] != i]
        if i and not es:
            no_why.append(s["bars"])
    return {"center_verbatim": j.get("center") == center, "bars_ok": [s["bars"] for s in segs] == [f"{x['start']}–{x['end']}" for x in draft10.segs(w)],
            "items": len(I), "chars": sum(map(len, texts)), "avg": sum(map(len, texts)) // max(1, len(texts)),
            "too_long": [x for x in texts if len(x) > 45], "with_digits": [x for x in texts if BAR.search(x)],
            "bad_refs": bad, "segments_without_arrow": no_why}


def arrows(j):
    I = tgraph4.index(j); n = 0; lst = []
    for s in j["segments"]:
        for e in s.get("because") or []:
            n += 1; a, b = I.get(e.get("from")), I.get(e.get("to"))
            e["aid"] = f"A{n}"
            if a and b:
                lst.append(f"A{n}：（{j['segments'][a[0]]['bars']}）{a[1]['text']}  —{e.get('rel')}→  （{s['bars']}）{b[1]['text']}")
    return lst


def render(j, w, plain=False):
    """plain: package 3's own layout (for the regression judges); otherwise markdown for the user."""
    I = tgraph4.index(j); segs = j["segments"]; ids = [x["id"] for x in draft10.segs(w)]; out = []
    for k, s in enumerate(segs):
        out += [f"S{k + 1:02d} ｜ {s['bars']}小节 ｜ {s.get('relation', '')}" if plain else f"**线**（{s.get('relation', '')}）", ""]
        for n, it in enumerate(s.get("items") or []):
            out.append(f"{'→' if it.get('follows') and n else '•'} {it['text']}" if plain else f"- {'→ ' if it.get('follows') and n else ''}{it['text']}")
            for e in s.get("because") or []:
                x = I.get(e.get("from"))
                if e.get("to") == it["id"] and x:
                    ref = f"{ids[x[0]]}（{segs[x[0]]['bars']}）「{x[1].get('key') or x[1]['text'][:10]}」"
                    out.append(f"  ← {segs[x[0]]['bars']}「{x[1].get('key') or x[1]['text'][:10]}」〔{e.get('rel')}〕" if plain else f"  - ← {e.get('rel')}：{ref}")
        out.append("")
    return "\n".join(out)


def main(dry):
    OUT.mkdir(exist_ok=True)
    src = {w: source(w) for w in ("op60", "op61")}
    jobs = []
    for w, (center, text) in src.items():
        msg = stateinc.fill(BUILD, w).replace("{CENTER}", center) + "========== 原稿 ==========\n" + text
        (OUT / f"prompt_gr7_{w}.txt").write_text(msg, encoding="utf-8")
        print(w, "建图提示词", len(msg), "字（原稿", len(text), "字）", flush=True)
        if not evo.done(f"gr7_{w}"):
            jobs.append(node2b.job(f"gr7_{w}", msg, {"stage": "graph7"}, w="g6"))
    if dry:
        return
    evo.run_parallel(jobs, 2)
    graphs, jobs = {}, []
    for w, (center, text) in src.items():
        j = evo.parse_json(evo.output(f"gr7_{w}")); j["check"] = check(j, w, center); graphs[w] = j
        print(w, "图：", json.dumps(j["check"], ensure_ascii=False)[:800], flush=True)
        msg = AUDIT + "========== 原稿 ==========\n" + text + "\n\n========== 图的条目 ==========\n" + render(j, w, plain=True) + "\n\n========== 关系 ==========\n" + "\n".join(arrows(j))
        if not evo.done(f"ga7_{w}"):
            jobs.append(node2b.job(f"ga7_{w}", msg, {"stage": "graph7-audit"}, w="g56"))
    evo.run_parallel(jobs, 2)
    jobs = []
    for w, j in graphs.items():
        a = evo.parse_json(evo.output(f"ga7_{w}")); j["audit"] = a
        for s in j["segments"]:                       # THREAD_SPEC §九 5: 勉强 and 不支持 arrows are deleted
            s["because_all"] = s.get("because") or []
            s["because"] = [e for e in s["because_all"] if a.get(e.get("aid")) == "支持"]
        print(w, "箭头：", {v: sum(1 for k, x in a.items() if k.startswith("A") and x == v) for v in ("支持", "勉强", "不支持")},
              "| 多出来的", len(a.get("added") or []), "| 丢掉的", len(a.get("lost") or []), flush=True)
        new = f"{covjudge.NAME[w]}\nCenter：{j['center']}\n\n" + render(j, w, plain=True)
        (OUT / f"P7g_{w}.txt").write_text(new, encoding="utf-8")
        jobs += [node2b.job(f"gj7_{w}_{k}", finalize3.R.format(NAME=covjudge.NAME[w], OLD=finalize3.PKG3[w].read_text(encoding="utf-8-sig"), NEW=new),
                            {"stage": "graph7-R"}, w=k) for k in ("g6", "g56") if not evo.done(f"gj7_{w}_{k}")]
    evo.run_parallel(jobs, 2)
    out = ["# 半成品：关系图 + 珠子（10-28）", "",
           "- **线**：这两天修准后的线，整理成关系图：每条一件事、不超过 45 字；→ 表示由上一条引出；← 指回前面段落里真正的前因。",
           "- **珠子**：包 3 的珠子原样照录。", ""]
    for w, j in graphs.items():
        j["regression"] = {k: evo.parse_json(evo.output(f"gj7_{w}_{k}")) for k in ("g6", "g56")}
        (OUT / f"gr7_{w}.json").write_text(json.dumps(j, ensure_ascii=False, indent=1), encoding="utf-8")
        print(w, "对照包3：", {k: r.get("verdict") for k, r in j["regression"].items()}, flush=True)
        bs = covjudge.beads(w); parts = render(j, w).split("\n\n**线**")
        out += [f"## 肖邦{covjudge.NAME[w]}", "", f"**这首的主线**：{j['center']}", ""]
        for s, body in zip(draft10.segs(w), [parts[0]] + ["**线**" + p for p in parts[1:]]):
            out += [f"### {s['id']} ｜ {s['start']}–{s['end']} 小节", "", body.strip(), "", "**珠子**", ""]
            out += [f"- **{b['id'].split('-')[-1]}**［{b['role']}］（{b['measures']} 小节）{b['text']}" for b in bs if b["sec"] == s["id"]]
            out.append("")
    DELIVER.write_text("\n".join(out), encoding="utf-8")
    print(DELIVER, flush=True)


if __name__ == "__main__":
    main("dry" in sys.argv[1:])
