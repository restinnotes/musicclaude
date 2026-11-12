"""11-01: DAG N05 v3 + N06 v5 — fix circling at the source, with the new Center (N04 v2, chosen2.json).
Found: every later layer (N08 v3 voices, N09c, N09d with Argon / Gemini / GPT-6) keeps the line's structure because the writer
sees the old line; the open review's main complaint (the same dilemma re-said segment after segment, a narrow set of abstract
words) is a content matter born upstream: N05 asks each moment to be explained by what came before but forbids outer events,
so the only engine left is the inner dilemma, re-said; N06 defines every item as "他此刻感到什么、想要什么、怕什么", so each
segment re-lists the standing feelings. User (11-01): "dag 不仅是你可以加后置层 还有可能可以修改已有的层的呀"; also the
delivered h-line still carried the OLD Center ("……相互牵制"), which itself breeds the back-and-forth.
  lines : spine + article ×3 per work with the new Center; ids lna3_<w>_r<j>, ln3_<w>_r<j>
  judge : blind read of the 3 new articles + the previous DAG pick (pick_d) as reference: legible / advance / overall;
          ids lj3_<w>_<judge>; pick -> evaluations/center_dag/pick_<TAG>.json (TAG default e)
  graph : N06 v5 (item = what is NEW in this segment; standing worries are pointed back to, not re-listed), 2 builds,
          ids tg5_<article>_r<j>; import -> evaluations/v6fix/<w>_<TAG>0.json
usage: python dag_src3.py lines | judge | graph | import"""
import json, os, random, sys
from statistics import mean
import arts, covjudge, draft9, draft10, evo, line8, line_dag, node2b, stateinc, tgraph3, tgraph4, v6fix as V
import center_dag

W = ("op60", "op61"); R = (1, 2, 3)
TAG = os.environ.get("TAG", "e")
CENTER = json.loads((center_dag.OUT / "chosen2.json").read_text(encoding="utf-8"))
tgraph3.center = lambda w: CENTER[w]
PICK = center_dag.OUT / f"pick_{TAG}.json"
PREV = json.loads((center_dag.OUT / "pick_d.json").read_text(encoding="utf-8"))

# 11-01 (second try, same day): the first version of this rule asked "他因此试了什么办法……在哪里不够用" — exactly the
# wording 10-23 measured as the source of the 办法→失效→换办法 swing (THREAD_SPEC §十.7, draft9.py). So N05 v3 = draft9's
# corrected S rules (no 试过/发现, PLAIN: 不靠心理动作推动故事) + one rule against re-saying, which names no methods.
ADV = ("前面已经写清的顾虑或两难，后面不要再完整说一遍。同一种感受延续下去时，只写它这一次有什么不同"
       "（更深了、变轻了、换成了它的哪一面、和什么连到了一起），旧的理由用几个字带过。"
       "他想要的、怕的，每次都说出这一回具体是哪一面，不要反复用同一个概括的词。")
SPINE = draft9.S_SPINE.replace("\n只输出这段文字。", "\n7. " + ADV + "\n只输出这段文字。")
LAY = draft9.S_LAY.replace("不写前言，直接从第一段写起。\n", "不写前言，直接从第一段写起。\n6. " + ADV + "\n")
assert ADV in SPINE and ADV in LAY

# 11-01 night (user: the re-saying rule "看起来很怪……非常不泛化……也不像是人话"): ADV and NEW_ITEM were my own untested
# additions — ADV presumes every piece is about 顾虑/两难 and contradicts draft9 rule 3 ("一段里可以没有新的变化，只是前面感受的
# 延续、加深或再次出现"); NEW_ITEM brings back the relation label "仍在起作用" the user rejected on 10-30. SRCV=4 = the clean
# baseline: draft9 S rules exactly as confirmed 10-23 (THREAD_SPEC §十.7), the DAG's own pick judge and N06 prompt unchanged.
SRCV = os.environ.get("SRCV", "3")
if SRCV == "4":
    SPINE, LAY = draft9.S_SPINE, draft9.S_LAY
PX = {"3": ("lna3", "ln3", "lj3", "tg5"), "4": ("lna4", "ln4", "lj4", "tg6")}[SRCV]

OLD_ITEM = "每条是一个短句，只说一件事：他此刻感到什么、想要什么、怕什么、做了什么、发现了什么。"
NEW_ITEM = ("每条是一个短句，只说这一段新出现的一件事：他此刻新感到的、新想要的、新怕的，或者原有的感受这一次有什么不同；"
            "此刻的感受只在它是新的，或者是这一步的直接原因时才写成条目。前面段落已经写成条目的顾虑和两难，这里不再写成条目，"
            "用关系（仍在起作用、限制）指回那一条。条目不必都以“他”开头，也不必写成“他想/他怕/他觉得……”，可以直接说那件事。")
assert tgraph4.P.count(OLD_ITEM) == 1
P6 = tgraph4.P.replace(OLD_ITEM, NEW_ITEM) if SRCV == "3" else tgraph4.P

JUDGE = line_dag.JUDGE.replace(
    "每项给 清楚 / 模糊 / 说不出，并引用一句最能说明你判断的原文。",
    "4. 前后推进：后面的段落是在往前走（他的感受和所求随经历真正变了，站到了新的位置），还是在原地打转"
    "（把同一个两难、同一组词换个说法再说一遍）？指出最大的一处打转（引用原文）。\n"
    "前三项给 清楚 / 模糊 / 说不出，并引用一句最能说明你判断的原文。").replace(
    "最后给 legible", "再给 advance（1–10：前后推进，10 = 每个阶段都站在新位置、没有重说；靠“劝自己、想通、找办法、办法失效、下决心”来回摆也算打转）、loop（最大的一处打转，一句话）；最后给 legible").replace(
    '"legible": 0, "overall": 0', '"advance": 0, "loop": "…", "legible": 0, "overall": 0')
assert "advance" in JUDGE
if SRCV == "4":
    JUDGE = line_dag.JUDGE


def lines():
    base = {w: line_dag.base(w, CENTER[w]) for w in W}
    evo.run_parallel([node2b.job(f"{PX[0]}_{w}_r{j}", base[w] + "\n\n---\n" + SPINE, {"stage": "dag_n05v3_spine", "work": w})
                      for w in W for j in R if not evo.done(f"{PX[0]}_{w}_r{j}")], 6)
    evo.run_parallel([node2b.job(f"{PX[1]}_{w}_r{j}", base[w] + "\n\n---\n" + LAY.replace("{SPINE}", evo.output(f"{PX[0]}_{w}_r{j}")), {"stage": "dag_n05v3", "work": w})
                      for w in W for j in R if evo.done(f"{PX[0]}_{w}_r{j}") and not evo.done(f"{PX[1]}_{w}_r{j}")], 6)
    print({f"{PX[1]}_{w}_r{j}": evo.done(f"{PX[1]}_{w}_r{j}") for w in W for j in R}, flush=True)


def maps(w, jn):
    ns = ([PREV[w]] if SRCV == "3" else []) + [f"{PX[1]}_{w}_r{j}" for j in R if evo.done(f"{PX[1]}_{w}_r{j}")]
    m = ns[:]; random.Random(f"{PX[2]}{w}{jn}").shuffle(m)
    return {f"文章{chr(65 + i)}": n for i, n in enumerate(m)}


def judge():
    jobs = []
    for w in W:
        for jn, model in (("g6", evo.G6), ("g56", evo.G56)):
            mp = maps(w, jn); rid = f"{PX[2]}_{w}_{jn}"
            arts_ = "\n\n".join(f"【{k}】\n{evo.output(n)}" for k, n in mp.items())
            if not evo.done(rid):
                jobs.append((rid, (lambda rid=rid, msg=JUDGE.format(NAME=covjudge.NAME[w], ARTS=arts_), model=model: evo.call(rid, msg, model=model, meta={"stage": "dag_n05v3_judge"}))))
    evo.run_parallel(jobs, 4)
    out, md = {}, ["# N05 v3 盲读（新 Center + 往前走的要求；上一轮 DAG 选中稿作参照）", ""]
    for w in W:
        sc = {}
        md += [f"## {w}", "", "| 评委 | 文章 | 来源 | 推进 | 看得懂 | 总体 | 最大的打转 | 复述 |", "|---|---|---|---|---|---|---|---|"]
        for jn in ("g6", "g56"):
            mp = maps(w, jn)
            for a in (evo.parse_json(evo.output(f"{PX[2]}_{w}_{jn}") or "{}") or {}).get("articles") or []:
                n = mp.get(a.get("id"), "?")
                md.append(f"| {jn} | {a.get('id')} | {n} | {a.get('advance')} | {a.get('legible')} | {a.get('overall')} | {a.get('loop', '')} | {a.get('story', '')} |")
                if n.startswith(PX[1] + "_"):
                    sc.setdefault(n, []).append(float(a.get("overall") or 0) + (float(a.get("advance") or 0) if SRCV == "3" else 0) + float(a.get("legible") or 0) / 10)
        md.append("")
        if sc:
            out[w] = max(sc, key=lambda n: mean(sc[n])); print(w, {n: round(mean(v), 2) for n, v in sc.items()}, "->", out[w], flush=True)
    (center_dag.OUT / f"legible{SRCV}_{TAG}.md").write_text("\n".join(md), encoding="utf-8"); print("\n".join(md), flush=True)
    PICK.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")


def graph():
    P = json.loads(PICK.read_text(encoding="utf-8")); jobs = []
    for w, t in P.items():
        msg = stateinc.fill(P6, w).replace("{CENTER}", CENTER[w]) + "========== 原稿 ==========\n" + arts.clean(evo.output(t))
        jobs += [node2b.job(f"{PX[3]}_{t}_r{j}", msg, {"stage": "dag_n06v5", "thread": t}) for j in (1, 2) if not evo.done(f"{PX[3]}_{t}_r{j}")]
    evo.run_parallel(jobs, 4)
    for w, t in P.items():
        for j in (1, 2):
            if evo.done(f"{PX[3]}_{t}_r{j}"):
                tgraph4.save(f"{PX[3]}_{t}_r{j}", t)


def imp():
    import dag_run
    P = json.loads(PICK.read_text(encoding="utf-8"))
    for w, t in P.items():
        cands = []
        for j in (1, 2):
            f = tgraph4.OUT / f"{PX[3]}_{t}_r{j}.json"
            if f.exists():
                d = json.loads(f.read_text(encoding="utf-8")); cands.append((dag_run.problems(d["check"]), j, d))
        _, j, d = min(cands, key=lambda x: x[:2])
        out = []
        for s, x in zip(draft10.segs(w), d["segments"]):
            out.append({"sec": s["id"], "bars": x["bars"], "relation": x.get("relation"),
                        "items": [{k: it.get(k) for k in ("id", "text", "key", "follows")} for it in x.get("items") or []],
                        "because": [{k: e.get(k) for k in ("from", "to", "rel", "how")} for e in x.get("because") or []]})
        g = V.tidy({"center": CENTER[w], "segments": out})
        json.dump({"graph": g, "rows": {}, "base": (f"DAG v3：新 Center 写稿 {t}（N05 v3）→ 转关系图 {PX[3]}_{t}_r{j}（N06 v5）" if SRCV == "3" else f"基线：现行 DAG + 10-23 写稿修正（draft9 S），新 Center 写稿 {t} → 转关系图 {PX[3]}_{t}_r{j}（N06 原版）")},
                  open(V.OUT / f"{w}_{TAG}0.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        (V.OUT / f"{w}_{TAG}0.md").write_text(f"# {'Op.60' if w == 'op60' else 'Op.61'}｜DAG v3 关系图（{TAG}0）\n\n" + V.view(g), encoding="utf-8")
        print(w, "导入", f"{PX[3]}_{t}_r{j}", "段", len(out), "条目", sum(len(s["items"]) for s in out), flush=True)


if __name__ == "__main__":
    {"lines": lines, "judge": judge, "graph": graph, "import": imp}[sys.argv[1]]()
