"""One targeted resume of the final2_b/S10 session: bring B3/B4 measures inside 216–225 (text must stay identical).
Output stage final3_b; accepted only if every bead text / reader is unchanged (checked below)."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import sat  # noqa: E402

SEG = "S10"
P = """脚本检查发现：你刚才输出的 S10（第 216–225 小节）里，B3 和 B4 的 `measures` 写成了「214–225」，起点落在相邻的 S09（第 214–215 小节）里。每个 bead 的 `measures` 必须落在本段 216–225 之内。

请只修正 B3、B4 的 `measures`（如有需要连同 `placement`）：如果这两种理解在本段内成立，就写成本段内的范围；原稿范围更宽这一点可以留在括号说明或 `internal_note` 里，但起止数字要在 216–225 内。**不要改动任何 `text`、`reader`、`title`、`sources` 或其他字段的文字。**

然后重新输出 S10 完整的同一 JSON 结构（只输出一个 JSON 代码块，直接写在回答正文里，不要生成文件或下载链接，不要联网搜索）。"""

if not sat.load("final3_b", SEG):
    sat.finish("final3_b", SEG, sat.call("final3_b", SEG, P, session=sat.handle("final2_b", SEG)))
a, b = sat.load("final2_b", SEG), sat.load("final3_b", SEG)
if not b:
    sys.exit("final3_b/S10 failed")
same = (a["reader"] == b["reader"] and a["title"] == b["title"]
        and [x["text"] for x in a["beads"]] == [x["text"] for x in b["beads"]])
print("text unchanged:", same)
print([(x["id"], x["measures"], x["placement"]) for x in b["beads"]])
if not same:
    (ROOT / "runs" / "final3_b" / f"{SEG}.REJECTED_text_changed").write_text("x")
