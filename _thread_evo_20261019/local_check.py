"""Local-mechanism recall (10-27): the checklist is what both judges named as lost against package 3 in final.json (the
pool-only line of P3a). Used only to evaluate drafts, never shown to a writer. One g56 call per draft:
for every (segment, lost mechanism) -> 有 / 部分 / 没有 with a one-line reason.
ids: lc_<draft>.  usage: THREAD_ROUTE=mimic python local_check.py <draft> ...  -> evaluations/local/<draft>.json"""
import json, sys
import covjudge, draft10, evo, node2b

OUT = evo.ROOT / "evaluations" / "local"
Q = """下面是一份对肖邦{NAME}的解释稿（每段：感受、段内转折及其原因、整体原因），以及一张清单：清单上每一条是某一段里一个具体的“此刻”心理机制。
请逐条判断这份稿子在同一段（或相邻段）里有没有写出这个机制：
- 有：写出了同一个机制（说法可以不同，但原因和结果要对得上）；
- 部分：只写到了结果或一半原因；
- 没有：没写到，或写成了别的原因。
每条写一句理由。

【清单】
{LIST}

【稿子】
{DRAFT}

只输出 json：
```json
{{"items": [{{"i": 1, "label": "有", "why": "……"}}]}}
```"""


def checklist(w):
    fin = json.loads((evo.ROOT / "evaluations" / "synth" / f"P3a_{w}" / "final.json").read_text(encoding="utf-8"))
    out = []
    for j, r in (fin.get("regression") or {}).items():
        for x in r.get("worse") or []:
            out.append({"sec": x["sec"], "judge": j, "lost": x["lost"]})
    return out


def draft_text(n):
    d = json.loads((draft10.OUT / f"{n}.json").read_text(encoding="utf-8"))
    return "\n\n".join(f"### {x['sec']}（{x['bars']}小节）\n感受：{x['feel']}\n{x['thread']}" for x in d["sections"])


def run(names):
    OUT.mkdir(exist_ok=True)
    w = names[0].split("_")[1]; cl = checklist(w)
    lst = "\n".join(f"{i}. {c['sec']}：{c['lost']}" for i, c in enumerate(cl, 1))
    evo.run_parallel([node2b.job(f"lc_{n}", Q.format(NAME=covjudge.NAME[w], LIST=lst, DRAFT=draft_text(n)), {"stage": "local"}, w="g56")
                      for n in names if not evo.done(f"lc_{n}")], 5)
    for n in names:
        try:
            r = {int(x["i"]): x for x in evo.parse_json(evo.output(f"lc_{n}"))["items"]}
        except Exception:
            print(n, "no result"); continue
        rows = [dict(c, label=r.get(i, {}).get("label"), why=r.get(i, {}).get("why")) for i, c in enumerate(cl, 1)]
        (OUT / f"{n}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
        cnt = {k: sum(x["label"] == k for x in rows) for k in ("有", "部分", "没有")}
        print(n, "local", cnt, "of", len(rows), flush=True)


if __name__ == "__main__":
    run(sys.argv[1:])
