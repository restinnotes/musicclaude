"""10-29: a FIXED checklist of v6's substantive content for the regression check. The open blind question ("would replacing v6
lose anything?") gives a different list on every call and never converges (w9 fixed all of w8's list, got as many new items and
lower bead coverage). Here: (1) build: merge the two diagnosis reviewers' keep + cross lists into one deduplicated checklist per
piece, once; (2) check: for a version, two judges label every item 保留 / 更好地取代 / 丢失 with where and why.
ids: ckl_<w> (build), chk_<w>_<j>_<tag> (check).  usage: python v6check.py build | check <tag> -> evaluations/v6fix/checklist_*.json"""
import json, sys
import covjudge, evo, v6fix as V

BUILD = """下面是肖邦{NAME}的一条 Thread（关系图，叫 v6），以及两位评审各自列出的“v6 里真正成立、修补时不能丢的实质内容”（按段，另有跨段关系）。
请把两位的清单合并成一份去重的清单，用来检查以后的修补版本有没有丢掉 v6 的好内容。

要求：
- 每条只写一个独立的心理事实，或一条前后之间有解释力的关系；两位说的是同一件事就合成一条。
- 每条写：所在段（跨段的写最后起作用的那一段）、对应的 v6 条目编号、一句平常话的描述（说清这个内容是什么，不照抄 v6 原句）。
- 评审自己说过“和珠子对不上”“不成立”的，不要收进清单。只是措辞、总结句、重复强调的，不要收。
- 不要新增评审没提到的内容。

{WHAT}

【v6】
{V6}

【评审甲的清单】
{A}

【评审乙的清单】
{B}

只输出 json：
```json
{{"items": [{{"id": "K1", "sec": "S03", "v6": ["R10", "R11"], "what": "……"}}]}}
```"""
CHECK = """下面是肖邦{NAME}一条 Thread（关系图）的一个修补版本，以及一份清单：清单上是原来那一版（v6）里已经说清的实质内容。
请逐条核对，这个修补版本对每条内容的处理：
- 保留：意思还在（措辞可以不同，可以合并进别的条目，也可以分散在几条里），写出在哪几条；
- 更好地取代：换成了更有解释力、更贴合的说法，原来的意思被包含在里面或被合理修正，写出在哪几条、为什么更好；
- 丢失：这个意思没有了，也没有被更好的说法取代。
只看意思在不在，不看字面。戏剧化、主观不算问题。每条写一句理由。不要漏掉清单上任何一条。

{WHAT}

【修补版本】（方括号里是条目编号）
{LINE}

【清单】
{LIST}

只输出 json：
```json
{{"items": [{{"id": "K1", "label": "保留", "where": ["S03-2"], "why": "……"}}]}}
```"""
LAB = ("保留", "更好地取代", "丢失")


def keep_text(w, j):
    d = V.parse(f"v6d_{w}_{j}") or {}
    out = []
    for s in d.get("sections") or []:
        for k in s.get("keep") or []:
            out.append(f"- {s.get('sec')}［{'、'.join(k.get('ids') or [])}］{k.get('what', '')}")
    out += [f"- 跨段［{'、'.join(c.get('ids') or [])}］{c.get('what', '')}" for c in d.get("cross") or []]
    return "\n".join(out)


def build():
    jobs = []
    for w in ("op60", "op61"):
        msg = BUILD.format(NAME=covjudge.NAME[w], WHAT=V.WHAT, V6=V.view(V.v6(w), ids=True), A=keep_text(w, "g6"), B=keep_text(w, "g56"))
        rid = f"ckl_{w}"
        if not evo.done(rid):
            jobs.append((rid, lambda rid=rid, msg=msg: evo.call(rid, msg, model=evo.G6, meta={"stage": "v6-checklist"})))
    evo.run_parallel(jobs, 2)
    for w in ("op60", "op61"):
        d = V.parse(f"ckl_{w}") or {}
        json.dump(d, open(V.OUT / f"checklist_{w}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(w, "清单", len(d.get("items") or []), "条", flush=True)


def items(w):
    return json.loads((V.OUT / f"checklist_{w}.json").read_text(encoding="utf-8"))["items"]


def check(tag):
    import os
    jobs = []
    for w in [x for x in os.environ.get("ONLY_W", "op60,op61").split(",") if x]:
        lst = "\n".join(f"- {k['id']}（{k['sec']}）{k['what']}" for k in items(w))
        msg = CHECK.format(NAME=covjudge.NAME[w], WHAT=V.WHAT, LINE=V.view(V.graph_of(w, tag), ids=True), LIST=lst)
        for j, m in V.JUDGES.items():
            rid = f"chk_{w}_{j}_{tag}"
            if not evo.done(rid):
                jobs.append((rid, lambda rid=rid, msg=msg, m=m: evo.call(rid, msg, model=m, meta={"stage": "v6-check-list"})))
    evo.run_parallel(jobs, 4)
    return summarize(tag)


def summarize(tag):
    res = {}; md = [f"# v6 好内容清单核对：{tag}", ""]
    for w in ("op60", "op61"):
        K = {k["id"]: k for k in items(w)}; per = {}
        for j in V.JUDGES:
            d = V.parse(f"chk_{w}_{j}_{tag}") or {}
            for x in d.get("items") or []:
                if x.get("id") in K:
                    per.setdefault(x["id"], {})[j] = x
        lost_any = [k for k in K if any((per.get(k, {}).get(j) or {}).get("label") == "丢失" for j in V.JUDGES)]
        lost_both = [k for k in lost_any if all((per.get(k, {}).get(j) or {}).get("label") == "丢失" for j in V.JUDGES)]
        cnt = {j: {l: sum(1 for k in K if (per.get(k, {}).get(j) or {}).get("label") == l) for l in LAB} for j in V.JUDGES}
        res[w] = {"n": len(K), "cnt": cnt, "lost_any": lost_any, "lost_both": lost_both}
        md += [f"## {'Op.60' if w == 'op60' else 'Op.61'}（清单 {len(K)} 条）", "",
               *(f"- {'gpt-6' if j == 'g6' else '5.6'}：保留 {c['保留']}、更好地取代 {c['更好地取代']}、丢失 {c['丢失']}" for j, c in cnt.items()),
               f"- 两位都判丢失 {len(lost_both)} 条，至少一位判丢失 {len(lost_any)} 条", ""]
        for k in lost_any:
            md.append(f"- {k}（{K[k]['sec']}）{K[k]['what']}")
            md += [f"  - {'gpt-6' if j == 'g6' else '5.6'}：{(per.get(k, {}).get(j) or {}).get('label', '未判')}。{(per.get(k, {}).get(j) or {}).get('why', '')}" for j in V.JUDGES]
        md.append("")
        print(tag, w, f"清单 {len(K)} 条 | " + " | ".join(f"{j} 保留{c['保留']} 取代{c['更好地取代']} 丢失{c['丢失']}" for j, c in cnt.items())
              + f" | 两位都判丢失 {len(lost_both)}，任一位 {len(lost_any)}", flush=True)
    (V.OUT / f"checklist_{tag}.md").write_text("\n".join(md), encoding="utf-8")
    json.dump(res, open(V.OUT / f"checklist_{tag}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return res


if __name__ == "__main__":
    if sys.argv[1] == "build":
        build()
    elif sys.argv[1] == "check":
        for t in sys.argv[2:]:
            check(t)
