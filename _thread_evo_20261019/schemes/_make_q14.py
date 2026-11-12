"""11-02 round 3: Q8/Q12 won by writing 2-3 sentences per item (avg 60-70 chars per item; 标准.md asks one sentence per item, 2-4 items per segment, because the video
needs items it can pick and place). Judges never looked at this. Q14 = Q12 with the standard's form put back; nothing else changes."""
import json
from pathlib import Path
S = Path(__file__).parent
a = (S / "Q12_A4.txt").read_text(encoding="utf-8")
old = "1. 篇幅控制：每段写 1–3 条。短段落（小节少、变化单一的段落）只写 1–2 条，宁短勿凑。"
assert old in a
a = a.replace(old, "1. 形态：每段写 2–4 条要点，每条是一句完整、自然的话，只说一件事，连着读仍像一段流畅的经历。一句能说清的不拆成几条，也不合成散文式的长句；小段落（小节少、变化单一）写 2 条就够，宁短勿凑。")
(S / "Q14_A4.txt").write_text(a, encoding="utf-8")
q = json.loads((S / "Q12.json").read_text(encoding="utf-8"))
q["name"] = "Q14"; q["note"] = "Q14：Q12 的写线层，形态按标准改回每段 2–4 条、每条一句"
for s in q["steps"]:
    if s["id"] == "A4":
        s["prompt_file"] = "Q14_A4.txt"
(S / "Q14.json").write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok")
