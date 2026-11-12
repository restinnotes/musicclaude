"""11-02 迭代准则 I12/I13, second form: the proposer of ONE layer (the writer layer A4) sees what its layer produced, with all reasons, and decides.
Only the writer layer is open; A1-A3 are shared with the other variants. ids fu_<tag>. usage: python advisor_followup2.py <letter> <tag> <who g6|g56|gem> <newletter> [base=m6w]
writes schemes/<new>_A1..A4.txt and <new>.json (a complete scheme, unchanged layers copied)."""
import json, re, shutil, sys
from pathlib import Path
import evo, v6fix as V
from advisor_followup import meas_text

HERE = Path(__file__).parent
S = HERE / "schemes"

P = """我们之前请你改写线那一层（下面的 A4）的提示词，好提高和珠子的贴合，同时保住人话和不啰嗦。我们按你的提示词实际跑了一次（两首作品，前面几层和别的版本共用）。下面是全部结果。请你作为这一层的提出者判断下一步。

【标准（用户定的，以此为准）】
{STD}

【任何方案都必须满足的硬约束】
{RULES}

【前面几层的提示词（只作背景，这一轮不改）】
{UP}

【你提出的写线层（实际运行的版本）】
{A4}

【它产出的线】
{LINES}

【测量结果】（主线 = 现在流水线的成品，用来比较）
{MEAS}

【覆盖评委判定为接得不好的珠子和理由】
{WEAK}

【同一批试验里其他写线层的结果（只给数字，帮你判断取舍）】
{OTHERS}

【请你判断】
1. 结果说明了什么：哪些比主线好，哪些更差；更差的地方是这一层提示词的哪句话造成的，还是上游路线带来的、这一层改不了？请具体到句子。
2. 评委说的问题不都要照办。先想想：这个问题读者真的会在意吗？照办会不会带来别的毛病？继续叠禁止条款容易写成机械的心理算账，优先想能换掉什么、去掉什么。
3. 结论二选一：
   - 放弃：这条路本身不行。写清为什么，以后要避开什么。
   - 改了再试：给出完整的新提示词。保持原来的占位符（{{…}}）和输出 JSON 结构不变，以便直接运行。
4. 不能违反标准和硬约束，不能写针对这两首曲子的内容或例子（检验：换一首完全不同的曲子，这句话还说得通吗？）。

输出格式：先用中文写分析；然后单独一行写“结论：放弃”或“结论：改了再试”；如果改了再试，新提示词用下面的格式给出：
=====FILE: {LETTER}_A4.txt=====
（完整提示词）
=====END====="""

OTHERS = """- Q5（GPT-6 第一版）：字数 1583/1538，覆盖 47/46（共50）、48/49（共53），盲比 3/4 选新版，净胜 单独+5.0 啰嗦+6.8 人话+5.0 覆盖-3.2
- Q6（Gemini 第一版）：字数 2495/1856，覆盖 49/48、51/52，盲比 4/4，净胜 单独+9.5 啰嗦-0.2 人话0 覆盖+11
- Q4（GPT-5.6 第一版）：字数 2188/1747，覆盖 49/49、50/47，盲比 3/4，净胜 单独+5.0 啰嗦-1.5 人话0 覆盖-1.2
- Q7（GPT-6 改版，写完再对照体验性质）：字数 1354/1676，覆盖 40/41、49/49，盲比 3/4，净胜 单独+7.5 啰嗦+6.5 人话+7.0 覆盖-6.25
- Q8（Gemini 改版）：字数 2167/2269，覆盖 50/50、50/51，盲比 4/4，净胜 单独+10 啰嗦+4.75 人话+7.5 覆盖-0.25
- Q9（GPT-5.6 改版，体验性质只作检查）：字数 931/879，覆盖 22/21、25/32，盲比 3/4，净胜 单独+3.5 啰嗦+8.75 人话+9 覆盖-11.5
- 主线字数 1206/1432。"""


def weak(tag):
    out = []
    for w in ("op60", "op61"):
        for j in ("g6", "g56"):
            d = V.parse(f"cov2_{w}_{j}_{tag}") or {}
            for x in d.get("beads") or []:
                if x.get("status") != "说清":
                    out.append(f"- {w} {x.get('sec')} {x.get('bead')}（评委{j}：{x.get('status')}）：{str(x.get('why'))[:150]}")
    return "\n".join(out)


def msg(letter, tag, base):
    G = (HERE / "迭代准则.md").read_text(encoding="utf-8")
    rules = G[G.index("## 二、迭代范围和硬约束"):G.index("## 三、流程")]
    up = "\n\n".join(f"===== Q1_{n}.txt =====\n{(S / f'Q1_{n}.txt').read_text(encoding='utf-8')}" for n in ("A1", "A2", "A3"))
    lines = "\n\n".join(V.view(V.graph_of(w, tag), center=True) for w in ("op60", "op61"))
    return P.format(STD=(HERE / "标准.md").read_text(encoding="utf-8"), RULES=rules, UP=up, A4=(S / f"{letter}_A4.txt").read_text(encoding="utf-8"),
                    LINES=lines, MEAS=meas_text(tag, base), WEAK=weak(tag), OTHERS=OTHERS, LETTER=letter)


def apply(letter, tag, new):
    o = evo.output(f"fu_{tag}") or ""
    (V.OUT / f"followup_{tag}.md").write_text(o, encoding="utf-8")
    verdict = "改了再试" if "结论：改了再试" in o else ("放弃" if "结论：放弃" in o else "?")
    fs = re.findall(r"=====FILE:\s*(\S+?)=====\n(.*?)\n=====END=====", o, flags=re.S)
    print(tag, "结论", verdict, "文件", [f[0] for f in fs], flush=True)
    if verdict != "改了再试" or not fs:
        return
    (S / f"{new}_A4.txt").write_text(fs[0][1].strip() + "\n", encoding="utf-8")
    q = json.loads((S / f"{letter}.json").read_text(encoding="utf-8"))
    q["name"] = new; q["note"] = f"{new}：{letter} 的提出者看过结果后改的写线层"
    for s in q["steps"]:
        if s["id"] == "A4":
            s["prompt_file"] = f"{new}_A4.txt"
    (S / f"{new}.json").write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    letter, tag, who, new = sys.argv[1:5]; base = sys.argv[5] if len(sys.argv) > 5 else "m6w"
    m = msg(letter, tag, base); print("材料长度", len(m), flush=True)
    r = f"fu_{tag}"
    if not evo.done(r):
        if who == "gem":
            evo.call_gemini_direct(r, m, meta={"stage": "followup"})
        else:
            evo.call(r, m, model=V.JUDGES[who], meta={"stage": "followup"})
    apply(letter, tag, new)
