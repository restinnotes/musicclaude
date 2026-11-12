"""11-02 block for 迭代准则: the one-shot writers (P1) get the content right but run long and read like explanation. One whole-line
rewrite by Argon: same meaning and order, one sentence per item, about half the length, plain speech. Blind vs mainline decides
whether it earns a place. ids pp_<w>_<out>.  usage: python plainpass.py <base tag> <out tag> [ratio=0.5] [writer=argon|gpt]"""
import json, os, sys
import covjudge, evo, v6fix as V
from v6gen import build
from v6human import line_json

P = """下面是一条“线”：一个人在{NAME}里经历的一件事，按音乐段落分段，每段几条要点。这条线的内容是对的：前后有逻辑，读得出他此刻为什么这样。问题是太长，读起来像有人在解释他的心理。

请把它改写得短、像人话：
1. 意思和先后不变，不加新内容；每段他和整件事的关系不变；每条的 cite 照原来的填。
2. 每条一句话，只说一件事。这一段发生得少就写得短。全篇压到原来的 {PCT} 左右（约 {N} 字）。
3. 前面已经说过的不再完整说一遍，提一下就够。能合并的条目就合并，但每段至少留一条。
4. 像一个人平平常常讲自己的经历：能直接说他想要什么、怕什么、舍不得什么，就不要用抽象的说法概括；不用解释他意识到了什么；不用工整的对照句和总结句撑结构；不必要的否定不写。
5. 不加口语填充词，不加新的事件、物件、对白。
6. 连着读下来，每一句都能自然接上前一句。

【Center 不写进条目，只供参考】{CENTER}

【线】（json）
{LINE}

只输出 json：
```json
{{"segments": [{{"sec": "S01", "items": [{{"text": "……", "cite": []}}]}}]}}
```"""


def piece(w, base, out, ratio, writer):
    g = V.graph_of(w, base); C = sum(len(i["text"]) for s in g["segments"] for i in s["items"])
    rid = f"pp_{w}_{out}"
    msg = P.format(NAME=f"肖邦{covjudge.NAME[w]}", PCT=f"{int(ratio * 100)}%", N=int(C * ratio // 50 * 50), CENTER=g["center"], LINE=line_json(g))
    if not evo.done(rid):
        if writer == "argon":
            evo.call_argon_direct(rid, msg, meta={"stage": "plainpass"})
        else:
            evo.call(rid, msg, model=evo.G6, meta={"stage": "plainpass"})
    e = V.parse(rid)
    G, kept = build(w, base, out, e)
    n = sum(len(i["text"]) for s in G["segments"] for i in s["items"])
    print(w, out, "字数", C, "→", n, "没写出的段", kept, flush=True)
    d = json.loads((V.OUT / f"{w}_{out}.json").read_text(encoding="utf-8"))
    d["base"] = f"{base} → {out}（整条压缩加人话，{writer}，目标 {int(ratio * 100)}%）"
    json.dump(d, open(V.OUT / f"{w}_{out}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    base, out = sys.argv[1], sys.argv[2]
    ratio = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
    writer = sys.argv[4] if len(sys.argv) > 4 else "argon"
    evo.run_parallel([(w, (lambda w=w: piece(w, base, out, ratio, writer))) for w in ("op60", "op61")], 2)
