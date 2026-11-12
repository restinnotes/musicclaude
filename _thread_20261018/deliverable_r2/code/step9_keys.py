"""Round 2: structured final (thread statement + 4-5 key moments, each: what Bead already gives / what the thread adds),
from audit-confirmed best lines. GPT-6 and GPT-5.6, fresh sessions."""
import re
import thr, common
import step7_final_tell as s7


def keep_all():
    items = []
    for c, label in s7.CAND.items():
        for m in ("g6", "g56"):
            for k in thr.load("audit", f"{c}-{m}").get("keep_lines", []):
                items.append(k["quote"])
    for m in ("g6", "g56"):
        for k in thr.load("final_audit", m).get("keep_lines", []):
            items.append(k["quote"])
    seen, out = set(), []
    for q in items:
        if q not in seen:
            seen.add(q); out.append(q)
    return "\n".join(f"- 「{q}」" for q in out)


TPL = (thr.ROOT / "prompts" / "keys_v1.md").read_text(encoding="utf-8")
keys = []
for mk, model in (("g6", thr.G6), ("g56", thr.G56)):
    def write(mk=mk, model=model):
        p = TPL.replace("{KEEP}", keep_all()).replace("{BEADS}", common.beads_text())
        return thr.finish_text("keys", mk, thr.call("keys", mk, p, model=model))
    thr.task("keys", mk, write, kind="text"); keys.append(("keys", mk))

if __name__ == "__main__":
    import sys
    if "dry" in sys.argv:
        print(len(keep_all().splitlines()), len(TPL.replace("{KEEP}", keep_all()).replace("{BEADS}", common.beads_text())))
    else:
        thr.run(keys)
