"""Thread finders from three entries: T research only / Beads only / both. 5 independent GPT-6 lanes each."""
import thr, common

TPL = (thr.ROOT / "prompts" / "find_v1.md").read_text(encoding="utf-8")
SEG = f"全曲按 PTNA／朝山冻结的十四段：{common.SEGLIST}。"
ENTRIES = {
    "T": (f"{SEG}\n\n{common.MAT_T}", True),
    "B": (f"{SEG}\n\n{common.MAT_B}\n\n{common.beads_text()}", False),
    "TB": (f"{SEG}\n\n{common.MAT_T}\n\n{common.MAT_B}\n\n{common.beads_text()}", True),
}
LANES = 5
keys = []
for e, (mat, att) in ENTRIES.items():
    p = TPL.replace("{MATERIALS}", mat).replace("{WEB_NOTE}", "不要联网搜索。")
    for i in range(1, LANES + 1):
        name = f"{e}-{i}"

        def fn(name=name, p=p, att=att):
            return thr.finish_text("find", name, thr.call("find", name, p, [common.t_zip()] if att else []))
        thr.task("find", name, fn, kind="text"); keys.append(("find", name))

if __name__ == "__main__":
    for e, (mat, att) in ENTRIES.items():
        print(e, len(TPL.replace("{MATERIALS}", mat)))
    import sys
    if "run" in sys.argv:
        thr.run(keys)
