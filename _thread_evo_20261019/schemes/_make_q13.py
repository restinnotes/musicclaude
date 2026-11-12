"""11-02 round 3: GPT-5.6's revised skeleton layer from advisor2 (keep live contradictions, don't choose sides early, no turn started by the other person's new move)
with the best writer so far (Q8). Judges on ql Op.60: the weak point is turns resting on what the other person suddenly feels or hides, which comes from the route."""
import json
from pathlib import Path
S = Path(__file__).parent; H = S.parent
o = (H / "runs/adv2_g56/output.txt").read_text(encoding="utf-8")
a = o.index("你要为一首器乐作品设计 Thread 的“人的经历骨架”。")
b = o.index("只输出 JSON（字段名照上面写的）。", a) + len("只输出 JSON（字段名照上面写的）。")
t = o[a:b].strip() + "\n"
for k in ("{NAME}", "{SECTIONS}", "{CENTER}", "{K}"):
    assert k in t, k
(S / "Q13_A1.txt").write_text(t, encoding="utf-8")
q = json.loads((S / "Q8.json").read_text(encoding="utf-8"))
q["name"] = "Q13"; q["note"] = "Q13：GPT-5.6 改的经历骨架层（保留活的矛盾，不过早选边，不靠对方新举动发动转折）+ Q8 写线层"
for s in q["steps"]:
    if s["id"] == "A1":
        s["prompt_file"] = "Q13_A1.txt"
(S / "Q13.json").write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")
print("ok", len(t), [(s["id"], s["prompt_file"]) for s in q["steps"]])
