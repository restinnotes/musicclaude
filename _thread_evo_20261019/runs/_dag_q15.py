"""11-02: 迭代准则 I09 again. qu (Q15) passed acceptance and beats qo on every dimension of the side-by-side scores, and its form follows 标准.md. Mainline moves to Q15."""
from pathlib import Path

p = Path("DAG.md")
t = p.read_text(encoding="utf-8")
t = t.replace("`pipe.py run schemes/Q5.json` 的 A1", "`pipe.py run schemes/Q15.json` 的 A1")
old_start = t.index("| N05d 写线 |")
old_end = t.index("\n", old_start)
t = t[:old_start] + ("| N05d 写线 | 看路线和体验性质（不看珠子原文），定一条路线，一次写完：前因只来自他自己先前的经历；方向和体验性质对齐但不把它当台词；"
                     "写他心里直接冒出来的念头，不搭心理分析的句子；每段 2–4 条、每条一句；不事后补珠子 | 同上 A4 | GPT-6 | [模板](DAG/prompts/N05d_写线/模板.txt) | "
                     "⚠️ 单次抽样差异大：同一套做法有的抽样过验收，有的底线不过 |") + t[old_end:]
t = t.rstrip() + """
- **11-02（写线层再换一次，主线 `qu`）**：写线层换成 Gemini 看过两轮结果后写的版本，形态按标准改回每段 2–4 条、每条一句，加回引用要求（`schemes/Q15.json`、`schemes/Q15_A4.txt`），前三层不变。成品 `qu`：字数 1502/1528；覆盖 Op.60 49/50、Op.61 49/48；单独读成立 12/14、13/14、13/13、13/13；每条都是一句。和原主线 `m6w` 盲比 8 份：6 份选新版，6 份判不算退步；净胜 单独 +5.0、啰嗦 +9.0、人话 +12.0、覆盖 −0.38。上一条的 `qo` 也过了验收，但五版一起盲打分时每个维度都低于 `qu`。
"""
p.write_text(t, encoding="utf-8")
d = Path("dag_export.py")
s = d.read_text(encoding="utf-8")
assert '"Q5_A4.txt"' in s
s = s.replace('ROOT / "schemes" / "Q5_A4.txt"', 'ROOT / "schemes" / "Q15_A4.txt"')
d.write_text(s, encoding="utf-8")
print("ok")
