"""11-02 my synthesis after Q1/Q2: Q2's rules for the experience skeleton (don't narrow the Center, no new facts about the other person
as a trigger, one event != one mechanism) + Q1's way of writing (the writer sees bead qualities, 10-23 user: synthesis may see beads),
because Q2's beads-free writer came out thin (about 650 chars, all one thought)."""
import json
from pathlib import Path
S = Path(__file__).parent
R = lambda n: (S / n).read_text(encoding="utf-8")
W = lambda n, t: (S / n).write_text(t, encoding="utf-8")


def sub(t, old, new):
    assert old in t, old[:40]
    return t.replace(old, new)


a1 = R("Q2_A1.txt")
a1 = sub(a1, "这个层完全不看珠子。这里产出的每条候选，如果后来被选中，其中的 state 文本会原样进入最终 Thread，不再根据珠子改写；因此这一层既要把经历本身想清楚，也要把每条 state 写成最终可用的人话。",
         "这个层完全不看珠子，只负责把这件事本身想清楚；最终文字由后面一层写。")
a1 = sub(a1, "- 作品名只用于识别作品。即使你知道这首作品的音乐细节，也不能根据某段音乐的强弱、停顿、回返、上升、下降或其他走势，为人物反推同样形状的心理动作。",
         "- 可以用你对这首作品的了解（也可以联网查）安排各阶段的轻重，让这件事贴合作品常被听出的气质和走向；但不要因为某段音乐怎么动，就给人物安排同样形状的心理动作。")
a1 = sub(a1, "  - state：本段最终可直接使用的 Thread 文本，2–4 条，按顺序排列", "  - state：本段此刻实际是什么情况，1–3 条")
W("Q3_A1.txt", a1)

a2 = R("Q2_A2.txt")
a2 = sub(a2, "这些候选中的 state 已经按最终 Thread 的标准写好。你选中的第一名，后续会在看见珠子之前被冻结；以后只能把珠子匹配到它上面，不能再根据珠子改写它。\n\n", "")
a2 = sub(a2, "第一名就是正式 primary route：它必须只根据上述 Thread 本身的质量选出。后续即使发现别的候选更容易匹配珠子，也不能因此更换第一名。\n\n第二、第三名只作为诊断和回退候选，不影响第一名已经在看珠子之前确定这一事实。\n\n", "")
W("Q3_A2.txt", a2)

a3 = R("Q2_A3.txt")
a3 = sub(a3, "你只负责把每一颗珠子转换成供后续“匹配已经写好的 Thread”使用的体验性质。\n\n后续 Thread 在看到你的输出以前就已经写完并冻结。你的输出不能成为人物剧情、心理动作或语言的脚本。",
         "你只负责把每一颗珠子转换成供后续写线时参考的体验性质。你的输出不能成为人物剧情、心理动作或语言的脚本。")
W("Q3_A3.txt", a3)

a4 = R("Q1_A4.txt")
a4 = sub(a4, "另一条候选里的局部想法，只有在不新增人物前提、也不改变 base_route 已成立事实时才能采用。\n", "")
W("Q3_A4.txt", a4)

q = json.loads(R("Q1.json"))
q["name"] = "Q3"; q["note"] = "方案 Q3：Q2 的经历规则（不缩窄 Center、不靠对方新举动发动）+ Q1 的写法（写线时看去掉画面情节的体验性质）"
for s in q["steps"]:
    s["prompt_file"] = "Q3_" + s["prompt_file"].split("_", 1)[1]
W("Q3.json", json.dumps(q, ensure_ascii=False, indent=2))
print("ok")
