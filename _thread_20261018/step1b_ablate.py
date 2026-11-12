"""Ablation: Bead-entry finder without the explicit 'do not collapse into one emotional arc (e.g. happiness/loss/acceptance)' line."""
import thr, common
TPL = (thr.ROOT / "prompts" / "find_v1_nodebias.md").read_text(encoding="utf-8")
SEG = f"全曲按 PTNA／朝山冻结的十四段：{common.SEGLIST}。"
p = TPL.replace("{MATERIALS}", f"{SEG}\n\n{common.MAT_B}\n\n{common.beads_text()}").replace("{WEB_NOTE}", "不要联网搜索。")
keys = []
for i in (1, 2, 3):
    name = f"B0-{i}"
    def fn(name=name):
        return thr.finish_text("find_ablate", name, thr.call("find_ablate", name, p))
    thr.task("find_ablate", name, fn, kind="text"); keys.append(("find_ablate", name))
if __name__ == "__main__":
    thr.run(keys)
