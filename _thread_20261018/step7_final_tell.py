"""Round 2 final: write the short whole-piece longitudinal understanding from audit-confirmed gains (GPT-6 and GPT-5.6,
fresh sessions), then cross-audit with the same adversarial audit prompt."""
import json, re
import thr, common

CAND = {"TA": "承托", "TB": "旧话重提", "TC": "各有其声", "TD": "美好与时间", "TE": "离开与归来"}


def first_bar(s):
    n = re.findall(r"\d+", s or "")
    return int(n[0]) if n else 999


def keep_text():
    items = []
    for c, label in CAND.items():
        for m in ("g6", "g56"):
            d = thr.load("audit", f"{c}-{m}")
            for s in d["stops"]:
                if s["kind"] == "增益":
                    items.append((first_bar(s["where"]), s["where"], label, s["quote"], s["why"]))
            for k in d.get("keep_lines", []):
                items.append((first_bar(k["quote"]) if re.search(r"第\d", k["quote"]) else 900, "（整篇中值得留下的句子）", label, k["quote"], k["why"]))
    items.sort(key=lambda x: x[0])
    return "\n".join(f"- 【{w}｜候选：{lab}】「{q}」——审读理由：{why}" for _, w, lab, q, why in items)


TPL = (thr.ROOT / "prompts" / "final_tell_v1.md").read_text(encoding="utf-8")
AUD = (thr.ROOT / "prompts" / "audit_v1.md").read_text(encoding="utf-8")
keys = []
for mk, model, other in (("g6", thr.G6, thr.G56), ("g56", thr.G56, thr.G6)):
    def tell(mk=mk, model=model):
        p = TPL.replace("{KEEP}", keep_text()).replace("{BEADS}", common.beads_text())
        return thr.finish_text("final_tell", mk, thr.call("final_tell", mk, p, model=model))
    thr.task("final_tell", mk, tell, kind="text"); keys.append(("final_tell", mk))

    def audit(mk=mk, other=other):
        p = AUD.replace("{TELL}", thr.text("final_tell", mk)).replace("{BEADS}", common.beads_text())
        return thr.finish_json("final_audit", mk, thr.call("final_audit", mk, p, model=other))
    thr.task("final_audit", mk, audit, [("final_tell", mk)]); keys.append(("final_audit", mk))

if __name__ == "__main__":
    import sys
    if "dry" in sys.argv:
        p = TPL.replace("{KEEP}", keep_text()).replace("{BEADS}", common.beads_text()); print(len(p)); print(keep_text()[:1500])
    else:
        thr.run(keys)
