"""DAG N09w (11-01, user: "也觉得骄傲 没有人提出这个也字吗 … 他经常容易出现这种很莫名其妙的也"): word-level proofreading.
The open review reads sentences and the whole; it does not ask of every word whether it is needed. Here two judges read
like a copy editor, item by item, and list only word-level edits (delete / replace a word or a few characters) — no
sentence rewrites, no category list. The edits are applied by the SCRIPT as exact replacements inside the item (a quote
that is not found verbatim is skipped), so meaning and structure cannot drift; an edit proposed by both judges, or by one
judge and not contradicted, is applied. ids wd_<w>_<j>_<tag>.  usage: python v6word.py <base> <out>"""
import json, sys
import covjudge, evo, os, v6fix as V

EDITORS = os.environ.get("WORD_EDITORS", "g6,g56").split(",")   # 11-01: gem / argon allowed while the GPT routes are protected

P = """下面是一段中文，按条目排列（方括号里是条目编号）。它要读起来像一个人平平常常地讲自己的经历。

请你像出版社的文字编辑做最后一遍逐字校对：一条一条、一个字一个字地读，问每个字词是不是必要、是不是用得自然准确。
只挑字词层面的问题：删掉以后意思不变、读起来更干净的字；用得不准或多余的虚词、副词、连接词；不自然的搭配里只需换一两个词就能修好的地方。
还要看全篇：同一个虚词、副词或句式在许多条里反复出现（例如可有可无的“也”“还是”“又”，一再出现的“越……越……”“越发”），单看不错、连读就单调或像套话的，也要逐处处理：删掉那几个字，或换成别的说法，只改那几个字，留下确实需要的。
不要改句子结构，不要重写整句，不要改意思，不要为了凑数挑毛病；没问题的条目不用提。

每处给出：条目编号；原文里要改的那一小段（原样照抄，越短越好，但要足以在这一条里唯一定位，通常 2–12 个字）；改成什么（删除就写空字符串）；一句理由。

{TEXT}

只输出 json：
```json
{{"edits": [{{"id": "S01-2", "from": "原文片段", "to": "改后片段", "why": "…"}}]}}
```"""


def text(g):
    return "\n".join(f"[{it['id']}] {it['text']}" for s in g["segments"] for it in s["items"])


def run(base, out):
    jobs = []
    for w in ("op60", "op61"):
        g = V.graph_of(w, base)
        for j in EDITORS:
            rid = f"wd2_{w}_{j}_{base}"
            if not evo.done(rid):
                msg = P.format(TEXT=text(g))
                fn = {"gem": evo.call_gemini_direct, "argon": evo.call_argon_direct}.get(j)
                jobs.append((rid, (lambda rid=rid, msg=msg, j=j, fn=fn: fn(rid, msg, meta={"stage": "v6-word"}) if fn else evo.call(rid, msg, model=V.JUDGES[j], meta={"stage": "v6-word"}))))
    evo.run_parallel(jobs, 4)
    md = [f"# 逐字精读：{base} → {out}", ""]
    for w in ("op60", "op61"):
        g = json.loads(json.dumps(V.graph_of(w, base))); items = {it["id"]: it for s in g["segments"] for it in s["items"]}
        props = {}
        for j in EDITORS:
            for e in (V.parse(f"wd2_{w}_{j}_{base}") or {}).get("edits") or []:
                i, a, b = e.get("id"), e.get("from") or "", e.get("to") if e.get("to") is not None else ""
                if i in items and a and a != b:
                    props.setdefault((i, a), []).append((j, b, e.get("why", "")))
        applied = skipped = 0
        for (i, a), ps in sorted(props.items()):
            outs = {b for _, b, _ in ps}
            if len(outs) > 1 and len(ps) > 1:     # the two judges disagree on the replacement: take the shorter one
                b = min(outs, key=len)
            else:
                b = ps[0][1]
            t = items[i]["text"]
            if t.count(a) == 1:
                items[i]["text"] = t.replace(a, b); applied += 1
                md.append(f"- [{w} {i}]「{a}」→「{b}」（{'；'.join(f'{x[0]}: {x[2]}' for x in ps)}）")
            else:
                skipped += 1
        G = V.tidy(g)
        rows = json.loads((V.OUT / f"{w}_{base}.json").read_text(encoding="utf-8")).get("rows", {})
        json.dump({"graph": G, "rows": rows, "base": f"{base} → {out}（逐字精读，脚本替换 {applied} 处）"}, open(V.OUT / f"{w}_{out}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        (V.OUT / f"{w}_{out}.md").write_text(f"# {'Op.60' if w == 'op60' else 'Op.61'}｜线（{out}）\n\n" + V.view(G), encoding="utf-8")
        before = sum(len(it["text"]) for s in V.graph_of(w, base)["segments"] for it in s["items"]); after = sum(len(it["text"]) for s in G["segments"] for it in s["items"])
        print(w, out, "提议", len(props), "处，替换", applied, "处，原文找不到", skipped, "处；字数", before, "→", after, flush=True)
    (V.OUT / f"word_{out}.md").write_text("\n".join(md), encoding="utf-8")


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2])
