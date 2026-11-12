"""11-02 round 2 advisors (迭代准则 I02, focused): all round-1 results are in; the open question is how to raise bead coverage without
local patching and without translating beads. Advisors see standard, constraints, experiment log, the best scheme's prompts (Q1),
its line and the coverage verdicts on it. ids adv2_<j>.  usage: python advisor2.py"""
import json
from pathlib import Path
import evo, v6fix as V

HERE = Path(__file__).parent
TAG = "qb"

P = """我们在迭代一条写作流水线：给一首器乐作品生成一条“线”（一个人在这首曲子里经历的一件事，按段写成要点），和逐段的听感记录“珠子”排在一起给读者看。请认真想，可以大胆。

【标准（用户定的）】
{STD}

【硬约束和迭代范围】
{RULES}

【已经试过的方案和结果（都读完，不要重复已经证明不行的路）】
{LOG}

【目前最好的方案 Q1 的各层提示词】
{PROMPTS}

【Q1 写出的线（Op.60）】
{LINE}

【覆盖评委对这条线的判定：接得不好的珠子和理由】
{WEAK}

【问题】
现在的局面：写线时能看到“去掉画面和情节的体验性质”时，人话和单独成立都赢了现行流水线，但覆盖明显低（Op.60 约 35–38/50，Op.61 约 47–49/53）；旧的做法靠事后逐段补珠子把覆盖提到 50，但把珠子的情节搬进了线、句子塞满；完全不见珠子则覆盖崩到 25–34。

1. 这些没接上的珠子，真正缺的是什么？是路线选窄了、写线时没用上体验性质、一段的处境容纳不下、还是评委太严？请看具体的判定，给出你的判断。
2. 怎样才能把覆盖提到大约 90%（不必 100%），同时保住人话和单独成立，不翻译珠子，不事后打补丁？给出 1–2 个具体做法。要写出改动后的提示词（只写改动的那层，保持原占位符和输出结构）。
3. 还有没有别的值得一试的做法？

不要写针对这两首曲子的内容（检验：换一首完全不同的曲子，这句话还说得通吗？）。"""


def weak(w):
    c = json.loads((V.OUT / f"cov2_{TAG}.json").read_text(encoding="utf-8"))
    out = []
    seen = set()
    for j in V.JUDGES:
        d = V.parse(f"cov2_{w}_{j}_{TAG}") or {}
        for x in d.get("beads") or []:
            if x.get("status") != "说清":
                k = (x.get("sec"), x.get("bead"), j)
                if k not in seen:
                    seen.add(k); out.append(f"- {x.get('sec')} {x.get('bead')}（评委{j}：{x.get('status')}）：{str(x.get('why'))[:120]}")
    return "\n".join(out)


def msg():
    G = (HERE / "迭代准则.md").read_text(encoding="utf-8")
    rules = G[G.index("## 二、迭代范围和硬约束"):G.index("## 三、流程")]
    prompts = "\n\n".join(f"===== {f.name} =====\n{f.read_text(encoding='utf-8')}" for f in sorted((HERE / "schemes").glob("Q1_*.txt")))
    return P.format(STD=(HERE / "标准.md").read_text(encoding="utf-8"), RULES=rules, LOG=(HERE / "试验记录.md").read_text(encoding="utf-8"),
                    PROMPTS=prompts, LINE=V.view(V.graph_of("op60", TAG), center=True), WEAK=weak("op60"))


if __name__ == "__main__":
    m = msg(); print("材料长度", len(m), flush=True)
    jobs = []
    for j in ("g6", "g56"):
        r = f"adv2_{j}"
        if not evo.done(r):
            jobs.append((r, (lambda r=r, j=j: evo.call(r, m, model=V.JUDGES[j], meta={"stage": "advisor2"}))))
    if not evo.done("adv2_gem"):
        jobs.append(("adv2_gem", (lambda: evo.call_gemini_direct("adv2_gem", m, meta={"stage": "advisor2"}))))
    evo.run_parallel(jobs, 3)
    md = ["# 第二轮顾问：怎样提覆盖", ""]
    for j in ("g6", "g56", "gem"):
        md += [f"## {j}", "", (evo.output(f"adv2_{j}") or "（没有结果）") if evo.done(f"adv2_{j}") else "（没有结果）", ""]
    (V.OUT / "advisor2.md").write_text("\n".join(md), encoding="utf-8"); print("->", V.OUT / "advisor2.md")
