"""Experiment 3 (10-28, advisor gpt-6): split the "退步 against package 3" verdict into two reviews, so we know whether the
independent core or the bead alignment is behind. Three versions per piece in one uniform layout (segment header, "•" items,
"→" steps; package 3's ← back-references and every version's relation labels dropped; P7 with ids cleaned), anonymised as
甲/乙/丙 in a random order per call:
  core  : no beads. Center, why-now causality, invented backstory / abstraction / lost qualifiers, plain and focused.
  align : with the beads. Per segment whether the main experience and in-segment changes are explained, reversed beads,
          and the 4 key mechanisms of experiment 1 (mech_check.MECH) per version.
Versions: package 3, P4d (T0, pool-only line), P7 (T0 + bead-aware local repair, evaluations/repair/P7_<work>.json).
Read (set before running): core not worse than package 3 but align behind -> the bottleneck is alignment; both behind -> the
core itself; verdicts far from the old "退步" -> the old judge was swayed by layout and length.
ids: sj3_<work>_<core|align>_<judge>.  usage: THREAD_ROUTE=gpt3s python split_judge.py [dry] -> evaluations/split/"""
import json, random, re, sys
import covjudge, deliver_halfdone as D, draft10, evo, finalize3, mech_check, node2b, precise as P

OUT = evo.ROOT / "evaluations" / "split"
NAMES = ("甲", "乙", "丙")
COMMON = ("下面是肖邦{NAME}的三版 Thread：逐段解释他此刻为什么会这样感受。三版格式已统一，顺序随机，不代表先后或好坏。"
          "不要因为字多、条目多或故事完整就判好，也不要因为说得笃定、戏剧化或只讲一个故事就扣分。每个判断写一句理由。\n\n")
CORE = COMMON + """这一次不给听感记录，只评 Thread 本身是否独立成立：
1. center：Center 是否准确、能不能统摄全曲；
2. why：每段此刻的感受，能不能从前面已经发生的事理解——前因具体、因果说得出“因为什么、所以怎样”；
3. invent：有没有编听感撑不住的前史、事件、身份，或用空泛说法代替原因（“更在乎了”“有了新的分量”），或丢掉重要的限定（仿佛、一度、还没）；
4. plain：是不是普通人一遍能懂的话，读起来集中、不重复。
先逐版写它好在哪、差在哪，再按这四项各给三版排名（第一名在前），最后给总排名。

{VERSIONS}

只输出 json：
```json
{{"notes": {{"甲": "……", "乙": "……", "丙": "……"}}, "ranks": {{"center": ["乙", "甲", "丙"], "why": ["…"], "invent": ["…"], "plain": ["…"]}},
 "rank_why": {{"center": "……", "why": "……", "invent": "……", "plain": "……"}}, "overall": ["乙", "甲", "丙"], "overall_why": "……"}}
```"""
ALIGN = COMMON + """这一次给出每段的听感记录（另一批人听这段写下的原文），评三版对听感的解释：
1. 逐段看：标［主体验］的听感和［段内变化］，各版有没有说清它此刻为什么会出现；有没有把某颗听感解释反了（方向相反）。每格一句，不超过 30 字。
   不要求每颗听感都被同一个故事吞进去：与解释相容、作为感受保留，或者属于另一种听法，都可以。
2. 下面这 4 条具体机制，各版有没有写出真正的因果：有 / 部分（只写到结果或一半原因）/ 没有。
3. 给每版数：主体验说清楚了的段数、写反的段；最后给总排名（第一名在前）。

【这首要核对的机制】
{MECHS}

【听感记录】
{BEADS}

{VERSIONS}

只输出 json：
```json
{{"segs": [{{"sec": "S01", "甲": "……", "乙": "……", "丙": "……"}}],
 "mechs": [{{"i": 1, "甲": "有", "乙": "部分", "丙": "没有", "why": "……"}}],
 "b1_clear": {{"甲": 10, "乙": 9, "丙": 8}}, "reversed": {{"甲": ["S04"], "乙": [], "丙": []}}, "overall": ["乙", "甲", "丙"], "overall_why": "……"}}
```"""


def head(s):
    return f"### {s['id']} ｜ {s['start']}–{s['end']} 小节"


def pkg3(w):
    t = finalize3.PKG3[w].read_text(encoding="utf-8-sig")
    center = re.search(r"Center：(.*)", t).group(1).strip()
    parts = {m.group(1): m.group(2) for m in re.finditer(r"^(S\d\d) ｜[^\n]*\n(.*?)(?=^S\d\d ｜|\Z)", t, re.M | re.S)}
    body = []
    for s in draft10.segs(w):
        lines = [l.rstrip() for l in parts.get(s["id"], "").splitlines() if l.strip() and not l.strip().startswith("←")]
        body += [head(s), ""] + lines + [""]
    return center, "\n".join(body)


def split_item(it):
    if it.get("feel"):
        return it["feel"], it.get("why", "")
    m = re.match(r"感受：(.*?)\s*为什么：(.*)", it.get("text", ""), re.S)
    return (m.group(1), m.group(2)) if m else (it.get("text", ""), "")


def p4d(w):
    fin, _ = P.t0(w); body = []
    for s in draft10.segs(w):
        sec = next(x for x in fin["sections"] if x["sec"] == s["id"])
        body += [head(s), ""]
        for it in sec["items"]:
            f, y = split_item(it)
            body += [f"• {D.clean(f)}"] + ([f"→ {D.clean(y)}"] if y else [])
        body.append("")
    return fin.get("center", ""), "\n".join(body)


def p7(w):
    rows = json.loads((evo.ROOT / "evaluations" / "repair" / f"P7_{w}.json").read_text(encoding="utf-8"))["rows"]
    fin, _ = P.t0(w); body = []
    for s in draft10.segs(w):
        body += [head(s), ""]
        for x in rows[f"{w}_{s['id']}"]["edit"].get("items") or []:
            body += [f"• {D.clean(x.get('feel', ''))}", f"→ {D.clean(x.get('why', ''))}"]
        body.append("")
    return fin.get("center", ""), "\n".join(body)


def versions(w):
    return {"包3": pkg3(w), "P4d": p4d(w), "P7": p7(w)}


def main(dry):
    OUT.mkdir(exist_ok=True)
    jobs, order = [], {}
    for w in ("op60", "op61"):
        vs = versions(w)
        beads = "\n".join(f"- {b['id']}［{b['role']}］{b['text']}" for b in covjudge.beads(w) if b["role"] != "演奏条件")
        mechs = "\n".join(f"{i}. {m}" for i, m in enumerate(mech_check.MECH[w], 1))
        for kind in ("core", "align"):
            for j in ("g6", "g56"):
                rid = f"sj3_{w}_{kind}_{j}"
                ks = list(vs); random.Random(rid).shuffle(ks); order[rid] = dict(zip(NAMES, ks))
                vt = "\n\n".join(f"========== {n} 版 ==========\nCenter：{vs[k][0]}\n\n{vs[k][1]}" for n, k in zip(NAMES, ks))
                msg = (CORE if kind == "core" else ALIGN).format(NAME=covjudge.NAME[w], VERSIONS=vt, MECHS=mechs, BEADS=beads)
                (OUT / f"prompt_{rid}.txt").write_text(msg, encoding="utf-8")
                print(rid, len(msg), "字", order[rid], flush=True)
                if not evo.done(rid):
                    jobs.append(node2b.job(rid, msg, {"stage": "split-judge"}, w=j))
    json.dump(order, open(OUT / "order.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if dry:
        return
    evo.run_parallel(jobs, 4)
    res = {}
    for rid, o in order.items():
        try:
            r = evo.parse_json(evo.output(rid))
        except Exception as e:
            print(rid, "读不出结果", e, flush=True); continue
        res[rid] = r; un = lambda xs: [o.get(x, x) for x in xs or []]
        line = f"{rid}: 总排名 {un(r.get('overall'))}"
        if "_core_" in rid:
            line += " | " + "；".join(f"{k} {un(v)}" for k, v in (r.get("ranks") or {}).items())
        else:
            line += f" | 主体验说清 { {o.get(k, k): v for k, v in (r.get('b1_clear') or {}).items()} }"
            line += f" | 写反 { {o.get(k, k): v for k, v in (r.get('reversed') or {}).items()} }"
            line += " | 机制“有” " + str({o[n]: sum(1 for m in r.get("mechs") or [] if m.get(n) == "有") for n in NAMES})
        print(line, flush=True)
    json.dump({"order": order, "results": res}, open(OUT / "split_results.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main("dry" in sys.argv[1:])
