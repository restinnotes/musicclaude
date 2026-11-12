"""11-02 round 3: Q14's Op.60 came out with no cite at all (Q12 dropped the instruction, Q8 had it by luck); 标准.md: 提到前面的内容就直接提，标出是哪一段的哪一条.
Q15 = Q14 + the cite rule back. Annotation only, the text rules do not change."""
import json
from pathlib import Path
S = Path(__file__).parent
a = (S / "Q14_A4.txt").read_text(encoding="utf-8")
old = "六、段落关系标签（relation）"
assert old in a
a = a.replace(old, "六、引用（cite）\n某条提到或依赖更早某一条时，在 cite 里写那一条的编号（如 S02-1）。提到前面的内容就直接提，不必每条都有；只是主题相近、情绪相近不算。\n\n七、段落关系标签（relation）")
(S / "Q15_A4.txt").write_text(a, encoding="utf-8")
q = json.loads((S / "Q14.json").read_text(encoding="utf-8"))
q["name"] = "Q15"; q["note"] = "Q15：Q14 加回引用的要求"
for s in q["steps"]:
    if s["id"] == "A4":
        s["prompt_file"] = "Q15_A4.txt"
(S / "Q15.json").write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
