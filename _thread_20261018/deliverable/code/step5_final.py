"""Final stage per thread:
merge (resume the judged-better model's own Inner session, absorbing the other model's strengths)
-> curate_final (fresh GPT-6: select Outers for the merged Inner from the full mixed pool of all models)
-> review_final x2 (fresh GPT-6 and GPT-5.6 clean reviewers)
-> inner_final (resume merge session) and outer_final (resume curate_final session)."""
import json
import thr, common
import step3_inner_outer as s3
import step4_models as s4

NT = "18"
P = {k: (thr.ROOT / "prompts" / f"{k}.md").read_text(encoding="utf-8") for k in
     ("merge_inner_v1", "curate_v1", "review_v1", "revise_inner_v1", "revise_outer_v1")}
# base model per thread = winner of the 3-judge panel (majority); other = the remaining GPT model
BASE = {"TA": ("inner", thr.G6, "inner_g56"), "TB": ("inner_g56", thr.G56, "inner"), "TC": ("inner_g56", thr.G56, "inner")}
SEL = s3.SEL


def judges_text(tid):
    out = []
    for j in ("gpt6", "gpt56", "gemini"):
        d = thr.load("judge_inner", f"{tid}-{j}")
        m = d["_mapping"]; name = {"gpt6": "作者A", "gpt56": "作者B", "gemini": "作者C"}
        c = d.get("complementary", "")
        for k, v in m.items():
            c = c.replace(k, name[v])
        for v, n in name.items():
            c = c.replace(v, n)
        out.append(f"- 评审{len(out)+1}：{c}")
    me = {"inner": "作者A", "inner_g56": "作者B"}[BASE[tid][0]]
    other = {"inner": "作者A", "inner_g56": "作者B"}[BASE[tid][2]]
    return f"（底稿的作者是{me}，另一份的作者是{other}；作者C 是第三份版本的作者，其全文不在这里，评审引用的句子可以直接参考。）\n" + "\n".join(out)


def t_merge(tid):
    base, model, other = BASE[tid]
    rv = thr.load("review", tid) or {}
    p = (P["merge_inner_v1"].replace("{BASE}", s4.render_inner(thr.load(base, tid)))
         .replace("{OTHER}", s4.render_inner(thr.load(other, tid)))
         .replace("{ORIG}", s4.inner_prompt(tid, False))
         .replace("{JUDGES}", judges_text(tid))
         .replace("{REVIEW}", json.dumps({k: v for k, v in rv.items() if k in ("issues", "cut", "overall")}, ensure_ascii=False, indent=0)))
    return thr.finish_json("merge", tid, thr.call("merge", tid, p, [common.t_zip()], model=model))


def final_inner_text(tid, stage):
    d = thr.load(stage, tid)
    lines = [f"Thread：{next(t['text'] for t in SEL if t['id'] == tid)}", ""]
    for m in d["moments"]:
        lines.append(f"[{m['id']}｜{m.get('where')}｜{m.get('kind')}] 听到：{m.get('heard')}\n仍然活着：{m.get('alive')}\nInner：{m.get('inner')}")
    return "\n\n".join(lines)


def pool_text(tid):
    lab = json.loads((thr.RUNS / "outer_m" / f"{tid}.mixpool.json").read_text(encoding="utf-8"))
    # moment ids in the pool refer to the GPT-6 Inner; give the location instead of the id
    g6 = {m["id"]: m.get("where") for m in thr.load("inner", tid)["moments"]}
    return "\n".join(f"- {k}［原写给：{g6.get(c.get('moment'), c.get('moment'))}］{c.get('text')}" for k, c in lab.items())


def t_curate_final(tid):
    segs = sorted({m.get("segment") for m in thr.load("merge", tid)["moments"] if m.get("segment") in thr.SEGS})
    p = (P["curate_v1"].replace("{INNER}", final_inner_text(tid, "merge")).replace("{CANDS}", pool_text(tid))
         .replace("{BEADS}", "\n\n".join(common.bead_block(s) for s in segs)))
    p = p.replace("下面是多位作者为它写的 Outer 候选", "下面是多位作者为它写的 Outer 候选（每条注明它原本是为哪个音乐位置写的；请对照上面的 Inner 时刻编号标注你的选择）")
    return thr.finish_json("curate_final", tid, thr.call("curate_final", tid, p))


def package(tid, inner_stage, cur_stage):
    d = thr.load(inner_stage, tid); c = thr.load(cur_stage, tid)
    out = [f"## Thread\n{next(t['text'] for t in SEL if t['id'] == tid)}", "## Inner（按时间）"]
    for m in d["moments"]:
        out.append(f"### {m['id']}｜{m.get('where')}\n听到：{m.get('heard')}\n仍然活着：{m.get('alive')}\n{m.get('inner')}")
    out.append(f"## 曲终回看\n{d.get('retrospective')}")
    out.append("## Outer")
    for j, s in enumerate(c.get("selected", []), 1):
        out.append(f"- O{j}［{s.get('moment')}］{s.get('text')}")
    return "\n\n".join(out)


def t_review_final(tid, who):
    p = (P["review_v1"].replace("{NT}", NT).replace("{PACKAGE}", package(tid, "merge", "curate_final"))
         .replace("{BEADS}", common.beads_text()))
    return thr.finish_json("review_final", f"{tid}-{who}",
                           thr.call("review_final", f"{tid}-{who}", p, [common.t_zip()], model=thr.G6 if who == "gpt6" else thr.G56))


def reviews(tid):
    out = {}
    for who in ("gpt6", "gpt56"):
        d = thr.load("review_final", f"{tid}-{who}") or {}
        out[f"审读者{1 if who == 'gpt6' else 2}"] = {k: v for k, v in d.items() if k in ("issues", "cut", "overall")}
    return out


def t_inner_final(tid):
    cf = (thr.load("curate_final", tid) or {}).get("inner_feedback", [])
    p = (P["revise_inner_v1"].replace("一位独立审读者", "两位独立审读者")
         .replace("{REVIEW}", json.dumps(reviews(tid), ensure_ascii=False, indent=0))
         .replace("{OUTER_FEEDBACK}", json.dumps(cf, ensure_ascii=False, indent=0)))
    return thr.finish_json("inner_final", tid, thr.call("inner_final", tid, p, session=thr.handle("merge", tid), model=BASE[tid][1]))


def t_outer_final(tid):
    rv = {k: [i for i in v.get("issues", []) if i.get("type") in ("Outer", "时间", "套路", "其他")] for k, v in reviews(tid).items()}
    p = (P["revise_outer_v1"].replace("审读者对你选出的 Outer 也提了意见", "两位审读者对你选出的 Outer 也提了意见")
         .replace("{INNER}", final_inner_text(tid, "inner_final")).replace("{REVIEW}", json.dumps(rv, ensure_ascii=False, indent=0)))
    prev = thr.load("curate_final", tid)
    p += ("\n\n## 你上一轮的选择\n\n```json\n" + json.dumps({k: prev.get(k) for k in ("selected", "group_check")}, ensure_ascii=False, indent=0)
          + "\n```\n\n## 原候选池\n\n" + pool_text(tid))
    return thr.finish_json("outer_final", tid, thr.call("outer_final", tid, p))


keys = []
for tid in BASE:
    thr.task("merge", tid, lambda tid=tid: t_merge(tid), [("review", tid)]); keys.append(("merge", tid))
    thr.task("curate_final", tid, lambda tid=tid: t_curate_final(tid), [("merge", tid), ("curate_mix", tid)]); keys.append(("curate_final", tid))
    for who in ("gpt6", "gpt56"):
        thr.task("review_final", f"{tid}-{who}", lambda tid=tid, who=who: t_review_final(tid, who), [("curate_final", tid)])
        keys.append(("review_final", f"{tid}-{who}"))
    thr.task("inner_final", tid, lambda tid=tid: t_inner_final(tid), [("review_final", f"{tid}-gpt6"), ("review_final", f"{tid}-gpt56")]); keys.append(("inner_final", tid))
    thr.task("outer_final", tid, lambda tid=tid: t_outer_final(tid), [("inner_final", tid)]); keys.append(("outer_final", tid))

if __name__ == "__main__":
    thr.run(keys)
