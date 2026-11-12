"""Advisor round 2: reader test for Center / History visibility (model readers stand in for people).
  qbank : GPT-6 builds, from the original + skeleton, per line: a Center rubric (0-3) and 6 History MCQs about long-range
          links; questions describe moments by content (no bar numbers); 4 plausible options + E "稿子里没写到".
  read  : a fresh reader (gpt6, gpt56) sees ONE version only; free Center summary; MCQ answers (E if not stated);
          1-7: 像同一件事一路发展 / 需要自己补原因
  grade : GPT-6 scores the Center summaries with the rubric.
versions: A tls_ (show+link), B tlh_ (headline only), C tlx_ (A, middle shuffled, bars hidden), F7, cr, st.
usage: python readertest.py qbank | read <eid> | grade <eid>"""
import json, random, re, sys
from collections import defaultdict
from statistics import mean
from pathlib import Path
import arts, causal, evo, plain

OUT = evo.ROOT / "evaluations" / "reader"
QB = ("下面是一篇“线”的原稿和它的骨架。我们要测：别人写的各种压缩版，能不能让一个没看过原稿的读者读出这条线的整体（Center）和前后因果（History）。"
      "请出题：\n1. center_rubric：读者用一两句话概括“这个人从开头到结尾一直在处理什么、结尾什么变了、什么还没解决”，给出 0/1/2/3 分各自的判断标准"
      "（0 说不出共同问题；1 只说出泛泛的情绪；2 说清这件事的核心矛盾；3 还说清结尾的变化与未解之处）。\n"
      "2. mcq：6 道选择题，考跨段的前后因果——较早的哪件经历，怎样导致或改变了后来的某个反应。至少 4 道考相隔两段以上的联系。"
      "题干用内容描述那个时刻（如“他已经能管住情绪之后，为什么仍然焦躁？”），不要写小节号。"
      "每题 A–D 四个选项，只有一个是原稿的因果；另外三个都必须是看似合理的心理解释——如果文字没交代真正原因，读者很可能会信——不要写明显错误或极端的选项。"
      "E 固定为“稿子里没写到”。答案位置随机分布。\n"
      "只输出一个 ```json 代码块：{\"center_rubric\": {\"0\": \"…\", \"1\": \"…\", \"2\": \"…\", \"3\": \"…\"}, \"mcq\": [{\"id\": 1, \"q\": \"…\", "
      "\"options\": {\"A\": \"…\", \"B\": \"…\", \"C\": \"…\", \"D\": \"…\", \"E\": \"稿子里没写到\"}, \"answer\": \"A\", \"link\": \"较早经历 → 后来反应（简述）\"}]}\n\n")
RD = ("你是一位普通读者，没有看过任何原稿或分析。下面是一份讲解视频用的稿子。请只根据稿子写出的内容回答，不要用常识替稿子补全。\n"
      "1. summary：用一两句话说，这个人从开头到结尾一直在处理什么事？到了结尾，什么改变了，什么还没有解决？\n"
      "2. 回答下面的选择题。稿子里没有写出这层原因，就选 E，不要猜。\n"
      "3. one_thing（1–7）：这些段落读起来像同一件事一路发展（7 = 非常像）。\n"
      "4. fill_in（1–7）：为了理解人物，我需要自己补出文字没说清的原因（7 = 经常需要）。\n"
      "只输出一个 ```json 代码块：{\"summary\": \"…\", \"answers\": {\"1\": \"A\"}, \"one_thing\": 1, \"fill_in\": 1}\n\n")
GR = ("按下面的评分标准，给读者的概括打 0–3 分。只输出一个 ```json 代码块：{\"score\": 0, \"why\": \"…\"}\n\n")


def threads():
    return [(t, w) for w, ts in plain.THREADS.items() for t in ts]


def versions(t):
    return {"A_显示层": f"tls_{t}_r1", "A2_显示层v2": f"tl2s_{t}_r1", "B_只有主句": f"tlh_{t}_r1", "C_打乱中段": f"tlx_{t}_r1",
            "F7": f"fm_F7_{t}_r1", "按需显示": f"cr_{t}", "结构化全稿": f"st_{t}_r1"}


def make_variants(t):
    j = json.loads((evo.ROOT / "evaluations" / "twolayer" / f"tl_{t}_r1.json").read_text(encoding="utf-8"))
    b = [f"**{j['center']}**", ""] + sum(([f"### {s['bars']}", "", f"**{s['show']['headline']}**", ""] for s in j["segments"]), [])
    segs = j["segments"][:]; mid = segs[1:-1]; random.Random(t).shuffle(mid); segs = [segs[0]] + mid + [segs[-1]]
    c = [f"**{j['center']}**", ""] + sum(([f"### 第{i + 1}段", "", f"**{s['show']['headline']}**"] + ([s["show"]["link"]] if s["show"]["link"] else []) + [""]
                                          for i, s in enumerate(segs)), [])
    for rid, lines in ((f"tlh_{t}_r1", b), (f"tlx_{t}_r1", c)):
        d = evo.RUNS / rid; d.mkdir(exist_ok=True); (d / "output.txt").write_text("\n".join(lines), encoding="utf-8")
        (d / "call.log").write_text(json.dumps({"note": f"derived from tl_{t}_r1 for the reader test"}), encoding="utf-8")


def qtext(qb):
    return "\n".join(f"{q['id']}. {q['q']}\n" + "\n".join(f"   {k}. {v}" for k, v in q["options"].items()) for q in qb["mcq"])


if __name__ == "__main__":
    ph = sys.argv[1]; OUT.mkdir(parents=True, exist_ok=True); jobs = []
    if ph == "qbank":
        for t, w in threads():
            sk = (evo.ROOT / "evaluations" / "skeleton" / f"{t}.json").read_text(encoding="utf-8")
            jobs.append((f"qb_{t}", (lambda t=t, sk=sk: evo.call(f"qb_{t}", QB + "========== 原稿 ==========\n" + arts.clean(evo.output(t)) + "\n\n========== 骨架 ==========\n" + sk,
                                                              prompt_text=QB, meta={"stage": "qbank"}))))
        evo.run_parallel(jobs, 4)
        for t, w in threads():
            if evo.done(f"qb_{t}"):
                (OUT / f"qb_{t}.json").write_text(json.dumps(evo.parse_json(evo.output(f"qb_{t}")), ensure_ascii=False, indent=1), encoding="utf-8")
    elif ph == "read":
        eid = sys.argv[2]
        for t, w in threads():
            make_variants(t); qb = json.loads((OUT / f"qb_{t}.json").read_text(encoding="utf-8"))
            for lab, n in versions(t).items():
                for jn, model in (("gpt6", evo.G6), ("gpt56", evo.G56)):
                    rid = f"rd_{eid}_{n}_{jn}"
                    msg = RD + "========== 选择题 ==========\n" + qtext(qb) + "\n\n========== 稿子 ==========\n" + causal.text(n)
                    if not evo.done(rid):
                        jobs.append((rid, (lambda rid=rid, msg=msg, model=model: evo.call(rid, msg, prompt_text=RD, model=model, meta={"stage": "reader"}))))
        evo.run_parallel(jobs, 6)
    elif ph == "grade":
        eid = sys.argv[2]; rows = []
        for t, w in threads():
            qb = json.loads((OUT / f"qb_{t}.json").read_text(encoding="utf-8"))
            for lab, n in versions(t).items():
                for jn in ("gpt6", "gpt56"):
                    r = evo.output(f"rd_{eid}_{n}_{jn}")
                    if not r:
                        continue
                    a = evo.parse_json(r); ans = {str(k): str(v).strip()[:1] for k, v in a.get("answers", {}).items()}
                    corr = sum(ans.get(str(q["id"])) == q["answer"] for q in qb["mcq"]); nE = sum(v == "E" for v in ans.values())
                    gid = f"gr_{eid}_{n}_{jn}"
                    g = evo.output(gid) or evo.call(gid, GR + "========== 评分标准 ==========\n" + json.dumps(qb["center_rubric"], ensure_ascii=False, indent=1)
                                                    + "\n\n========== 读者概括 ==========\n" + a.get("summary", ""), prompt_text=GR, model=evo.G56, meta={"stage": "reader_grade"})
                    rows.append({"thread": t, "version": lab, "name": n, "reader": jn, "mcq_correct": corr, "mcq_n": len(qb["mcq"]), "mcq_E": nE,
                                 "center": evo.parse_json(g).get("score") if g else None, "one_thing": a.get("one_thing"), "fill_in": a.get("fill_in"),
                                 "chars": len(causal.text(n))})
        (OUT / f"{eid}_rows.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
        by = defaultdict(list)
        for r in rows:
            by[r["version"]].append(r)
        print(f"{'版本':10s} {'因果题正确率':>8s} {'选E(没写到)':>10s} {'Center(0-3)':>10s} {'像一件事':>6s} {'要自己补':>6s} {'字数':>5s}")
        for v in ["A_显示层", "A2_显示层v2", "B_只有主句", "C_打乱中段", "F7", "按需显示", "结构化全稿"]:
            rs = by.get(v, [])
            if rs:
                m = lambda k: mean([float(x[k]) for x in rs if x.get(k) is not None] or [float('nan')])
                print(f"{v:10s} {100 * mean([x['mcq_correct'] / x['mcq_n'] for x in rs]):7.0f}% {100 * mean([x['mcq_E'] / x['mcq_n'] for x in rs]):9.0f}% "
                      f"{m('center'):10.2f} {m('one_thing'):6.1f} {m('fill_in'):6.1f} {m('chars'):5.0f}")
