"""10-29 (user: "覆盖率而言 目前能覆盖多少了 珠子 这个不止要测对比吧 还要测对应到珠子关系图覆盖多少了"). Absolute bead coverage of
one line version: the judge sees ONE line (not told which version) and every bead of the piece, and labels each bead
说清 / 偏弱 / 相反 / 没有 with a reason and the items that do the work. Same prompt for v6 and every repaired round.
ids: cov_<w>_<j>_<tag>.  usage: python v6cov.py <tag> [<tag> ...]  (tag v6 = the original) -> evaluations/v6fix/cov_<tag>.json/.md"""
import json, sys
from collections import Counter
import covjudge, evo, v6fix as V

COV = """下面是肖邦{NAME}的一条 Thread（关系图），以及另一批人听这首曲子每一段写下的听感记录（珠子）。请逐颗珠子判断：这条线有没有给出“他此刻为什么会这样”的原因。

{WHAT}

每颗珠子判一项：
- 说清：线里有条目给出了具体原因，读完能明白这颗珠子写的感受为什么偏偏此刻出现；
- 偏弱：沾边，但原因笼统、只解释了一部分，或者只是把感受换个说法复述；
- 相反：线在这一段写的感受和这颗珠子对不上；
- 没有：线没有涉及。
线不需要把珠子的细节再写一遍，只看有没有原因。“另一种理解”（和主体验不能同时成立的听法）也照样判断。戏剧化、主观、只讲一个故事都不算缺点。
每颗写一句理由，并写出起作用的条目（引几个字即可）。不要漏掉任何一颗。

【线】
{LINE}

【珠子】
{BEADS}

只输出 json：
```json
{{"beads": [{{"sec": "S01", "bead": "B1", "status": "说清", "items": "……", "why": "……"}}]}}
```"""
COV2 = """下面是肖邦{NAME}的一条线，以及另一批人听这首曲子每一段写下的听感记录（珠子）。请逐颗珠子判断：读者在线的同一段里，能不能找到和这颗珠子的感受情境相近的处境或原因。

{WHAT}

每颗珠子判一项：
- 说清：线这一段的处境或原因，让人能感到这颗珠子的感受为什么会出现在这里。相关、情境相近就算，不要求逐项解释；
- 偏弱：只照应了一部分，或者只是把感受换个说法；
- 相反：线在这一段写的感受和这颗珠子对不上；
- 没有：线没有涉及。
只看珠子里人的感受那一层：珠子里纯粹的声音、画面、比喻本身，不要求线去对应。线把珠子里的画面或想象出的情节搬进来当成他真的经历的事，不算说清。
“另一种理解”（和主体验不能同时成立的听法）也照样判断。戏剧化、主观、只讲一个故事都不算缺点。
每颗写一句理由，并写出起作用的条目（引几个字即可）。不要漏掉任何一颗。

【线】
{LINE}

【珠子】
{BEADS}

只输出 json：
```json
{{"beads": [{{"sec": "S01", "bead": "B1", "status": "说清", "items": "……", "why": "……"}}]}}
```"""
import os as _os
JV = _os.environ.get("JV", "1"); PFX = "cov2" if JV == "2" else "cov"
ST = ("说清", "偏弱", "相反", "没有")


def graph(w, tag):
    return V.v6(w) if tag == "v6" else V.graph_of(w, tag)


def roles(w):
    return {(b["sec"], b["id"].split("-")[-1]): b["role"] for b in covjudge.beads(w) if b["role"] != "演奏条件"}


def run(tags):
    jobs = []
    import os
    WS = [x for x in os.environ.get("ONLY_W", "op60,op61").split(",") if x]
    for tag in tags:
        for w in WS:
            msg = (COV2.format(NAME=covjudge.NAME[w], WHAT=V.WHAT2, LINE=V.view(graph(w, tag)), BEADS=V.beads(w)) if JV == "2"
                   else COV.format(NAME=covjudge.NAME[w], WHAT=V.WHAT, LINE=V.view(graph(w, tag)), BEADS=V.beads(w)))
            for j, m in V.JUDGES.items():
                rid = f"{PFX}_{w}_{j}_{tag}"
                if not evo.done(rid):
                    jobs.append((rid, lambda rid=rid, msg=msg, m=m: evo.call(rid, msg, model=m, meta={"stage": "v6-cov"})))
    evo.run_parallel(jobs, 8)
    for tag in tags:
        summarize(tag)


def summarize(tag):
    out = {}; md = [f"# 珠子覆盖（绝对）：{tag}", "", "每位评委只看这一版线和全部珠子，逐颗判 说清 / 偏弱 / 相反 / 没有。", ""]
    for w in ("op60", "op61"):
        R = roles(w)
        for j in V.JUDGES:
            d = V.parse(f"{PFX}_{w}_{j}_{tag}") or {}
            got = {(x.get("sec"), str(x.get("bead"))): x for x in d.get("beads") or []}
            by = {}
            for key, role in R.items():
                st = (got.get(key) or {}).get("status", "未判")
                by.setdefault(role, Counter())[st if st in ST else "未判"] += 1
            tot = sum(by.values(), Counter())
            out[f"{w}_{j}"] = {"total": dict(tot), "by_role": {r: dict(c) for r, c in by.items()}, "n": len(R),
                               "weak": [(k[0], k[1], got[k].get("status"), got[k].get("why", "")) for k in R if k in got and got[k].get("status") in ("偏弱", "相反", "没有")]}
            md += [f"## {'Op.60' if w == 'op60' else 'Op.61'} · {'gpt-6' if j == 'g6' else 'gpt-5.6'}（共 {len(R)} 颗）", "",
                   "| 角色 | 说清 | 偏弱 | 相反 | 没有 | 未判 |", "|---|---|---|---|---|---|"]
            for r in ("主体验", "段内变化", "另一侧面", "另一种理解"):
                if r in by:
                    c = by[r]; md.append(f"| {r} | {c['说清']} | {c['偏弱']} | {c['相反']} | {c['没有']} | {c['未判']} |")
            md += [f"| 合计 | {tot['说清']} | {tot['偏弱']} | {tot['相反']} | {tot['没有']} | {tot['未判']} |", ""]
            md += [f"- {s} {b}［{R[(s, b)]}］{st}：{why}" for s, b, st, why in out[f"{w}_{j}"]["weak"]] + [""]
    (V.OUT / f"{PFX}_{tag}.md").write_text("\n".join(md), encoding="utf-8")
    json.dump(out, open(V.OUT / f"{PFX}_{tag}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for k, v in out.items():
        t = v["total"]; main = v["by_role"].get("主体验", {})
        print(tag, k, f"说清 {t.get('说清', 0)}/{v['n']} 偏弱 {t.get('偏弱', 0)} 相反 {t.get('相反', 0)} 没有 {t.get('没有', 0)} 未判 {t.get('未判', 0)} | 主体验说清 {main.get('说清', 0)}/{sum(main.values())}", flush=True)


def self_reported(tag):
    """no model call: beads that some line item says it explains (the line's own `explains`)"""
    for w in ("op60", "op61"):
        R = roles(w); g = graph(w, tag)
        claimed = {(s["sec"], b) for s in g["segments"] for it in s["items"] for b in it.get("explains") or []}
        n = sum(1 for k in R if k in claimed and R[k] != "另一种理解"); m = sum(1 for k in R if R[k] != "另一种理解")
        print(tag, w, f"线自报解释了 {n}/{m} 颗（不含另一种理解）", flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "self":
        for t in sys.argv[2:]:
            self_reported(t)
    else:
        run(sys.argv[1:])
