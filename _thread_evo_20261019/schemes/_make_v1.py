"""11-02 first-output fixes (迭代准则：第一个产物不对立刻修). P1_A0: no invented life settings; Q1_*: Center is given (it is frozen, the
line must be about it), JSON output. Originals stay untouched."""
import json
from pathlib import Path
S = Path(__file__).parent
R = lambda n: (S / n).read_text(encoding="utf-8")
W = lambda n, t: (S / n).write_text(t, encoding="utf-8")

# ---------- P1 ----------
a0 = R("P_A0.txt")
i, j = a0.index("一、人物与事情"), a0.index("二、真正的历史")
a0 = a0[:i] + """一、人物与事情

每条候选必须是同一个人从头到尾经历的同一件事。

明确他在意的是什么、为什么在意。说到这个程度就够：
可以是“一个人”“一段关系”“从前的生活”这样说得出
性质的对象。

不虚构具体的生活设定：职业、工作机会、亲属身份、年龄、
地点、物件、具体发生过的事，都不要写。
可以有一个从头到尾不变的、很轻的处境，但它不产生新事件。
变化只发生在这个人心里。

不要用一个抽象问题代替人物经历。要具体，就具体在他的
所求、顾虑和感受上，不是具体在情节上。

这件事要贴合这首作品本身常被听出的气质和走向：
可以用你对这首作品的了解，也可以联网查资料。

""" + a0[j:]
a0 = a0.replace("""三条候选应在人物究竟经历什么、为什么在意、
或怎样逐渐变化上有实质差异。""", """三条候选都围绕上面给定的 Center，应在他为什么在意、
或怎样逐渐变化上有实质差异。""")
assert "逐渐变化上有实质差异" in a0 and "Center，应在" in a0
W("P1_A0.txt", a0)
p = json.loads(R("P.json"))
p["name"] = "P1"; p["note"] = "方案 P1：P 第一步改为不虚构具体生活设定、贴合作品（可联网）；其余同 P"
st = next(s for s in p["steps"] if s["id"] == "A0"); st["prompt_file"] = "P1_A0.txt"
st["replace"]["{INDEPENDENT_MUSIC_CONTEXT}"] = {"text": "（没有另外提供；可以用你对这首作品的了解，也可以联网查。）"}
W("P1.json", json.dumps(p, ensure_ascii=False, indent=2))

# ---------- Q1 ----------
q1 = R("Q_A1.txt")
old = "- 不写正式 Center。Center 会在最终 Thread 写完后再归纳。"
assert old in q1
q1 = q1.replace(old, "- Center 已经给定，见下。它是读者回头看整首时把各段组织起来的那件事；不是他一开始就清楚知道的事，也不是每一段都要回应的题目；不预告发展路线和结局。")
old = "段落顺序：{SECTIONS}"
assert old in q1
q1 = q1.replace(old, "段落顺序：{SECTIONS}\nCenter：{CENTER}")
old = "不要写最终文案，不要写 Center，不要评价候选。"
assert old in q1
q1 = q1.replace(old, "不要写最终文案，不要评价候选。")
old = "只输出结构化结果。"
assert old in q1
q1 = q1.replace(old, "只输出 JSON（字段名照上面写的）。")
W("Q1_A1.txt", q1)
q2 = R("Q_A2.txt"); old = "输出结构化结果。"; assert old in q2
W("Q1_A2.txt", q2.replace(old, "只输出 JSON。"))
q3 = R("Q_A3.txt"); old = "只输出结构化结果。"; assert old in q3
W("Q1_A3.txt", q3.replace(old, "只输出 JSON（字段名照上面写的）。"))
q4 = R("Q_A4.txt")
old = "【段落】\n{SECTIONS}"
assert old in q4
q4 = q4.replace(old, "【段落】\n{SECTIONS}\n\n【这件事（Center，已经给定，不改）】\n{CENTER}\n它是回头看整首时把各段组织起来的那件事，不是每一段都要回应的题目。")
old = "你看到三类材料："
assert old in q4
q4 = q4.replace(old, "你看到这些材料：")
W("Q1_A4.txt", q4)
q = json.loads(R("Q.json"))
q["name"] = "Q1"; q["note"] = "方案 Q1：Q 加上给定的 Center，中间步骤输出 JSON；其余同 Q"
for s in q["steps"]:
    s["prompt_file"] = "Q1_" + s["prompt_file"].split("_", 1)[1]
    if s["id"] in ("A1", "A4"):
        s["replace"]["{CENTER}"] = "CENTER"
W("Q1.json", json.dumps(q, ensure_ascii=False, indent=2))
print("ok")
