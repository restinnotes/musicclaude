"""Thread graph v3 (user 10-21). v2 split one situation into 所求/恐惧/理由/办法/机制/状态 nodes that restated each other,
let the model rewrite the Center, forced every segment to touch the Center, and turned passing feelings into 发现.
  center  : the accepted sentence, copied verbatim (checked)
  segments: {bars, relation: 正在面对|还说不清|没在想, units:[{id, text, kind?, handles:[{id, label, type}]}],
             because:[{from: earlier handle id, to: unit id here, rel, how?}], outer?}
  unit    = a short coherent passage (one situation); two units only when two different things happen in the segment
  handle  = only the part of a unit that a later segment points back to (label = words found verbatim in the unit)
  because = why-now (Connection/History): every segment after the first needs one from an earlier segment
Checks: Center verbatim; why-now per segment; handles unused / label not in text; near-duplicate units or how-notes;
hedges in the original segment that vanished; formula sentences; relation counts; chars vs original.
Coverage: GPT-6 causal-step inventory of the line (stepcheck.INV), GPT-5.6 checks graph and view against it (stepcheck.CHK).
ids: tg3_<line>_r<j> -> evaluations/tgraph3/; inv_<line>, g3chk_<full|view>_<graph id>
usage: python tgraph3.py build <line60> <line61> | inv <line...> | cov <graph id...>"""
import json, re, sys
from collections import Counter
import arts, evo, node2b, segcheck, stateinc, stepcheck, structured

OUT = evo.ROOT / "evaluations" / "tgraph3"
RELS = ("提供理由", "说明", "限制", "动摇", "唤起", "改写", "失效", "仍在起作用")
HEDGE = re.compile(r"仿佛|似乎|好像|一度|那一刻|有那么一刻|一时")
P = ("请把下面的原稿整理成一张“Thread 图”：每段一两个连贯的小段话（单位），加上段与段之间的关系。之后视频怎么呈现、要提取什么，都从这张图里取。"
     "原稿是基准：它的内容和内在逻辑不能丢，可以去掉的只有重复、铺垫、过渡、修饰和音乐描写。\n\n"
     "【Center】照抄下面这一句，一个字都不改，不要扩写、解释或另写：{CENTER}\n\n"
     "【每段的单位 units】\n"
     "- 一个单位是一小段连贯的话（通常两三句），用人话说清此刻他怎样、为什么会这样。原稿这一段里的每一步推进都要留在单位里"
     "（因为前面的什么，所以此刻怎样）；同一个意思只说一次。\n"
     "- 一段通常只有一个单位。只有这一段里真的发生了两件不同的事，才写成两个单位。不要把同一个处境按所求、恐惧、理由、办法、状态拆成几块。\n"
     "- 原稿里的限定要保留：原稿说仿佛、一度、那一刻、似乎，单位里也要有；一时的感受不能写成已经成立的认识；原稿还说不清的，不要替他说清。\n"
     "- 不加原稿没有的东西。\n"
     "- 如果这个单位是一次理解的积累，标 kind：分清（原先挤在一起的两个要求被分清）、办法的限度（一种给过他东西的办法显出不能处理的部分）、"
     "选择的代价、满足照出未满足、知道更多反而更尖锐。不是就留空。\n\n"
     "【把手 handles】\n"
     "- 只有后面某一段会单独回头指向的部分，才在单位里标成把手：label 是单位 text 里原样出现的几个字；type 写它是什么"
     "（快乐、回报、困难、需要、办法、认识、恐惧、所求等，选最贴切的一个）。\n"
     "- 后面没有段落指向的，不要标。\n\n"
     "【关系 because】\n"
     "- 写在后面那一段上：from 是更早段落里的把手 id，to 是这一段的单位 id，rel 取：" + "、".join(RELS) + "。\n"
     "- how：一句话说出这条关系里两端都没说出的东西；如果只是把两端连起来再说一遍，就省略。\n"
     "- 第一段以后的每一段，至少要有一条来自更早段落的关系——这就是他为什么此刻会这样。他暂时没在想那件事的段也一样：是前面的什么让他此刻能这样。\n"
     "- 要连出原稿写到的远处关系，不只连上一段。\n\n"
     "【他和那件事的关系 relation】每段标一个：正在面对（他在想它、试办法、有所发现）、还说不清（他感到被什么牵动，但说不出是什么）、"
     "没在想（他沉浸在别的感受里，这件事暂时不在心上）。照原稿如实标，不要求比例。\n\n"
     "【outer】可选：原稿里有的可感处境，一句；没有就省略，不要编。\n\n"
     + stateinc.RULES +
     "\n只输出一个 ```json 代码块：{\"center\": \"…\", \"segments\": [{\"bars\": \"{FIRST}\", \"relation\": \"还说不清\", "
     "\"units\": [{\"id\": \"U1\", \"text\": \"…\", \"kind\": \"\", \"handles\": [{\"id\": \"H1\", \"label\": \"…\", \"type\": \"办法\"}]}], \"because\": []}]}\n"
     "第二段起 because 写成 [{\"from\": \"H1\", \"to\": \"U2\", \"rel\": \"改写\", \"how\": \"…\"}]。segments 按顺序覆盖：{BARS}。\n\n")


# v3.1 (user 10-21 "有问题就继续修"): v3's last segments re-told earlier segments inside the unit while also pointing at them
# (Op.60 111–116: 464 chars, 12 arrows), and "仍在起作用" arrows piled up; "站稳" slipped through from the line.
P31 = (P.replace("同一个意思只说一次。\n", "同一个意思只说一次。\n"
                 "- 单位只写这一段新发生的。原稿里回顾、总结前面经历的句子（例如把前面几段的经历再数一遍），不要在单位里复述："
                 "用箭头指回那几段的把手，单位里只留从这些经历里得出的新东西。\n", 1)
       .replace("- 要连出原稿写到的远处关系，不只连上一段。\n", "- 要连出原稿写到的远处关系，不只连上一段。\n"
                "- 只连真正解释此刻的关系。“仍在起作用”只用于此刻确实还在左右他的感受或做法的东西；只是仍然存在、此刻没有起作用的，不连。"
                "同一个意思不要从几个把手各连一条。\n", 1)
       .replace("\n只输出一个 ```json", "不用“站稳、安顿、归属、边界、张力”这类抽象姿态词；原稿里有的，换成他具体在做什么、感到什么。\n"
                "\n只输出一个 ```json", 1))
assert P31.count("单位只写这一段新发生的") == 1 and P31.count("只连真正解释此刻的关系") == 1 and P31.count("站稳、安顿") == 1


def center(w):
    return json.loads((evo.ROOT / "evaluations" / "centers" / f"sel_{w}.json").read_text(encoding="utf-8"))[0]["center"]


def segtexts(t, w):
    return {f"{s['start']}–{s['end']}": s["text"] for s in segcheck.to_json(arts.clean(evo.output(t)), w)["segments"]}


def index(j):
    U, H = {}, {}
    for i, s in enumerate(j["segments"]):
        for u in s.get("units") or []:
            U[u["id"]] = (i, u)
            for h in u.get("handles") or []:
                H[h["id"]] = (i, h, u)
    return U, H


def bigrams(t):
    t = re.sub(r"\W", "", t)
    return {t[k:k + 2] for k in range(len(t) - 1)}


def sim(a, b):
    A, B = bigrams(a), bigrams(b)
    return len(A & B) / max(1, len(A | B))


def check(j, w, t):
    segs, orig = j["segments"], segtexts(t, w)
    U, H = index(j); used, no_why, bad, dup = set(), [], [], []
    for i, s in enumerate(segs):
        ok = False
        for e in s.get("because") or []:
            f = e.get("from")
            if f in H and H[f][0] < i:
                ok = True; used.add(f)
            else:
                bad.append(f"{s['bars']} from {f}")
            if e.get("to") not in U or U[e["to"]][0] != i:
                bad.append(f"{s['bars']} to {e.get('to')}")
            if e.get("rel") not in RELS:
                bad.append(f"{s['bars']} rel {e.get('rel')}")
            if e.get("how") and e.get("to") in U and sim(e["how"], U[e["to"]][1]["text"]) > 0.3:
                dup.append(f"{s['bars']} how≈{e['to']}")
        if i and not ok:
            no_why.append(s["bars"])
        us = s.get("units") or []
        dup += [f"{s['bars']} {a['id']}≈{b['id']}" for k, a in enumerate(us) for b in us[k + 1:] if sim(a["text"], b["text"]) > 0.3]
    alltext = "\n".join(u["text"] for _, u in U.values()) + "\n".join(e.get("how", "") for s in segs for e in s.get("because") or [])
    return {"center_verbatim": j.get("center") == center(w), "bars_ok": [s["bars"] for s in segs] == structured.bars(w),
            "segments_without_why_now": no_why, "bad_refs": bad, "handles": len(H),
            "unused_handles": [h for h in H if h not in used], "label_not_in_text": [h for h, (_, x, u) in H.items() if x.get("label", "") not in u.get("text", "")],
            "near_duplicates": dup, "hedge_lost": [s["bars"] for s in segs if HEDGE.search(orig.get(s["bars"], "")) and not any(HEDGE.search(u["text"]) for u in s.get("units") or [])],
            "formula": len(re.findall(r"越[^，。；]{0,12}越", alltext)) + len(re.findall(r"不是[^。；]{0,20}而是", alltext)),
            "posture_words": re.findall(r"站稳|安顿|归属|边界|张力", alltext),
            "arrows": sum(len(s.get("because") or []) for s in segs),
            "still_arrows": sum(e.get("rel") == "仍在起作用" for s in segs for e in s.get("because") or []),
            "longest_unit_chars": max((sum(len(u["text"]) for u in s.get("units") or []), s["bars"]) for s in segs),
            "relations": dict(Counter(s.get("relation") for s in segs)), "units_per_seg": dict(Counter(len(s.get("units") or []) for s in segs)),
            "kinds": dict(Counter(u.get("kind") for _, u in U.values() if u.get("kind"))),
            "chars": len(alltext), "orig_chars": sum(len(x) for x in orig.values())}


def view(j, title):
    U, H = index(j); segs = j["segments"]
    md = [f"# {title}", "", f"**Center：**{j['center']}", ""]
    for s in segs:
        md += [f"### {s['bars']}　（{s.get('relation')}）", ""]
        for u in s.get("units") or []:
            txt = u["text"]
            for h in u.get("handles") or []:
                if h.get("label") and h["label"] in txt:
                    txt = txt.replace(h["label"], f"**{h['label']}**", 1)
            md += [txt + (f"　✦ {u['kind']}" if u.get("kind") else ""), ""]
        def where(e):
            src = H.get(e.get("from"))
            return f"（{segs[src[0]]['bars']}）「{src[1].get('label')}」" if src else f"（?）{e.get('from')}"
        es = s.get("because") or []   # why-now arrows one per line; what merely stays in force on one line
        for e in [e for e in es if e.get("rel") != "仍在起作用" or e.get("how")]:
            md.append(f"- ← {e.get('rel')}：{where(e)}" + (f" —— {e['how']}" if e.get("how") else ""))
        still = [where(e) for e in es if e.get("rel") == "仍在起作用" and not e.get("how")]
        if still:
            md.append("- ⟲ 仍在起作用：" + "；".join(still))
        if s.get("outer"):
            md.append(f"- ◎ {s['outer']}")
        md.append("")
    return "\n".join(md)


def full_text(j):
    U, H = index(j); segs = j["segments"]
    md = [f"Center：{j['center']}", ""]
    for s in segs:
        md.append(f"### {s['bars']}（{s.get('relation')}）")
        md += [f"- {u['id']}：{u['text']}" + (f"（理解的积累：{u['kind']}）" if u.get("kind") else "")
               + "".join(f"［把手 {h['id']}「{h.get('label')}」·{h.get('type')}］" for h in u.get("handles") or []) for u in s.get("units") or []]
        md += [f"- 关系：{e.get('from')}（{segs[H[e['from']][0]]['bars'] if e.get('from') in H else '?'}）{e.get('rel')} {e.get('to')}" + (f"：{e['how']}" if e.get("how") else "")
               for e in s.get("because") or []]
        if s.get("outer"):
            md.append(f"- 处境：{s['outer']}")
        md.append("")
    return "\n".join(md)


def work(t):
    return "op60" if "op60" in t else "op61"


def save(rid, t):
    w = work(t); j = evo.parse_json(evo.output(rid)); j["source"] = t; j["check"] = check(j, w, t)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{rid}.json").write_text(json.dumps(j, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / f"{rid}_view.md").write_text(view(j, f"{'Op.60' if w == 'op60' else 'Op.61'}｜关系图"), encoding="utf-8")
    print(rid, json.dumps(j["check"], ensure_ascii=False), flush=True)


if __name__ == "__main__":
    ph, args = sys.argv[1], sys.argv[2:]
    if ph in ("build", "build31"):
        pre, prompt = ("tg3", P) if ph == "build" else ("tg31", P31)
        jobs = []
        for t in args:
            msg = stateinc.fill(prompt, work(t)).replace("{CENTER}", center(work(t))) + "========== 原稿 ==========\n" + arts.clean(evo.output(t))
            jobs += [node2b.job(f"{pre}_{t}_r{j}", msg, {"stage": pre, "thread": t}) for j in (1, 2) if not evo.done(f"{pre}_{t}_r{j}")]
        evo.run_parallel(jobs, 4)
        for t in args:
            for j in (1, 2):
                if evo.done(f"{pre}_{t}_r{j}"):
                    save(f"{pre}_{t}_r{j}", t)
    elif ph == "inv":
        stepcheck.OUT.mkdir(parents=True, exist_ok=True)
        evo.run_parallel([(f"inv_{t}", (lambda t=t: evo.call(f"inv_{t}", stepcheck.INV + arts.clean(evo.output(t)), prompt_text=stepcheck.INV, meta={"stage": "step_inventory"})))
                          for t in args if not evo.done(f"inv_{t}")], 2)
        for t in args:
            inv = evo.parse_json(evo.output(f"inv_{t}"))
            (stepcheck.OUT / f"{t}.json").write_text(json.dumps(inv, ensure_ascii=False, indent=1), encoding="utf-8")
            print(t, len(inv["steps"]), "steps", flush=True)
    elif ph == "final":   # relation per segment = majority of the line judges' 4 reads + both graph builds (tie: this graph)
        norm = {"面对": "正在面对", "说不清": "还说不清", "没在想": "没在想"}
        for g in args:
            j = json.loads((OUT / f"{g}.json").read_text(encoding="utf-8")); t = j["source"]; w = work(t)
            reads = [x["center_relation_by_segment"] for x in json.loads((evo.ROOT / "evaluations" / f"C8{w[2:]}" / "rows.json").read_text(encoding="utf-8"))
                     if x["name"] == t and len(x.get("center_relation_by_segment") or []) == len(j["segments"])]
            pre = g[:g.index("_" + t)]
            sib = [json.loads(f.read_text(encoding="utf-8")) for f in OUT.glob(f"{pre}_{t}_r*.json") if f.stem != g and not f.stem.endswith("_final")]
            for i, s in enumerate(j["segments"]):
                votes = [norm.get(r[i], r[i]) for r in reads] + [s["relation"]] + [x["segments"][i]["relation"] for x in sib]
                c = Counter(votes).most_common(); top = [k for k, n in c if n == c[0][1]]
                s["relation_votes"] = dict(c); s["relation_model"] = s["relation"]
                s["relation"] = s["relation"] if s["relation"] in top else top[0]
            j["check"] = check(j, w, t)
            (OUT / f"{g}_final.json").write_text(json.dumps(j, ensure_ascii=False, indent=1), encoding="utf-8")
            (OUT / f"{g}_final_view.md").write_text(view(j, f"{'Op.60' if w == 'op60' else 'Op.61'}｜关系图"), encoding="utf-8")
            print(g, [(s["bars"], s["relation_model"], "→", s["relation"]) for s in j["segments"] if s["relation"] != s["relation_model"]], flush=True)
    elif ph == "cov":
        vers = {}
        for g in args:
            j = json.loads((OUT / f"{g}.json").read_text(encoding="utf-8"))
            vers[(g, "full")] = full_text(j); vers[(g, "view")] = (OUT / f"{g}_view.md").read_text(encoding="utf-8")
        jobs = []
        for (g, v), txt in vers.items():
            t = json.loads((OUT / f"{g}.json").read_text(encoding="utf-8"))["source"]; rid = f"g3chk_{v}_{g}"
            if not evo.done(rid):
                msg = stepcheck.CHK.replace("{INV}", (stepcheck.OUT / f"{t}.json").read_text(encoding="utf-8")).replace("{TXT}", txt)
                jobs.append((rid, (lambda rid=rid, msg=msg: evo.call(rid, msg, prompt_text=stepcheck.CHK[:300], model=evo.G56, meta={"stage": "graph3_cov"}))))
        evo.run_parallel(jobs, 4)
        rows = []
        for (g, v), txt in vers.items():
            r = evo.output(f"g3chk_{v}_{g}")
            if not r:
                continue
            t = json.loads((OUT / f"{g}.json").read_text(encoding="utf-8"))["source"]
            inv = {s["id"]: s for s in json.loads((stepcheck.OUT / f"{t}.json").read_text(encoding="utf-8"))["steps"]}
            c = evo.parse_json(r); st = c.get("steps", {}); ad = c.get("additions", [])
            rows.append({"graph": g, "version": v, "total": len(inv), **{k: list(st.values()).count(k) for k in ("kept", "weakened", "lost", "wrong")},
                         "not_kept": [{"id": k, "seg": inv.get(k, {}).get("segment"), "because": inv.get(k, {}).get("because"), "so": inv.get(k, {}).get("so"), "verdict": x}
                                      for k, x in st.items() if x != "kept"],
                         "add_new": [a.get("text") for a in ad if a.get("type") == "new"], "chars": len(txt)})
        f = OUT / "cov_rows.json"; old = json.loads(f.read_text(encoding="utf-8")) if f.exists() else []
        keep = [r for r in old if (r["graph"], r["version"]) not in vers]
        f.write_text(json.dumps(keep + rows, ensure_ascii=False, indent=1), encoding="utf-8")
        for r in rows:
            print(f"{r['graph']:32s} {r['version']:4s} 保留{r['kept']}/{r['total']} 弱化{r['weakened']} 丢{r['lost']} 错{r['wrong']} 新增{len(r['add_new'])} 字{r['chars']}", flush=True)
