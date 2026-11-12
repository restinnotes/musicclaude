"""DAG N09v (11-01): sentence-shape variety. User: "因为你前面都这么说了，所以他后面也会仿照前面这么说 … 每个句子看起来读起来都
特别类似 … 不会去用很多不同的表达方法"; four models (sty_*: GPT-6, GPT-5.6, Gemini 3.8, Argon) agreed on: start from the
matter / time / a thought / a result instead of "他"; let the thought itself appear instead of reporting 他想/他怕; mix
long and short; keep about a third plain; inner speech rare; no colloquial fillers, no new images or events.
So the SCRIPT assigns each item a shape (models do not choose, so they cannot drift back into one template), with rules:
about 1/3 "plain"; adjacent items never share a shape; at most one 他-initial item per segment among the rewritten ones;
"direct thought" at most once per ~6 items and never in 没在想 segments; 还说不清 segments get no "result-first" shape.
The writer re-says each item in its assigned shape, same meaning and cites.  ids vy_<w>_<out>.
Also prints a skeleton meter (他-initial share, 也 / 越…越 / 想…又/怕 per item) before and after.
usage: python v6vary.py <base> <out>"""
import json, random, re, sys
import covjudge, evo, v6fix as V
from v6gen import build, gloss_text

SHAPES = {
    "plain": "保持平直：意思原样，只在不通顺处轻轻整理；可以就用“他……”起句。",
    "topic": "换起句支点：不从“他”起句，从这件事、某个对象、一段时间或一个已经发生的结果起句（汉语可以省掉主语），人的反应跟在后面。",
    "thought": "让念头直接出现：不写“他想/他怕/他明白”，直接写出那个念头、那个问题本身（可以是半句自问），再接上他怎么处理它。",
    "split": "长短交替：把这条拆成一长一短两句，或用一个很短的句子收住；短句要落在这条最要紧的那个意思上。",
}
P = """下面是肖邦{NAME}的一条“线”：一个人在这首曲子里经历的一件事，按段写成条目。意思和衔接都已经定好，现在只改说法：几乎每条都是“他＋心理动词＋判断”，读多了像心理状态汇报。
每条都已经指定了一种说法（见每条的【说法】），请严格按指定的说法重说这一条，不要换成别的说法，也不要模仿相邻条目的句式：
{SHAPES}

必须守住：
- 每条原来的意思一点不能变：不加原文没有的事件、人物、场景、画面、动作，不丢掉某条独有的意思；可能的不改成确定的，相关的不改成因果。下面【Center 各部分指什么】里的意思要守住。
- 不用“说到底”“其实吧”“偏偏”“掏心掏肺”这类口语填充词或夸张说法；不写声音、画面、身体感受。
- 字数和原来大致相当；每条的 cite 原样保留；段落、条目数量和顺序不变。

【Center 各部分指什么】
{GLOSS}

【线】（json；每条带指定的【说法】）
{LINE}

只输出改好的 json：
```json
{{"segments": [{{"sec": "S01", "items": [{{"text": "……", "cite": []}}]}}]}}
```"""


def meter(g):
    T = [it["text"] for s in g["segments"] for it in s["items"]]; n = max(1, len(T))
    return {"条目": len(T), "他起句": round(sum(t.startswith("他") for t in T) / n, 2), "也/条": round(sum(t.count("也") for t in T) / n, 2),
            "越…越/条": round(sum(len(re.findall(r"越.{0,10}越", t)) for t in T) / n, 2), "想…又/怕/条": round(sum(len(re.findall(r"想.{0,14}(又|却|可|但).{0,4}怕", t)) for t in T) / n, 2)}


def assign(g, seed):
    rnd = random.Random(seed); plan = {}; k = 0; last = None; since_thought = 99
    for s in g["segments"]:
        rel = s.get("relation") or ""
        for it in s["items"]:
            k += 1; since_thought += 1
            opts = ["plain", "topic", "thought", "split"]
            if rel == "没在想" or since_thought < 6:
                opts.remove("thought")
            if last in opts and len(opts) > 1:
                opts.remove(last)
            w = {"plain": 1.0, "topic": 1.2, "thought": 0.7, "split": 0.8}
            sh = rnd.choices(opts, weights=[w[o] for o in opts])[0]
            if sh == "thought":
                since_thought = 0
            plan[it["id"]] = sh; last = sh
    return plan


def run(base, out):
    def piece(w):
        g = V.graph_of(w, base); plan = assign(g, f"vy{w}{out}")
        line = {"segments": [{"sec": s["sec"], "relation": s.get("relation"),
                              "items": [{"id": it["id"], "【说法】": plan[it["id"]], "text": it["text"],
                                         "cite": [b["from"] for b in s["because"] if b.get("to") == it["id"] and b.get("rel") == "引用"]}
                                        for it in s["items"]]} for s in g["segments"]]}
        rid = f"vy_{w}_{out}"
        if not evo.done(rid):
            msg = P.format(NAME=covjudge.NAME[w], SHAPES="\n".join(f"- {k}：{v}" for k, v in SHAPES.items()), GLOSS=gloss_text(w),
                           LINE=json.dumps(line, ensure_ascii=False, indent=0))
            evo.call_argon_direct(rid, msg, meta={"stage": "v6-vary"})
        G, _ = build(w, base, out, V.parse(rid) or {})
        from collections import Counter
        print(w, out, "说法分配", dict(Counter(plan.values())), "| 前", meter(g), "| 后", meter(G), flush=True)
    evo.run_parallel([(w, (lambda w=w: piece(w))) for w in ("op60", "op61")], 2)


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2])
