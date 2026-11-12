"""Node 2 round D12 = P1 with lenses (10-23, user: "大刀阔斧一点"). D10/D11 drafts explain the whole piece with one abstract
opposition (安稳/投入, 满足/不足, 需要/安顿) and miss whole sources of feeling (time, memory, loss, the self stepping back);
coverage is pool-level, so the pool needs drafts that really start from different places.
P1 drops P0's verbatim text (its "同一件难以安顿的事" and satisfaction examples pull towards that one opposition) but keeps
its core: earlier lived experience gives later feelings their meaning, and later experience re-means earlier ones.
Each draft gets one lens, a question to ask first in every segment, with an explicit "if it doesn't apply, write what is true":
  f = free, t = time (passing / gone / remembering), p = the other person (here or not, near or far, known or not),
  s = the self (more self-concerned, or stepping back into something larger).
One call per piece (chained writing did not cover more in D10). Mostly gpt6 (it covered more than gpt56 in D10).
ids: d12{f|t|p|s}{6|56}_<work>_r<j>.  usage: python draft12.py"""
import json
import draft10 as d, evo, node2b, segcheck

NAME = {"op60": "肖邦《船歌》Op.60", "op61": "肖邦《幻想波兰舞曲》Op.61"}
P1 = """请为{NAME}写一条 Thread。

Thread 是什么：把整首音乐理解成一件持续发生在一个人身上的事。前面真实经历过的快乐、不安、期待和认识，会让后面的感受有特定的意义；后面的经历，也会让前面的经历显出新的意思。Thread 要回答的是：经历过前面那些的人，为什么此刻会这样感受。

按小节数 {BOUNDS} 分段（最后一个数只是全曲结束的边界，不是一个小节）。

写法：
1. 每一段先想清楚这一段的感受：它和前面有什么不同？有哪些感受同时成立？以前出现过的东西，在这里分量有没有变？不必只挑最主要的一种。
2. 感受的来源很多，不要只用“想要什么、得到了什么、还缺什么”来解释。它也可能来自时间（正在过去、已经回不来、像在回忆），来自另一个人在或不在，来自比自己更大的东西（自己暂时退到后面），来自身体和处境本身。每一段都重新想：这里的感受来自哪里。{LENS}
3. 再从前面已经发生的经历出发找理由。一个理由能解释几种感受，就不要拆成几步；几个相容的理由可以并存；这一段也可以只是前面的延续，没有新的认识。
4. 不要用一个对立（比如安稳与投入、满足与不足、亲近与自我保护）解释全曲。如果一个理由放到别的段落也同样成立，它还没有说出这一段的原因。
5. 不要先编好一套故事再让音乐配合它。不编自我劝说、想通、下决心，不编外部事件、物件、场景或对白；不把音乐的变化当成他心里变化的原因。开头不交代他的经历、性格、习惯，不提前说出主题，任何一段都不预告后面。但不编前史，不等于感受只能发生在当下：此刻的感受本身可以带着回忆或失去的性质，这不需要编出具体发生过什么。
6. 用普通人一遍能听懂的话写。说清他在乎的具体是什么（例如“这一刻会过去”“那个人此刻就在身边”），不要只用“需要、安顿、满足、投入、完整”这类抽象词代替。不要描写声音、旋律、和声、意象，不写哲理总结。

从第一段写到最后一段，每段写五项。只输出一个 json 代码块：
```json
{"sections": [{"bars": "1–3", """ + d.FIELDS + """}]}
```
"""
LENS = {"f": "",
        "t": "\n这一篇写的时候，每段先问一句：这里的感受和时间有什么关系——什么正在过去、什么已经回不来、什么像在回忆里？问过以后，如果这一段和时间无关，就照实按别的来源写。",
        "p": "\n这一篇写的时候，每段先问一句：这里的感受和另一个人有什么关系——那个人在不在、近还是远、他的心意能不能被对方知道？问过以后，如果这一段和别人无关，就照实按别的来源写。",
        "s": "\n这一篇写的时候，每段先问一句：这里的感受和他自己有什么关系——他是更在意自己，还是自己退到了后面、被比自己更大的东西带走？问过以后，如果这一段不是这样，就照实按别的来源写。"}
CELLS = [(l, "6", j) for l in LENS for j in (1, 2, 3)] + [(l, "56", 1) for l in LENS]


def msg(w, lens):
    segs = d.segs(w)
    bounds = ", ".join(str(s["start"]) for s in segs) + f", {segs[-1]['end'] + 1}"
    return P1.replace("{NAME}", NAME[w]).replace("{BOUNDS}", bounds).replace("{LENS}", LENS[lens])


def one(name, w, mdl, lens):
    for rid in (name, name + "_x"):
        if not evo.done(rid):
            node2b.job(rid, msg(w, lens), {"stage": "d12", "work": w, "lens": lens}, w=mdl)[1]()
        r = d.parse(rid) if evo.done(rid) else None
        xs = (r or {}).get("sections") or []
        if len(xs) == len(d.segs(w)) and all(x.get("thread") for x in xs):
            return d.save(name, [x | {"sec": s["id"], "bars": f"{s['start']}–{s['end']}"} for x, s in zip(xs, d.segs(w))])
    print(name, "FAILED (sections != segments)", flush=True)


if __name__ == "__main__":
    jobs = []
    for w in d.W:
        for lens, m, j in CELLS:
            name = f"d12{lens}{m}_{w}_r{j}"
            if not (d.OUT / f"{name}.json").exists():
                jobs.append((name, lambda name=name, w=w, mdl=("g6" if m == "6" else "g56"), lens=lens: one(name, w, mdl, lens)))
    evo.run_parallel(jobs, 32)
