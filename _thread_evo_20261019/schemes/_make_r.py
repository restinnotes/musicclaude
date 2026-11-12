"""11-02 round 2 scheme R (my synthesis of round 1): Q3 skeleton + 10-23 rule back in (no story driven by mental moves) + route selection also
sees bead qualities (synthesis may see beads; avoids narrow routes) + the writer aims at most qualities of a segment, not "some"."""
import json
from pathlib import Path
S = Path(__file__).parent
R = lambda n: (S / n).read_text(encoding="utf-8")
W = lambda n, t: (S / n).write_text(t, encoding="utf-8")


def sub(t, old, new):
    assert old in t, old[:40]
    return t.replace(old, new)


MOVES = "不要靠心理动作推动故事：劝自己、提醒自己、想通、找到办法、发现办法不管用、下决心——只有这一段的感受非它不能解释时才写。"

a1 = R("Q3_A1.txt")
a1 = sub(a1, "5. 不要把感受的形状本身当成人物推进。", "5. " + MOVES + "\n也不要给他的做法或顾虑起一个名字，然后反复用这个词推进。\n\n6. 不要把感受的形状本身当成人物推进。")
# renumber the rules after the inserted one
for old, new in (("9. 结尾不必解决问题。", "10. 结尾不必解决问题。"), ("8. state 要写人的处境", "9. state 要写人的处境"), ("7. ", "8. "), ("6. 不要让人物不停总结", "7. 不要让人物不停总结")):
    if old in a1:
        a1 = a1.replace(old, new, 1)
W("R_A1.txt", a1)

a2 = R("Q3_A2.txt")
a2 = sub(a2, "你完全看不到珠子，也不要根据音乐细节评判。", "不要根据音乐细节评判。最后还附了这首作品逐段的体验性质（从听感记录里去掉画面和情节后留下的）。")
a2 = sub(a2, "不要改写候选，只能选择和诊断。", """另外逐条检查：
- 是不是靠“找办法、试办法、发现不管用、下决心”这类心理动作一步步推进？这是严重问题。
- 这条路线的处境，能不能在各段自然容纳附上的大部分体验性质？只有一两种情绪反复出现、容纳不下其他性质的路线，即使逻辑整齐也要扣分。这一项只看容纳能力，不要因此奖励照着体验性质编出来的情节。
再给 fit：1–10。

不要改写候选，只能选择和诊断。""")
W("R_A2.txt", a2)

W("R_A3.txt", R("Q3_A3.txt"))

a4 = R("Q3_A4.txt")
a4 = sub(a4, "Thread 只需要提供一个人的经历，使其中一些性质自然成立。", "Thread 提供一个人的经历，让这一段的大部分性质都能在其中自然成立：一个处境常常能同时容纳几种性质，写之前先想想这一段的处境还能容纳什么，不要只写最顺手的那一种。")
a4 = sub(a4, "不要写格言、人生原则或作者替人物作总结。", "不要写格言、人生原则或作者替人物作总结。\n" + MOVES + "\n不要给他的做法或顾虑起一个名字然后反复用这个词。")
W("R_A4.txt", a4)

q = json.loads(R("Q3.json"))
q["name"] = "R"; q["note"] = "方案 R：经历骨架（不缩窄 Center、不靠对方新举动、不靠心理动作推进）→ 选路也看体验性质 → 写线让一段大部分性质成立"
for s in q["steps"]:
    s["prompt_file"] = "R_" + s["prompt_file"].split("_", 1)[1]
    if s["id"] == "A2":
        s["after"] = ["A1", "A3"]
        s["replace"]["{TARGETS}"] = "step:A3"
        s["append"] = s["append"] + "\n\n【逐段的体验性质】\n{TARGETS}"
    if s["id"] == "A3":
        s["after"] = []
W("R.json", json.dumps(q, ensure_ascii=False, indent=2))
print("ok", [(s["id"], s.get("after")) for s in q["steps"]])
