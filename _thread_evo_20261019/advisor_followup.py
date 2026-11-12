"""11-02 迭代准则 I12/I13: hand a screened scheme's results back to the advisor who proposed it. The advisor sees the standard,
the hard constraints, the prompts it proposed (as actually run), the line they produced, and every measurement with reasons
(blind per-segment reasons + lost lists, single-read weak / repeated segments, bead-copying items, open-review problems),
and decides: 放弃 (this road cannot work, say why) or 改了再试 (give complete revised prompt files).
usage: python advisor_followup.py <scheme letter P|Q> <tag> [base=m6w]   -> evaluations/v6fix/followup_<tag>.md, schemes/<new>_*.txt"""
import json, os, re, sys
from pathlib import Path
import evo, v6fix as V

HERE = Path(__file__).parent
WHO = {"P": ("g6", "GPT-6"), "Q": ("g56", "GPT-5.6")}

P = """你之前为我们的写作流水线提出过一套改造方案。我们按你的方案实际跑了一次（两首作品），下面是结果。请你作为这套方案的提出者，看完后判断下一步。

【标准（用户定的，以此为准）】
{STD}

【任何方案都必须满足的硬约束】
{RULES}

【你的方案：实际运行的各层提示词】（我们只做过一处改动的地方会注明）
{PROMPTS}

【它产出的线】
{LINES}

【测量结果】（主线 = 现在流水线的成品，用来比较）
{MEAS}

【请你判断】
1. 结果说明了什么：哪些地方比主线好、哪些更差；更差的地方是方案本身的思路造成的，还是某一层提示词没写好、某个约束没表达清楚？请具体到层和句子。
2. 结论二选一：
   - 放弃：这条路本身不行。写清为什么，以后的方案要避开什么。
   - 改了再试：方向对，给出改过的提示词。只改需要改的层，但改了的层要写出完整的新提示词；保持原来的占位符（{{…}}）和输出 JSON 结构不变，以便直接运行。
3. 改动不能违反标准和硬约束，尤其不能写针对这两首曲子的内容或例子（检验：换一首完全不同的曲子，这句话还说得通吗？）。

输出格式：先用中文写分析；然后单独一行写“结论：放弃”或“结论：改了再试”；如果改了再试，每个改过的提示词文件用下面的格式给出（文件名用原来的，如 P_A2.txt）：
=====FILE: 文件名=====
（完整提示词）
=====END====="""


def meas_text(tag, base):
    out = []
    for t in (base, tag):
        c = json.loads((V.OUT / f"cov2_{t}.json").read_text(encoding="utf-8")) if (V.OUT / f"cov2_{t}.json").exists() else {}
        a = json.loads((V.OUT / f"alone2_{t}.json").read_text(encoding="utf-8")) if (V.OUT / f"alone2_{t}.json").exists() else {}
        for w in ("op60", "op61"):
            for j in ("g6", "g56"):
                cc = (c.get(f"{w}_{j}") or {}).get("total", {}); aa = a.get(f"{w}_{j}") or {}
                out.append(f"- {'主线' if t == base else '你的方案'} {w} 评委{j}：覆盖 说清 {cc.get('说清', '?')} 偏弱 {cc.get('偏弱', '?')} 没有 {cc.get('没有', '?')} 相反 {cc.get('相反', '?')}；"
                           f"单独读 {aa.get('self')}；重说 {aa.get('repeat')} 段；标签对不上 {aa.get('label_mismatch')} 段；复述珠子 {(aa.get('trans') or {}).get('复述珠子')} 条")
                if t == tag:
                    out += [f"    · 单独读不够的段 {s} {st}：{why}" for s, st, why in aa.get("weak_secs") or []]
                    out += [f"    · 复述珠子 {i}（{b}）：{why}" for i, lab, b, why in (aa.get("retold") or [])[:12]]
    b = V.OUT / f"blind2_{tag}_vs{base}.md"
    if b.exists():
        out += ["", "【盲比全文（新版 vs 主线，每段理由、丢失清单）】", b.read_text(encoding="utf-8")[:20000]]
    e = V.OUT / f"e2e_open2_{tag}.md"
    if e.exists():
        txt = e.read_text(encoding="utf-8")
        out += ["", "【四维开放评审对你的方案挑出的问题】", txt[:12000]]
    return "\n".join(out)


def msg(letter, tag, base):
    G = (HERE / "迭代准则.md").read_text(encoding="utf-8")
    rules = G[G.index("## 二、迭代范围和硬约束"):G.index("## 三、流程")]
    files = sorted((HERE / "schemes").glob(f"{letter}_*.txt"))
    prompts = "\n\n".join(f"===== {f.name} =====\n{f.read_text(encoding='utf-8')}" for f in files)
    if letter == "P":
        prompts += "\n\n（注：P_A2 的“七、Center”一节，我们改成了使用上游已定的 Center、不重写；P_A0 的段落后面附了上游 Center。原因：Center 已定，不在迭代范围。）"
    if letter == "Q":
        prompts += "\n\n（注：Q_A2、Q_A3 末尾分别附上了候选路线、段落和珠子；Q_A4 的 ROUTES 后附了宏观评审结果。成品展示时用上游已定的 Center。）"
    lines = "\n\n".join(V.view(V.graph_of(w, tag), center=True) for w in ("op60", "op61"))
    return P.format(STD=(HERE / "标准.md").read_text(encoding="utf-8"), RULES=rules, PROMPTS=prompts, LINES=lines, MEAS=meas_text(tag, base))


def apply(letter, tag, newletter):
    o = evo.output(f"fu_{tag}") or ""
    verdict = "改了再试" if "结论：改了再试" in o else ("放弃" if "结论：放弃" in o else "?")
    files = re.findall(r"=====FILE:\s*(\S+?)=====\n(.*?)\n=====END=====", o, flags=re.S)
    written = []
    for name, body in files:
        nn = newletter + name[len(letter):] if name.startswith(letter + "_") else name
        (HERE / "schemes" / nn).write_text(body.strip() + "\n", encoding="utf-8"); written.append(nn)
    # unchanged layers are copied so the new letter is a complete scheme
    for f in (HERE / "schemes").glob(f"{letter}_*.txt"):
        nn = newletter + f.name[len(letter):]
        if not (HERE / "schemes" / nn).exists():
            (HERE / "schemes" / nn).write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
    (V.OUT / f"followup_{tag}.md").write_text(o, encoding="utf-8")
    print(tag, "结论", verdict, "改写的文件", written, flush=True)
    return verdict, written


if __name__ == "__main__":
    letter, tag = sys.argv[1], sys.argv[2]; base = sys.argv[3] if len(sys.argv) > 3 else "m6w"
    newletter = os.environ.get("NEW", letter + "2")
    m = msg(letter, tag, base); print("材料长度", len(m), flush=True)
    j, _ = WHO[letter[0]]
    if not evo.done(f"fu_{tag}"):
        evo.call(f"fu_{tag}", m, model=V.JUDGES[j], meta={"stage": "followup"})
    apply(letter, tag, newletter)
