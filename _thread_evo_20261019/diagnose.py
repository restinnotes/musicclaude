"""Build an anonymized diagnosis (FP counts, judge one-liners, worst-passage excerpts) from judged rows.
usage: python diagnose.py <eval_id> <name-regex> <out.md>"""
import json, re, sys, random, collections
import evo
eid, pat, out = sys.argv[1], re.compile(sys.argv[2]), sys.argv[3]
rows = [r for r in json.loads((evo.ROOT / "evaluations" / eid / "rows.json").read_text(encoding="utf-8")) if pat.search(r["name"])]
names = {"F1": "情绪顺序表", "F2": "结论先行", "F3": "抽象注水", "F4": "拼接与虚构", "F5": "音响描写合集", "F6": "套路主题", "F7": "每段配额式领悟"}
fp = collections.Counter(f[:2] for r in rows for f in (r.get("false_positives") or []))
L = [f"共 {len(set(r['name'] for r in rows))} 篇文章、{len(rows)} 份评审。假阳性出现次数：" + "；".join(f"{k}{names.get(k, '')} {v}" for k, v in fp.most_common())]
L.append("\n评委对各篇的一句话结论：")
for r in rows:
    L.append(f"- [{r.get('overall')}/10] {r.get('verdict')}")
L.append("\n评委读后摘录（最差的一处）：")
blocks = {r["block"]: {lab for lab, n in [(r["label"], r["name"])]} for r in rows}
for r in rows:
    t = evo.output(f"j_{eid}_{r['block']}") or ""
    i = t.find(r["label"])
    seg = t[i:i + 2500] if i >= 0 else ""
    m = re.search(r"最差[^\n]{0,260}", seg)
    if m:
        L.append("- " + m.group(0).strip())
(evo.ROOT / out).write_text("\n".join(L), encoding="utf-8")
print(len("\n".join(L)), fp.most_common())
