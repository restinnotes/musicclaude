"""form check against 标准.md: 每段 2-4 条, 每条一句. counts only, for the report."""
import os, re, sys
os.environ["JV"] = "2"
sys.path.insert(0, ".")
import v6fix as V

for t in sys.argv[1:]:
    for w in ("op60", "op61"):
        g = V.graph_of(w, t)
        items = [i["text"] for s in g["segments"] for i in s["items"]]
        multi = sum(1 for x in items if len([p for p in re.split(r"[。！？]", x) if p.strip()]) > 1)
        counts = [len(s["items"]) for s in g["segments"]]
        chars = sum(len(x) for x in items)
        print(f"{t} {w} 字数 {chars} 条目 {len(items)} 每条平均 {chars / len(items):.0f} 字 | 超过一句的条目 {multi} | 每段条数 {min(counts)}–{max(counts)}，只有 1 条的段 {counts.count(1)}")
