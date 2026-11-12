"""Advisor for the iteration loop (user 10-23: "尽量多做迭代 … 除了你自己评也可以再参考一些gpt的意见"). A GPT reads one round's
finished products (line graph, screen plan) with the judges' reasons and proposes at most 3 concrete prompt changes. Its
proposals are advice, not orders: each is checked against THREAD_SPEC (§七 7 "照单全收评审建议" is a known failure) before use.
usage: python advisor.py <T> <op60|op61>   -> evaluations/beam/<T>/advice.json"""
import json, sys
import beam, evo, node2b, seq

P = ("你是这个项目的顾问。我们在为{WORK}做随音乐播放的讲解视频，内容有两条：珠子（听这段音乐的感受，原文不改，多种听法并存）和线"
     "（一张关系图：每段 1–3 条短条目，说明这些感受为什么此刻出现，理由来自这个人前面的经历，不是音乐事件；跨段箭头只连真正的前因）。\n"
     "线是这样产生的：先有多篇不看珠子写成的整稿作为候选；再从第一段往后逐段综合，每段看这一段的珠子和各候选，写 2–3 种写法，"
     "始终保留 3 条路，由另一个模型剪枝；全曲写完由两位评委选出一条，再润色措辞。最后把线和珠子排成每段几屏。\n\n"
     "用户在意的（按重要性）：线要真的解释珠子写的感受；读起来是一件事，不是两块内容；人话、简洁，句式不单调，不用抽象的姿态词；"
     "不编情节、不编人物前史、不编“找办法—失效—再找”的心理戏；开头可以还说不清，不能把主题说死；珠子的多种听法不能被线压成一种。\n\n"
     "下面是这一轮的成品和评委意见。请：\n"
     "1. 指出成品里最影响质量的 3 个问题，每个都举出具体的段和原句。\n"
     "2. 针对每个问题，提出一处具体的改法：改哪一步（逐段综合 / 剪枝评委 / 终评 / 润色 / 屏幕排法），怎么改提示词（写出要加或要换的那句话），"
     "以及这样改可能带来的副作用。\n"
     "3. 只提有把握的；不要建议给模型示例句（它会照抄句式），不要建议删内容来换简洁。\n\n"
     "最后只输出一个 ```json 代码块：\n"
     '{"problems": [{"what": "…", "where": "第4段：原句…", "fix_step": "逐段综合", "fix": "要加或要换的提示词原文", "risk": "…"}]}\n\n'
     "# 这一轮的关系图\n\n{GRAPH}\n\n# 屏幕排法（节选前 4 段）\n\n{JOIN}\n\n# 评委意见（理由节选）\n\n{JUDGES}")


def judges_text(T, work):
    out = []
    h2h = sorted(beam.OUT.glob(f"h2h_{work}_*{T}.json"))[-1:]   # the latest head-to-head that ends with this round
    for f in (*h2h, beam.OUT / T / "final.json", beam.OUT / T / "joinjudge.json"):
        if not f.exists():
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        for rid, r in list(d.items())[:2]:
            for k, v in (r.get("paths") or r.get("layouts") or {}).items():
                if k in (f"beam{T}", "plan") or f.name == "final.json":
                    out.append(f"[{f.stem}·{rid}·{k}] " + "；".join(f"{m}:{(v.get(m) or {}).get('why', '')}" for m in v if isinstance(v.get(m), dict)))
    return "\n".join(out)[:12000]


if __name__ == "__main__":
    T, work = sys.argv[1], sys.argv[2]
    beam.setup(work)
    graph = (beam.OUT / T / "graph.md").read_text(encoding="utf-8")
    jp = beam.OUT / T / "join.md"
    join = "\n".join(jp.read_text(encoding="utf-8").split("\n---\n")[:5]) if jp.exists() else "（还没有）"
    rid = f"adv{T}"
    if not evo.done(rid):
        node2b.job(rid, beam.fill(P, work, GRAPH=graph, JOIN=join, JUDGES=judges_text(T, work)), {"stage": "advisor"}, w="g6")[1]()
    r = seq.parse(evo.output(rid)) or {}
    (beam.OUT / T / "advice.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    for p in r.get("problems") or []:
        print("-", p.get("what"), "|", p.get("where", "")[:60], "|", p.get("fix_step"), "|", p.get("fix", "")[:120], flush=True)
