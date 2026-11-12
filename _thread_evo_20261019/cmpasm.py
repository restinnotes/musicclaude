"""Compress-then-assemble (X) vs assemble-then-compress (Y), route A (the line never saw the beads).
Both are delete-only: the model returns sentence ids, the script copies sentences verbatim.
  X: call 1 sees only the line -> keeps ~half the budget; call 2 sees only the beads -> keeps ~half; join by segment.
  Y: one call sees, per segment, the line sentences and the bead sentences together -> keeps the whole budget.
Order inside a segment is fixed for both: kept line sentences (original order), then kept bead sentences.
usage: python cmpasm.py   -> runs/cx_*/cy_*, evaluations/cmpasm/<name>.md/.json ; names ca_<X|Y>_<thread>_r<j>
"""
import json, re
import align, arts, evo, segcheck

OUT = evo.ROOT / "evaluations" / "cmpasm"
BUDGET = {"op60": 2000, "op61": 2400}
THREADS = {"op60": ["n6_op60_IB_own_r1", "n7_op60_IA_rs_r1"], "op61": ["n6_op61_IA_rs_r2", "n7_op61_IA_c4_r1"]}
SENT = re.compile(r"[^。！？!?\n]+[。！？!?」”]*")


def sents(t):
    return [s.strip() for s in SENT.findall(t) if s.strip()]


def units(work, thread):
    th = segcheck.to_json(arts.clean(evo.output(thread)), work)
    _, beads = align.beads_text(work)
    segs = []
    for s in th["segments"]:
        L = [(f"L{s['id'][1:]}.{i}", x) for i, x in enumerate(sents(s["text"].replace("**", "")), 1)]
        B = [(f"B{bid.replace('/', '.')[1:]}.{i}", x) for bid, txt in beads.items() if bid.startswith(s["id"] + "/")
             for i, x in enumerate(sents(txt), 1)]
        segs.append({"id": s["id"], "start": s["start"], "end": s["end"], "L": L, "B": B})
    return segs


def listing(segs, kinds):
    out = []
    for s in segs:
        out.append(f"## {s['id']}｜第{s['start']}–{s['end']}小节")
        for k in kinds:
            for i, x in s[k]:
                out.append(f"[{i}] {x}")
    return "\n".join(out)


COMMON = ("这是一部肖邦作品讲解视频的旁白稿素材。最终稿只能由下面编号的原句组成：你只能选择保留哪些句子，不能改写、合并或新写。"
          "请只输出一个 ```json 代码块：{\"keep\": [\"编号\", ...]}。\n\n")
LINE_X = (COMMON + "下面是一条“线”：它按段落讲一个人身上那件事怎样一步一步发生，每段说清此刻为什么会这样。请把它压缩到约 {N} 字："
          "每段保留承担“为什么此刻”的因果句，使删减后的线仍然是一条前后相连、一步推一步的过程；删去重复、铺陈和泛泛的话。每段至少保留一句。\n\n{L}")
BEAD_X = (COMMON + "下面是每段音乐的“当下体验”记录（珠子）。请把它压缩到约 {N} 字：每段保留最能让人感到此刻正在经历什么的句子，"
          "删去重复的意思。每段至少保留一句。\n\n{L}")
JOINT_Y = (COMMON + "下面每段有两种句子：L 开头的是“线”（讲那件事此刻走到哪一步、为什么），B 开头的是“珠子”（此刻的当下体验）。"
           "最终稿里每段会先放保留的 L 句，再放保留的 B 句。请把全文压缩到约 {N} 字：让最终稿读起来是一篇连贯的文章——"
           "线要仍然是一条前后相连、一步推一步的主干，珠子句提供此刻可感的体验，两者在同一段里要相合；删去重复、铺陈和泛泛的话。"
           "每段至少保留一句 L 和一句 B。\n\n{L}")


def keep(rid, msg):
    r = evo.call(rid, msg, prompt_text=msg[:400], meta={"stage": "cmpasm"})
    return set(evo.parse_json(r)["keep"]) if r else None


def render(name, work, thread, segs, kept):
    md, js = [f"# {name}", ""], []
    for s in segs:
        L = [x for i, x in s["L"] if i in kept]; B = [x for i, x in s["B"] if i in kept]
        js.append({"id": s["id"], "start": s["start"], "end": s["end"], "line": L, "bead_excerpts": B})
        md += [f"### 第{s['start']}–{s['end']}小节", "", "".join(L), ""] + [f"> 【珠子】{x}" for x in B] + [""]
    n = sum(len(x) for s in js for x in s["line"] + s["bead_excerpts"])
    nl = sum(len(x) for s in js for x in s["line"])
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.md").write_text("\n".join(md), encoding="utf-8")
    (OUT / f"{name}.json").write_text(json.dumps({"thread": thread, "work": work, "chars": n, "line_chars": nl, "segments": js},
                                                 ensure_ascii=False, indent=1), encoding="utf-8")
    print(name, "chars", n, "line", nl, "bead", n - nl, flush=True)


def one(work, thread, meth, j):
    segs = units(work, thread); N = BUDGET[work]; tag = f"{thread}_r{j}"
    if meth == "X":
        kl = keep(f"cx_L_{tag}", LINE_X.replace("{N}", str(N // 2)).replace("{L}", listing(segs, ["L"])))
        kb = keep(f"cx_B_{tag}", BEAD_X.replace("{N}", str(N // 2)).replace("{L}", listing(segs, ["B"])))
        kept = (kl or set()) | (kb or set()) if kl and kb else None
    else:
        kept = keep(f"cy_{tag}", JOINT_Y.replace("{N}", str(N)).replace("{L}", listing(segs, ["L", "B"])))
    if kept:
        render(f"ca_{meth}_{tag}", work, thread, segs, kept)


if __name__ == "__main__":
    jobs = [(f"{m}_{t}_{j}", (lambda w=w, t=t, m=m, j=j: one(w, t, m, j)))
            for w, ts in THREADS.items() for t in ts for m in "XY" for j in (1, 2)]
    evo.run_parallel(jobs, 16)
