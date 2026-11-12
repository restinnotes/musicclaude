"""11-02 round 3, my synthesis: Q7 (GPT-6's revision) reads cleanest but lost Op.60 coverage (47->40); Q5 had the coverage. The diagnosis: Q7 removed Q5's
"think through the whole piece before writing" step. Q11 = Q7 with that step put back; everything else stays Q7."""
import json
from pathlib import Path
S = Path(__file__).parent
R = lambda n: (S / n).read_text(encoding="utf-8")
a = R("Q7_A4.txt")
step = """【二、在写出任何要点之前，想清整篇的处境（不输出）】

逐段想清：

- 他此刻的处境是什么？它怎样接着前面？
- 此刻最切身的所求、顾虑或感受是什么？
- 同一处境有没有另外一面，能够与它同时存在，而不需要新增事实？
- 与此前相比，是真有事情发生了变化，还是已有事情继续存在、变得切身、带来后果，或者暂时退到心思之外？
- 本段有哪些主要体验需要有处境相近的内容支撑？有没有体验会被某个不必要的判断或决定直接排除？

这一步看整篇，不逐颗安排句子。一段的丰富，可以来自同一处境中同时存在的几种感受，不一定来自多次转折。

"""
old = "【二、把选中的经历写成一条线】"
assert old in a
a = a.replace(old, step + "【三、把选中的经历写成一条线】")
for o, n in (("【三、正文怎么写】", "【四、正文怎么写】"), ("【四、怎样接住 TARGETS】", "【五、怎样接住 TARGETS】"), ("【五、最后检查并标注】", "【六、最后检查并标注】")):
    assert o in a, o
    a = a.replace(o, n)
old2 = "经过这样的检查仍接不上的，留作 uncovered_targets。"
assert old2 in a
a = a.replace(old2, "以整篇自然成立为前提，争取尽量多的真实覆盖，不追求逐颗解释或表面上的全覆盖。\n\n" + old2)
(S / "Q11_A4.txt").write_text(a, encoding="utf-8")
q = json.loads(R("Q7.json")); q["name"] = "Q11"; q["note"] = "Q11：Q7 的写线层，放回 Q5 的“先想清整篇的处境”一步"
for s in q["steps"]:
    if s["id"] == "A4":
        s["prompt_file"] = "Q11_A4.txt"
(S / "Q11.json").write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok", len(a))
