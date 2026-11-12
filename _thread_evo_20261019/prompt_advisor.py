"""11-02 (user: 评审时把提示词附上，让多个评审对提示词发表意见、想想没试过的好东西；大刀阔斧，不要每次只动一点):
prompt-level advisors. Each advisor gets the whole pipeline (every layer's prompt template), the outputs at each stage,
the four-goal open review of the current product (m6w), the user's judgments, a contrast version the user liked (f8,
made with hand-written per-segment notes), the spec, and is asked to diagnose which prompt causes which problem and to
propose bold redesigns (delete / merge / reorder / rewrite layers) with full prompt text, plus ideas never tried.
ids adv_<judge>_r<k>.  usage: python prompt_advisor.py run | report"""
import json, os, sys
from pathlib import Path
import covjudge, evo, v6fix as V
import draft9, tgraph4, v6gen, v6human, v6boost, v6guard, v6word, lang_open, line_dag

HERE = Path(__file__).parent
TAG = os.environ.get("ADV_TAG", "m6w")


def view(w, t):
    return V.view(V.graph_of(w, t), center=True)


def e2e_summary(tag):
    import e2e_open as E
    out = []
    for w in ("op60", "op61"):
        for _, j, k in [x for x in E.runs() if x[0] == w]:
            e = V.parse(E.rid(w, j, k)) or {}
            if e:
                out.append(f"- {w}｜{E.NM[j]} 第{k}次：" + "；".join(e.get("top3") or []))
    return "\n".join(out)


def pipeline():
    spine_full = (HERE / "runs/lna4_op60_r1/prompt.txt").read_text(encoding="utf-8")
    L = [
        ("N05a 写初稿·第一步（连续文字，不分段、不写音乐；实发全文，以 Op.60 为例）", spine_full),
        ("N05b 写初稿·第二步（把上一步的线落到段落上）", draft9.S_LAY),
        ("N05c 挑稿（3 篇初稿，两位评委盲读打分，取最高）", line_dag.JUDGE),
        ("N06 转关系图（初稿 → 每段 2–4 条 + 箭头）", tgraph4.P),
        ("N07 Center 各部分释义", v6gen.GLOSS),
        ("N08 改写（关系图 → 说人话的条目；附 PLAIN_RULE）", v6gen.WRITE.replace("\n编号规则：", "\n" + v6gen.PLAIN_RULE + "\n编号规则：")),
        ("N09 语言开放评审（只读线，找语言问题）", lang_open.P2),
        ("N09c 按开放评审改", v6human.FIXOPEN),
        ("N10c 提覆盖（两轮；每轮只保留覆盖变好的段）", v6boost.FIX1),
        ("N09 再来一轮语言开放评审 + 按意见改（同上两个提示词）", "（同 N09、N09c）"),
        ("N10g 防丢覆盖（覆盖掉 ≥2 的段重写，仍低就退回）", v6guard.FIX),
        ("N09w 逐字精读（只做词句替换）", v6word.P),
    ]
    return "\n\n".join(f"===== {n} =====\n{p}" for n, p in L)


P = """你是一位帮我们改进一条“写作流水线”的顾问。请认真、详细地思考，不用顾及我们之前的做法，可以大刀阔斧。

【我们在做什么】
给一首器乐作品（古典钢琴曲）自动生成一份“成品”，两部分放在一起给读者：
- 珠子：逐段的音乐听感记录（已经做好，不改）。
- 线：一个人在这首曲子里经历的一件事，按音乐段落写成关系图（每段 2–4 条，条目间可以指回前面的某一条；每段标他此刻和整件事的关系：没在想 / 还说不清 / 正在面对）。线讲他自己的经历，用来把珠子串起来。
线由一条多层的流水线生成（下面附每一层的提示词）。流水线必须对任何新作品都能用：提示词里不能写针对某一首曲子的内容或例子。

【线要做到的四件事（也是我们的验收维度）】
1. 单独成立：只读线、不看珠子，每段他为什么此刻这样，都能由前面已经发生在他身上的事说明，有一条往前走的路；转折由他自己前面的经历引起，不由音乐事件引起。
2. 不啰嗦：每句有自己的用处；不重说前面说过的；这一段发生得少就写得短。
3. 像人话：像一个人平平常常讲自己的经历，不像心理分析或提纲。
4. 接得上珠子：每颗珠子的听感都能在线里找到情境相近的原因或处境；但线不翻译珠子里的画面、比喻、情节。
验收怎么测：覆盖（评委逐颗珠子判线有没有说清它的来由）、单独读（只读线逐段判讲不讲得通、有没有复述珠子）、新旧两版盲比 8 次（逐段比覆盖 / 啰嗦 / 人话）。

【标准（用户定的，以此为准）】
{SPEC}

【任何方案都必须满足的硬约束和迭代范围】
{RULES}

【以往试过的方案和结论（不要重复已经证明不行的路）】
{LOG}

【用户亲自下的评判（以这些为准）】
{USER}

【流水线：每一层的提示词】（{{…}} 是运行时填入的内容）
{PIPE}

【同一首（Op.60）在各层之后的样子】
--- 初稿（N05b 输出，开头部分） ---
{DRAFT}

--- 转关系图后（N06） ---
{M0}

--- 改写后（N08） ---
{M1}

--- 按语言开放评审改后（N09c） ---
{M2}

--- 两轮提覆盖后（N10c） ---
{M4K}

--- 最终成品（全部跑完；两首） ---
{FINAL60}

{FINAL61}

【Op.60 的珠子（供判断覆盖和“翻译珠子”）】
{BEADS}

【独立评审对最终成品挑出的主要问题（四维开放评审，多位评委）】
{E2E}

【对照：用户说“做得已经很不错了，只是要更人话一点”的一版（Op.60）】
注意：它用的是后来被换掉的旧 Center，而且是我们读完后手写逐段修改意见、反复修补出来的，不是流水线产出——这种手写意见不能泛化，所以不能当成品。它说明流水线目前离用户满意还有多远。
{F8}

【请你回答】
1. 诊断：上面挑出的每个主要问题，你认为是流水线哪一层、哪一句提示词造成或放大的？请引用提示词原文，说明机制。也指出哪些层在白白重写、互相抵消或越改越像。
2. 大改方案：给出 1–2 套你认为最可能大幅变好的流水线。可以删层、并层、改顺序、整层重写、换模型分工，也可以改变珠子进入的时机或方式（但珠子本身不改，也不能让线照抄珠子）。对你改动的每一层，给出完整的新提示词（不能写针对某首曲子的内容）。说明为什么它能同时守住覆盖和单独成立。
3. 没试过的好办法：有哪些我们显然没想到、但值得试的做法？
4. 风险：你的方案最可能在哪一维掉分，怎么提前发现？

输出用中文，结构清楚即可，不需要 json。新提示词请完整写出，放在代码块里。"""


def msg():
    draft = (HERE / "runs/ln4_op60_r1/output.txt").read_text(encoding="utf-8")
    G = (HERE / "迭代准则.md").read_text(encoding="utf-8")
    rules = G[G.index("## 二、迭代范围和硬约束"):G.index("## 三、流程")]
    return P.format(SPEC=(HERE / "标准.md").read_text(encoding="utf-8"), RULES=rules, LOG=(HERE / "试验记录.md").read_text(encoding="utf-8"),
                    USER=(HERE / "用户判定.md").read_text(encoding="utf-8"),
                    PIPE=pipeline(), DRAFT=draft[:1600] + "……（后略）",
                    M0=view("op60", "m0"), M1=view("op60", "m1"), M2=view("op60", "m2"), M4K=view("op60", "m4k"),
                    FINAL60=view("op60", TAG), FINAL61=view("op61", TAG), BEADS=covjudge.bead_text("op60"),
                    E2E=e2e_summary(TAG), F8=view("op60", "f8"))


ADV = [("g6", 1), ("g6", 2), ("g56", 1), ("gem", 1), ("argon", 1)]
NM = {"g6": "GPT-6", "g56": "GPT-5.6", "gem": "Gemini 3.8", "argon": "Argon"}


def rid(j, k):
    return f"adv_{TAG}_{j}_r{k}"


if __name__ == "__main__":
    if sys.argv[1] == "run":
        m = msg(); print("材料长度", len(m), flush=True)
        jobs = []
        for j, k in ADV:
            r = rid(j, k)
            if evo.done(r):
                continue
            mm = m + ("\n" if k == 2 else "")
            if j == "gem":
                jobs.append((r, (lambda r=r, mm=mm: evo.call_gemini_direct(r, mm, meta={"stage": "advisor"}))))
            elif j == "argon":
                jobs.append((r, (lambda r=r, mm=mm: evo.call_argon_direct(r, mm, meta={"stage": "advisor"}))))
            else:
                jobs.append((r, (lambda r=r, mm=mm, mo=V.JUDGES[j]: evo.call(r, mm, model=mo, meta={"stage": "advisor"}))))
        evo.run_parallel(jobs, 5)
    md = [f"# 提示词顾问（看 {TAG} 和整条流水线）", ""]
    for j, k in ADV:
        o = evo.output(rid(j, k)) if evo.done(rid(j, k)) else None
        md += [f"## {NM[j]} 第{k}次", "", o or "（没有结果）", ""]
    (V.OUT / f"advisor_{TAG}.md").write_text("\n".join(md), encoding="utf-8"); print("->", V.OUT / f"advisor_{TAG}.md")
