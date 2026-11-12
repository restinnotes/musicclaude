"""11-02: 迭代准则 I09. Write the accepted scheme (Q5: skeleton -> route pick -> experience qualities -> one-pass writer) into DAG.md. Backup kept next to it."""
import re, shutil
from pathlib import Path

H = Path(".")
p = H / "DAG.md"
shutil.copy(p, H / "标准_材料" / "DAG_换主线前_20261102.md")
t = p.read_text(encoding="utf-8")

t = t.replace("地位：和 `THREAD_SPEC.md` 同等。", "地位：现行主线，要做到什么看 `标准.md`，怎么改看 `迭代准则.md`。")

new_flow = """  N04c --> N05a[N05a 经历骨架 ×3：不看珠子，只想清这件事]
  N01 --> N05a
  N05a --> N05b[N05b 选路：不看珠子，给三条路线排序]
  N03i --> N05c[N05c 体验性质：珠子去掉画面和情节]
  N01 --> N05c
  N05a --> N05d[N05d 写线：定一条路线，先想清整篇，再一次写完]
  N05b --> N05d
  N05c --> N05d
  N05d --> N10[N10 测量：覆盖 / 单独读 / 盲评]
  N10 --> N12[N12 合写：线和珠子逐字排列，只显示小节号]
"""
a = t.index("  N04c --> N05[")
b = t.index("  N03i --> N12")
t = t[:a] + new_flow + t[b:]

rows = """| N05a 经历骨架 | 不看珠子，写 3 条这个人的经历路线：每段此刻什么情况、真正新增了什么、依赖哪条前因、还悬着什么，加一份“已经成立的事”账本 | `pipe.py run schemes/Q5.json` 的 A1 | GPT-6（联网不限） | [模板](DAG/prompts/N05a_经历骨架/模板.txt) | ✅ |
| N05b 选路 | 不看珠子，只按这件事本身给 3 条路线打分排序 | 同上 A2 | GPT-6 | [模板](DAG/prompts/N05b_选路/模板.txt) | ✅ |
| N05c 体验性质 | 把每颗珠子去掉音乐、比喻和想象情节，只留体验性质和先后变化 | 同上 A3 | GPT-6 | [模板](DAG/prompts/N05c_体验性质/模板.txt) | ✅ |
| N05d 写线 | 看路线和体验性质（不看珠子原文），定一条路线；动笔前先想清每段的处境和它的另外一面；一次写完整条线，每段 2–4 条、每条一句，不事后补珠子 | 同上 A4 | GPT-6 | [模板](DAG/prompts/N05d_写线/模板.txt) | ⚠️ 单次抽样差异大：同一提示词一次过验收，一次底线不过 |
"""
first = t.index("| N05 写稿 |")
t = t[:first] + rows + t[first:]
for n in ("N05 写稿", "N06 转关系图", "N07 抽词义", "N08 通用改写", "N09b 人话改写", "N09 开放评审", "N09c 按评审改", "N09v 句式多样化", "N09w 逐字精读", "N10c 提覆盖", "N10g 守覆盖", "N11 补漏"):
    assert f"| {n} " in t, n
    t = t.replace(f"| {n} ", f"| 🗄 {n}（11-02 被 N05a–d 替代）", 1)

t = t.rstrip() + """
- **11-02（主线换成“先想经历、再一次写完”）**：原来的写稿 → 转关系图 → 通用改写 → 人话改写 → 开放评审 → 按评审改 → 逐字精读 → 提覆盖 → 守覆盖 → 补漏，换成 N05a–d 四层（`schemes/Q5.json`，写线层是 GPT-6 看过顾问材料后写的，实际提示词 `schemes/Q5_A4.txt`）。成品 `qo`：字数 1678/1609（原 1206/1432）；覆盖 Op.60 48/48（共 50）、Op.61 48/49（共 53），原 50/50、46/49；单独读成立 13/14、12/14、13/13、13/13，原 11/14、12/14、11/13、11/13。和原主线 `m6w` 盲比 8 份：7 份选新版，6 份判不算退步；净胜 单独 +5.5、啰嗦 +2.9、人话 +10.4、覆盖 −2.75。不靠事后补珠子，线也不再把珠子的情节搬进来。旧 DAG 存 `标准_材料/DAG_换主线前_20261102.md`。过程和没过的方案见 `试验记录.md`。
"""
p.write_text(t, encoding="utf-8")
print("DAG.md 已更新", len(t))

d = H / "dag_export.py"
s = d.read_text(encoding="utf-8")
if "N05a_经历骨架" not in s:
    key = '    "N05a_写稿_主线":'
    assert key in s
    add = ('    "N05a_经历骨架": [("模板.txt", ("file", ROOT / "schemes" / "Q5_A1.txt"))],\n'
           '    "N05b_选路": [("模板.txt", ("file", ROOT / "schemes" / "Q5_A2.txt"))],\n'
           '    "N05c_体验性质": [("模板.txt", ("file", ROOT / "schemes" / "Q5_A3.txt"))],\n'
           '    "N05d_写线": [("模板.txt", ("file", ROOT / "schemes" / "Q5_A4.txt"))],\n')
    d.write_text(s.replace(key, add + key), encoding="utf-8")
    print("dag_export 已加四个节点")
