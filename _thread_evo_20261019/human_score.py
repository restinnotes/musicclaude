"""11-02 (迭代准则 §六): one score per dimension, only for a human to read (user: "有的时候还是需要一些评分 和简短例子能更直观的看出我们真的好了多少").
Never used for decisions. Each judge sees the versions together, in shuffled order under neutral labels, so the numbers share one scale. ids hs_<w>_<j>_<joined tags>.
usage: python human_score.py <tag> [<tag> ...]   -> evaluations/v6fix/human_score_<joined tags>.md/.json"""
import json, os, random, statistics, sys
os.environ.setdefault("JV", "2")
import evo, covjudge, v6fix as V

DIMS = (("alone", "单独成立"), ("lean", "不啰嗦、读得顺"), ("plain", "人话"), ("cover", "接得上珠子"), ("overall", "总体"))
P = """下面是肖邦{NAME}同一条线的几个版本，顺序是随机的，以及另一批人听这首曲子每一段写下的听感记录（珠子）。

{WHAT}

请给每个版本打分，1–10 分，可以用小数，只看整体印象，分数要拉开差距：
- alone（单独成立）：只看线，它是不是一个人一路经历下来的一件事，后面从前面长出来；
- lean（不啰嗦、读得顺）：每句都有用，连着读顺，没有重复；
- plain（人话）：像一个人平平常常讲自己的经历；
- cover（接得上珠子）：能让人感到珠子里那些感受为什么会出现在这里；相关就算，把珠子的情节搬进线当真的不算；
- overall（总体）：作为读者，你更愿意读哪一版。
每个版本再写一句话说它最突出的优点和最大的问题。

{VERS}

【珠子】
{BEADS}

只输出 json：
```json
{{"scores": {{"A": {{"alone": 7, "lean": 6.5, "plain": 7, "cover": 8, "overall": 7, "note": "……"}}}}}}
```
"""
LABELS = "ABCDEF"


def main(tags):
    joined = "_".join(tags)
    jobs, maps = [], {}
    for w in ("op60", "op61"):
        for j in V.JUDGES:
            rid = f"hs_{w}_{j}_{joined}"
            order = list(tags); random.Random(rid).shuffle(order)
            maps[rid] = dict(zip(LABELS, order))
            vers = "\n\n".join(f"【版本 {LABELS[i]}】\n{V.view(V.graph_of(w, t))}" for i, t in enumerate(order))
            msg = P.format(NAME=covjudge.NAME[w], WHAT=V.WHAT2, VERS=vers, BEADS=V.beads(w))
            if not evo.done(rid):
                jobs.append((rid, lambda rid=rid, msg=msg, m=V.JUDGES[j]: evo.call(rid, msg, model=m, meta={"stage": "human-score"})))
    evo.run_parallel(jobs, 4)
    res = {}
    for rid, mp in maps.items():
        d = V.parse(rid)
        if not d:
            continue
        w = rid.split("_")[1]
        for lab, t in mp.items():
            s = (d.get("scores") or {}).get(lab)
            if s:
                res.setdefault(w, {}).setdefault(t, []).append(s)
    md = ["# 给人看的评分（不作判定）", "", f"两位评委（GPT-6、GPT-5.6）一起看这几版，顺序打乱，版本名隐去，各打 1–10 分，这里是两人的平均。", ""]
    for w in ("op60", "op61"):
        md += [f"## {'Op.60' if w == 'op60' else 'Op.61'}", "", "| 版本 | " + " | ".join(n for _, n in DIMS) + " |", "|---|" + "---|" * len(DIMS)]
        for t in tags:
            rows = res.get(w, {}).get(t) or []
            cells = [f"{statistics.mean(r[k] for r in rows if isinstance(r.get(k), (int, float))):.1f}" if rows else "?" for k, _ in DIMS]
            md.append(f"| {t} | " + " | ".join(cells) + " |")
        md.append("")
        for t in tags:
            for r in res.get(w, {}).get(t) or []:
                md.append(f"- {t}：{str(r.get('note'))[:160]}")
        md.append("")
    (V.OUT / f"human_score_{joined}.md").write_text("\n".join(md), encoding="utf-8")
    (V.OUT / f"human_score_{joined}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main(sys.argv[1:])
