"""Model comparison on the Thread stage.
- Inner by GPT-5.6 (gpt3, same zip) and Gemini 3.8 Flash high (opencode, T docs inline) for each selected thread.
- Blind 3-way Inner judging by a panel of GPT-6, GPT-5.6 and Gemini (report per judge).
- Extra Outer lanes by GPT-5.6 and Gemini (input: the GPT-6 Inner, same as the GPT-6 lanes) -> mixed anonymous curation.
"""
import json, random, sys
import thr, common
import step3_inner_outer as s3

SEL = s3.SEL
NT = "18"  # this round uses the 18-doc T zip throughout (GPT-5.6 T docs were recovered after it began)
s3.NT = NT
T_INLINE = "\n\n".join(f"### {k}\n\n{v}" for k, v in thr.load_T().items() if k in {p.split('/')[-1][:-3] for p in []} or True)


def t_inline():
    T = {k: v for k, v in thr.load_T().items() if not k.startswith("T-gpt56w")}  # same 18 docs as the GPT runs
    return "\n\n".join(f"### 文件 T/{k}.md\n\n{v}" for k, v in T.items())


def inner_prompt(tid, inline):
    th = next(t for t in SEL if t["id"] == tid)
    p = (s3.P["inner_v1"].replace("{THREAD}", th["text"]).replace("{TID}", tid).replace("{NT}", NT)
         .replace("{BEADS}", common.beads_text()))
    if inline:
        p = p.replace("- 附件 `T_research.zip`：18 份独立的纵向聆听研究。", "- 文末附录：18 份独立的纵向聆听研究全文。")
        p += "\n\n## 附录：18 份独立的纵向聆听研究\n\n" + t_inline()
    return p


def t_inner56(tid):
    return thr.finish_json("inner_g56", tid, thr.call("inner_g56", tid, inner_prompt(tid, False), [common.t_zip()], model=thr.G56))


def t_innerG(tid):
    return thr.finish_json("inner_gem", tid, thr.call_gemini("inner_gem", tid, inner_prompt(tid, True)))


def render_inner(d):
    L = []
    for m in d.get("moments", []):
        L.append(f"[{m.get('id')}｜{m.get('where')}｜{m.get('kind')}]\n仍然活着：{m.get('alive')}\n{m.get('inner')}")
    L.append(f"[曲终回看]\n{d.get('retrospective')}")
    return "\n\n".join(L)


INNER_STAGES = {"gpt6": "inner", "gpt56": "inner_g56", "gemini": "inner_gem"}


def judge_prompt(tid):
    th = next(t for t in SEL if t["id"] == tid)
    order = list(INNER_STAGES); random.Random(f"jin-{tid}").shuffle(order)
    labels = ["甲", "乙", "丙"]; mapping = dict(zip(labels, order))
    vs = "\n\n".join(f"### 版本{l}\n\n{render_inner(thr.load(INNER_STAGES[mapping[l]], tid))}" for l in labels)
    tpl = (thr.ROOT / "prompts" / "judge_inner_v1.md").read_text(encoding="utf-8")
    return tpl.replace("{THREAD}", th["text"]).replace("{VERSIONS}", vs).replace("{BEADS}", common.beads_text()), mapping


def t_judge(tid, judge):
    p, mapping = judge_prompt(tid)
    name = f"{tid}-{judge}"
    if judge == "gemini":
        r = thr.call_gemini("judge_inner", name, p)
    else:
        r = thr.call("judge_inner", name, p, model=thr.G6 if judge == "gpt6" else thr.G56)
    ok = thr.finish_json("judge_inner", name, r)
    if ok:
        d = thr.load("judge_inner", name); d["_mapping"] = mapping; thr.save("judge_inner", name, d)
    return ok


def t_outer_m(tid, model, i):
    p = s3.P["outer_v1"].replace("{INNER}", s3.inner_text(tid))
    name = f"{tid}-{model}-{i}"
    if model == "gemini":
        r = thr.call_gemini("outer_m", name, p)
    else:
        r = thr.call("outer_m", name, p, model=thr.G56)
    return thr.finish_json("outer_m", name, r)


def mixed_cands(tid):
    allc = []
    for i in range(1, 9):
        for c in (thr.load("outer", f"{tid}-{i}") or {}).get("candidates", []):
            allc.append(dict(c, _model="gpt6", _lane=f"{tid}-{i}"))
    for m in ("gpt56", "gemini"):
        for i in range(1, 5):
            for c in (thr.load("outer_m", f"{tid}-{m}-{i}") or {}).get("candidates", []):
                allc.append(dict(c, _model=m, _lane=f"{tid}-{m}-{i}"))
    allc = [c for c in allc if c.get("text")]
    random.Random(f"mix-{tid}").shuffle(allc)
    lab = {f"C{j+1:03d}": c for j, c in enumerate(allc)}
    (thr.RUNS / "outer_m").mkdir(exist_ok=True)
    (thr.RUNS / "outer_m" / f"{tid}.mixpool.json").write_text(json.dumps(lab, ensure_ascii=False, indent=1), encoding="utf-8")
    return "\n".join(f"- {k}［{c.get('moment')}］{c.get('text')}" for k, c in lab.items())


def t_curate_mix(tid):
    p = (s3.P["curate_v1"].replace("{INNER}", s3.inner_text(tid)).replace("{CANDS}", mixed_cands(tid))
         .replace("{BEADS}", s3.segs_of(tid)))
    return thr.finish_json("curate_mix", tid, thr.call("curate_mix", tid, p))


keys = []
for th in SEL:
    tid = th["id"]
    thr.task("inner_g56", tid, lambda tid=tid: t_inner56(tid)); keys.append(("inner_g56", tid))
    thr.task("inner_gem", tid, lambda tid=tid: t_innerG(tid)); keys.append(("inner_gem", tid))
    for j in ("gpt6", "gpt56", "gemini"):
        thr.task("judge_inner", f"{tid}-{j}", lambda tid=tid, j=j: t_judge(tid, j),
                 [("inner", tid), ("inner_g56", tid), ("inner_gem", tid)]); keys.append(("judge_inner", f"{tid}-{j}"))
    lanes = []
    for m in ("gpt56", "gemini"):
        for i in range(1, 5):
            thr.task("outer_m", f"{tid}-{m}-{i}", lambda tid=tid, m=m, i=i: t_outer_m(tid, m, i), [("inner", tid)])
            keys.append(("outer_m", f"{tid}-{m}-{i}")); lanes.append(("outer_m", f"{tid}-{m}-{i}"))
    thr.task("curate_mix", tid, lambda tid=tid: t_curate_mix(tid),
             lanes + [("outer", f"{tid}-{i}") for i in range(1, 9)]); keys.append(("curate_mix", tid))

if __name__ == "__main__":
    thr.run(keys)
