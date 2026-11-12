"""Two independent compare/synthesis sessions over all 15 finder outputs (anonymised, shuffled differently)."""
import json, random, sys
import thr, common

TPL = (thr.ROOT / "prompts" / "compare_v1.md").read_text(encoding="utf-8")
FINDERS = sorted(p.stem.replace(".response", "") for p in (thr.RUNS / "find").glob("*.response.txt"))


def build(cid):
    order = FINDERS[:]; random.Random(f"compare-{cid}").shuffle(order)
    mapping = {f"L{i+1:02d}": f for i, f in enumerate(order)}
    z = thr.RUNS / f"finders_{cid}.zip"
    import zipfile
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as f:
        for lab, src in mapping.items():
            f.writestr(f"{lab}.md", thr.text("find", src))
    (thr.RUNS / f"finders_{cid}.mapping.json").write_text(json.dumps(mapping, ensure_ascii=False, indent=1), encoding="utf-8")
    p = (TPL.replace("{SEGLIST}", common.SEGLIST).replace("{N}", str(len(mapping))).replace("{NT}", str(len(thr.load_T())))
         .replace("{BEADS}", common.beads_text()))
    return p, [z, common.t_zip()]


keys = []
for cid in ("C1", "C2"):
    def fn(cid=cid):
        p, att = build(cid)
        return thr.finish_json("compare", cid, thr.call("compare", cid, p, att))
    thr.task("compare", cid, fn); keys.append(("compare", cid))

if __name__ == "__main__":
    assert len(FINDERS) == 15, FINDERS
    thr.run(keys)
