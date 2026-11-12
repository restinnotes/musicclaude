"""Experiment 1 (10-28, advisor gpt-6): does D22 (D21 + coping / backfire) supply the mechanisms every pool-only line lost to
package 3? A fixed checklist of 8 mechanisms (4 per piece, the advisor's wording), shown only to the judge, never to a
writer. Per draft one g56 call: each mechanism 有 / 部分 / 没有 with the segment and one line of reason, plus counts of
invented backstory and mechanical "try - fail - try another" loops. D21 drafts are judged the same way for comparison.
Pass (decided before looking): >= 6 of 8 mechanisms judged 有 in >= 2 D22 drafts, and no more invented backstory or
loops than D21.  ids: mcE1_<draft>.  usage: THREAD_ROUTE=gpt3s python mech_check.py  -> evaluations/mech/<draft>.json"""
import collections, json
import covjudge, draft10, evo, node2b

OUT = evo.ROOT / "evaluations" / "mech"
MECH = {"op60": ["满足为什么会生出想让亲近延续下去的愿望",
                 "越想抓牢当下，为什么只增加自己的牵动，却增加不了以后的保证",
                 "身体松下来为什么不等于心里的问题解决了",
                 "眼前的安慰退去以后，独自回味为什么仍能带来快乐，却没有消除想亲近的愿望"],
        "op61": ["越用力撑住自己，为什么反而越碰到自己有多眷恋",
                 "反复追问为什么改变不了距离，不舍却又不断催出新的追问",
                 "熟悉的感觉突然闯入时，为什么身体先受惊、反而照出缺席",
                 "疲惫为什么让抵抗停下，想念又怎样变成继续向前的力量"]}
Q = """下面是一份对肖邦{NAME}的逐段解释稿，以及一张清单。清单上每一条是一个具体的心理机制（为什么会这样，而不只是会怎样）。
请逐条判断这份稿子有没有在某一段写出这个机制的真正因果：
- 有：写出了同一个因果过程（说法可以不同，但“因为什么、所以怎样”要对得上），不只是出现相同的词；
- 部分：只写到结果，或只写到一半原因；
- 没有：没写到，或写成了别的原因。
每条写出在哪一段、一句理由。

另外请数两样：
- invented：稿子里有几处给人物编了听感撑不住的具体前史或外部事件（身份、往事、发生了什么事），每处写一句；
- loops：有几段写成了机械的“试一个办法—失败—换一个办法”的循环（只是为了交代应对而编出来的策略更替），每处写一句。

【清单】
{LIST}

【稿子】
{DRAFT}

只输出 json：
```json
{{"items": [{{"i": 1, "label": "有", "sec": "S04", "why": "……"}}], "invented": ["……"], "loops": ["……"]}}
```"""


def names():
    return sorted(p.stem for p in draft10.OUT.glob("d2[123]*_op6[01]_r1.json"))


def text(n):
    d = json.loads((draft10.OUT / f"{n}.json").read_text(encoding="utf-8"))
    return "\n\n".join(f"### {x['sec']}（{x['bars']}小节）\n感受：{x['feel']}\n{x['thread']}" for x in d["sections"])


def main():
    OUT.mkdir(exist_ok=True)
    ns = names(); jobs = []
    for n in ns:
        w = n.split("_")[1]
        lst = "\n".join(f"{i}. {m}" for i, m in enumerate(MECH[w], 1))
        if not evo.done(f"mcE1_{n}"):
            jobs.append(node2b.job(f"mcE1_{n}", Q.format(NAME=covjudge.NAME[w], LIST=lst, DRAFT=text(n)), {"stage": "mech"}, w="g56"))
    evo.run_parallel(jobs, 32)
    rows = {}
    for n in ns:
        try:
            j = evo.parse_json(evo.output(f"mcE1_{n}"))
        except Exception:
            print(n, "no result", flush=True); continue
        rows[n] = j; (OUT / f"{n}.json").write_text(json.dumps(j, ensure_ascii=False, indent=1), encoding="utf-8")
    for tag in ("d21", "d22", "d23"):
        print(f"== {tag}", flush=True)
        for w in ("op60", "op61"):
            got = collections.Counter(); part = collections.Counter(); k = 0
            for n, j in rows.items():
                if not n.startswith(tag) or f"_{w}_" not in n:
                    continue
                k += 1
                for x in j.get("items") or []:
                    got[int(x["i"])] += x.get("label") == "有"; part[int(x["i"])] += x.get("label") == "部分"
            inv = sum(len(j.get("invented") or []) for n, j in rows.items() if n.startswith(tag) and f"_{w}_" in n)
            lps = sum(len(j.get("loops") or []) for n, j in rows.items() if n.startswith(tag) and f"_{w}_" in n)
            print(f"  {w}（{k} 篇）每条机制写出“有”的篇数：" + "，".join(f"{i}:{got[i]}（部分{part[i]}）" for i in range(1, 5))
                  + f" | 编前史 {inv} 处，机械循环 {lps} 处", flush=True)
    for tg in ("d22", "d23"):
        ok_ = sum(1 for w in ("op60", "op61") for i in range(1, 5)
                  if sum(1 for n, j in rows.items() if n.startswith(tg) and f"_{w}_" in n
                         for x in j.get("items") or [] if int(x["i"]) == i and x.get("label") == "有") >= 2)
        print(f"{tg.upper()}：8 条机制里有 {ok_} 条在 ≥2 篇里写出“有”（过关线 6 条）", flush=True)
    d22ok = sum(1 for w in ("op60", "op61") for i in range(1, 5)
                if sum(1 for n, j in rows.items() if n.startswith("d22") and f"_{w}_" in n
                       for x in j.get("items") or [] if int(x["i"]) == i and x.get("label") == "有") >= 2)
    print(f"D22：8 条机制里有 {d22ok} 条在 ≥2 篇里写出“有”（过关线 6 条）", flush=True)


if __name__ == "__main__":
    main()
