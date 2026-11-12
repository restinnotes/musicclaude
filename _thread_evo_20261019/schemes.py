"""11-02 round 1 of 迭代准则 (I03/I04): two redesigned pipelines from the prompt advisors (evaluations/v6fix/advisor_m6w.md),
prompts verbatim in schemes/*.txt, run to their own output (the line graph) and saved in the normal graph format so the
usual measurements (v6cov / v6alone / e2e_open / v6fix blind) work on them.
  P (GPT-6 r1, 方案 A): A0 three experience blueprints, no beads (Center given) → A1 coverage diagnosis vs beads → A2 one-shot
    full graph (sees blueprints + diagnosis, not raw beads). My only edit: Center is the upstream N04 one, not rewritten.
  Q (GPT-5.6, 方案一): A1 three routes with an established-ledger, no beads, no Center → A2 macro selection → A3 beads → experience
    qualities (no imagery / plot) → A4 one-shot full graph from routes + qualities. The writer never sees Center; the saved
    graph shows the upstream Center.
usage: SCHEME=P TAG=pa python schemes.py run        (both works in parallel)"""
import json, os, sys
from pathlib import Path
import covjudge, evo, v6fix as V

HERE = Path(__file__).parent
SPFX = os.environ.get("SPFX", "")      # revised schemes: SPFX=P2 reads schemes/P2_A0.txt ... (advisor_followup.py)
S = lambda k: (HERE / "schemes" / f"{(SPFX + k[k.index('_'):]) if SPFX else k}.txt").read_text(encoding="utf-8")
SCHEME = os.environ.get("SCHEME", "P"); TAG = os.environ.get("TAG", "pa"); REF = os.environ.get("REF", "m6w")
CENTER_IN = ("\n【Center（上游已定，不改）】\n{CENTER}\n这是读者回头看整首时把各段组织起来的那件事；"
             "不是他一开始就清楚知道的事，也不是每一段都要回应的题目。不预告发展路线和结局。\n")
_A2 = S("P_A2") if (SPFX or "P").startswith("P") else ""
P_A2_C_OLD = _A2[_A2.index("七、Center"):_A2.index("八、语言")] if "七、Center" in _A2 and "八、语言" in _A2 else None
P_A2_C_NEW = ("七、Center\nCenter 已经给定：{CENTER}\n不改写它，输出的 center 字段原样填入。它是回头看整首时把各段组织起来的那件事，"
              "不预告路线，不是每段都要回应。不要为了符合它，在后半篇反复证明同一结论。\n\n")


def work_info(w):
    return f"作曲家：肖邦（Chopin）\n作品：{covjudge.NAME[w]}"


def segments(w):
    g = V.graph_of(w, REF)
    return "\n".join(f"{s['sec']}：第 {s['bars']} 小节" for s in g["segments"]), g


def call(rid, msg):
    if not evo.done(rid):
        evo.call(rid, msg, model=evo.G6, meta={"stage": f"scheme-{SCHEME}"})
    out = V.parse(rid)
    if not out:
        raise RuntimeError(f"{rid}: no usable json")
    return out


def save(w, g_ref, e, note):
    bars = {s["sec"]: s["bars"] for s in g_ref["segments"]}
    got = {s.get("sec"): s for s in e.get("segments") or []}
    missing = [s for s in bars if not (got.get(s) or {}).get("items")]
    if missing:
        raise RuntimeError(f"{w} {TAG}: segments missing {missing}")
    G = {"center": g_ref["center"], "segments": []}; seen = set()
    for sec in bars:
        n = got[sec]
        items = [{"id": f"{sec}-{k}", "text": it["text"], "key": it["text"][:8], "follows": bool(it.get("after")), "explains": [],
                  "cite": [c for c in it.get("cite") or [] if isinstance(c, str) and c in seen]} for k, it in enumerate(n["items"], 1)]
        links = [{"from": c, "to": it["id"], "rel": "引用"} for it in items for c in it["cite"]]
        G["segments"].append({"sec": sec, "bars": bars[sec], "relation": n.get("relation"), "items": items, "because": links})
        seen |= {it["id"] for it in items}
    V.tidy(G)
    rows = json.loads((V.OUT / f"{w}_{REF}.json").read_text(encoding="utf-8"))["rows"]
    json.dump({"graph": G, "rows": rows, "base": note}, open(V.OUT / f"{w}_{TAG}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    (V.OUT / f"{w}_{TAG}.md").write_text(f"# {'Op.60' if w == 'op60' else 'Op.61'}｜线（{TAG}）\n\n" + V.view(G), encoding="utf-8")
    print(w, TAG, "字数", sum(len(i["text"]) for s in G["segments"] for i in s["items"]),
          "条目", sum(len(s["items"]) for s in G["segments"]), "关系", [s["relation"] for s in G["segments"]], flush=True)


def run_P(w):
    seg, g = segments(w); C = g["center"]
    a0 = S("P_A0").replace("{WORK_INFO}", work_info(w)).replace("{SEGMENTS}", seg + CENTER_IN.replace("{CENTER}", C)) \
        .replace("{INDEPENDENT_MUSIC_CONTEXT}", "（无）")
    cand = call(f"sc{TAG}_{w}_A0", a0)
    a1 = S("P_A1").replace("{CANDIDATES_JSON}", json.dumps(cand, ensure_ascii=False, indent=1)) \
        .replace("{BEADS_JSON}", covjudge.bead_text(w)).replace("{SEGMENTS}", seg)
    plan = call(f"sc{TAG}_{w}_A1", a1)
    a2 = (S("P_A2").replace(P_A2_C_OLD, P_A2_C_NEW.replace("{CENTER}", C)) if P_A2_C_OLD else S("P_A2").replace("{CENTER}", C)) \
        .replace("{WORK_INFO}", work_info(w)).replace("{SEGMENTS}", seg) \
        .replace("{CANDIDATES_JSON}", json.dumps(cand, ensure_ascii=False, indent=1)).replace("{COVERAGE_PLAN_JSON}", json.dumps(plan, ensure_ascii=False, indent=1))
    e = call(f"sc{TAG}_{w}_A2", a2)
    save(w, g, e, "方案 P（GPT-6 顾问方案 A）：三条经历蓝图（不看珠子，给 Center）→ 覆盖诊断 → 一次成图；无后续改写")


def run_Q(w):
    seg, g = segments(w)
    routes = call(f"sc{TAG}_{w}_A1", S("Q_A1").replace("{NAME}", work_info(w)).replace("{SECTIONS}", seg).replace("{K}", "3"))
    R = json.dumps(routes, ensure_ascii=False, indent=1)
    jobs = [(f"sc{TAG}_{w}_A2", lambda: call(f"sc{TAG}_{w}_A2", S("Q_A2") + "\n\n【候选路线】\n" + R)),
            (f"sc{TAG}_{w}_A3", lambda: call(f"sc{TAG}_{w}_A3", S("Q_A3") + "\n\n【段落】\n" + seg + "\n\n【珠子】\n" + covjudge.bead_text(w)))]
    evo.run_parallel(jobs, 2)
    sel, tg = V.parse(f"sc{TAG}_{w}_A2"), V.parse(f"sc{TAG}_{w}_A3")
    if not sel or not tg:
        raise RuntimeError(f"{w}: A2/A3 failed")
    a4 = S("Q_A4").replace("{SECTIONS}", seg).replace("{ROUTES}", R + "\n\n【宏观评审结果】\n" + json.dumps(sel, ensure_ascii=False, indent=1)) \
        .replace("{TARGETS}", json.dumps(tg, ensure_ascii=False, indent=1))
    e = call(f"sc{TAG}_{w}_A4", a4)
    save(w, g, e, "方案 Q（GPT-5.6 顾问方案一）：三条经历骨架+账本（不看珠子，不给 Center）→ 宏观选路 → 珠子去词化 → 一次成图；无后续改写")


if __name__ == "__main__" and sys.argv[1] == "run":
    f = {"P": run_P, "Q": run_Q}[SCHEME]
    evo.run_parallel([(w, (lambda w=w: f(w))) for w in ("op60", "op61")], 2)
