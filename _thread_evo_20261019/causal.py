"""Advisor exp 3: blind causal-sufficiency test. The judge sees ONE line (no original, no analysis) and, per segment,
answers: what changed / why now / which earlier experience still acts and how / what it leaves for next; then scores
each 0-2 (0 can't answer or only restates; 1 vague, concept-repeating or index-only; 2 concrete mechanism that drives on).
usage: python causal.py <eid> <name>[,<name>...]   names: run ids, or stateinc/structured ids (read from their .md)"""
import json, sys
from pathlib import Path
import arts, evo, seg

EV = evo.ROOT / "evaluations"
Q = ("你没有看过这首曲子的任何分析，也没有原稿。下面是一份讲解视频用的“线”：它按段落讲一个人身上的一件事怎样一步步发生。"
     "请只凭这份稿子，逐段回答四个问题，并给每个回答打分：\n"
     "1. change：这一段里，他具体发生了什么心理变化？\n2. why：为什么他现在会产生这个变化？\n"
     "3. history：哪一段较早的经历仍在影响他？具体怎样影响？（第一段写“无”）\n4. pressure：这个变化把什么问题留给了下一段？（最后一段写它怎样收住）\n"
     "打分：0 = 无法回答，或只能复述本段字面；1 = 看到了，但只是重复概念、列举段号，或因果仍含糊；2 = 能说出具体的心理机制，并解释它怎样推动后续变化。"
     "严格按稿子写出的内容打分，不要替作者补全。\n"
     "最后另给两项 1–10 分：glance（扫一眼能否立刻看到实打实的内容）、natural（像人话，没有 AI 套路句和抽象空话）。\n"
     "只输出一个 ```json 代码块：{\"segments\": [{\"bars\": \"…\", \"change\": \"…\", \"why\": \"…\", \"history\": \"…\", \"pressure\": \"…\", "
     "\"s\": [2, 2, 1, 2]}], \"glance\": 1, \"natural\": 1, \"weakest\": \"最难回答‘为什么’的一两段及原因\"}\n\n========== 稿子 ==========\n")


def text(n):
    for d in ("stateinc", "structured", "st4", "tgraph2"):
        p = EV / d / f"{n}.md"
        if p.exists():
            return p.read_text(encoding="utf-8").split("\n", 2)[2]
    return arts.clean(evo.output(n))


def run(eid, names):
    jobs = []
    for n in names:
        for jn, model in (("gpt6", evo.G6), ("gpt56", evo.G56)):
            rid = f"cz_{eid}_{n}_{jn}"
            if not evo.done(rid):
                jobs.append((rid, (lambda rid=rid, n=n, model=model: evo.call(rid, Q + text(n), prompt_text=Q, model=model, meta={"stage": "causal"}))))
    evo.run_parallel(jobs, 6)
    rows = []
    for n in names:
        for jn in ("gpt6", "gpt56"):
            r = evo.output(f"cz_{eid}_{n}_{jn}")
            if not r:
                continue
            j = evo.parse_json(r); S = [s.get("s", [0, 0, 0, 0]) for s in j["segments"]]
            k = len(S) or 1
            rows.append({"name": n, "judge": jn, "change": sum(x[0] for x in S) / k, "why": sum(x[1] for x in S) / k,
                         "history": sum(x[2] for x in S[1:]) / max(1, k - 1), "pressure": sum(x[3] for x in S) / k,
                         "why2_share": sum(x[1] == 2 for x in S) / k, "glance": j.get("glance"), "natural": j.get("natural"),
                         "chars": len(text(n)), "weakest": j.get("weakest")})
    out = EV / eid; out.mkdir(parents=True, exist_ok=True)
    (out / "rows.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    from collections import defaultdict
    from statistics import mean
    by = defaultdict(list)
    for r in rows:
        by[r["name"]].append(r)
    for n, rs in by.items():
        g = lambda k: mean([float(r[k]) for r in rs if r.get(k) is not None])
        print(f"{n:34s} 字{rs[0]['chars']:5d} 变化{g('change'):.2f} 为什么{g('why'):.2f} 历史{g('history'):.2f} 下一步{g('pressure'):.2f} "
              f"为什么满分段{100*g('why2_share'):.0f}% 一眼{g('glance'):.1f} 人话{g('natural'):.1f}")


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2].split(","))
