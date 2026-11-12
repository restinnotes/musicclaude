"""Round 2: rewrite the confirmed longitudinal understanding into a direct, felt reader version (GPT-6 and GPT-5.6),
then cross-audit with the same adversarial prompt."""
import json, re
import thr, common


def body(mk):
    t = thr.text("final_tell", mk)
    return t.split("## 与 Bead 的对照")[0].replace("## 纵向理解", "").strip()


def audits():
    out = []
    for mk, lab in (("g6", "草稿一"), ("g56", "草稿二")):
        d = thr.load("final_audit", mk)
        out.append(f"### 对{lab}\n结论：{d['verdict']}。{d['verdict_why']}\n真正的增益：\n" +
                   "\n".join(f"- {s['where']}：{s['why']}" for s in d["stops"] if s["kind"] == "增益") +
                   "\n只是重述或说明：\n" + "\n".join(f"- {s['where']}（{s['kind']}）" for s in d["stops"] if s["kind"] != "增益"))
    return "\n\n".join(out)


TPL = (thr.ROOT / "prompts" / "alive_v1.md").read_text(encoding="utf-8")
AUD = (thr.ROOT / "prompts" / "audit_v1.md").read_text(encoding="utf-8")
keys = []
for mk, model, other in (("g6", thr.G6, thr.G56), ("g56", thr.G56, thr.G6)):
    def write(mk=mk, model=model):
        p = (TPL.replace("{T1}", body("g6")).replace("{T2}", body("g56")).replace("{AUDITS}", audits())
             .replace("{BEADS}", common.beads_text()))
        return thr.finish_text("alive", mk, thr.call("alive", mk, p, model=model))
    thr.task("alive", mk, write, kind="text"); keys.append(("alive", mk))

    def audit(mk=mk, other=other):
        t = thr.text("alive", mk).split("## 解释边界")[0]
        p = AUD.replace("{TELL}", t).replace("{BEADS}", common.beads_text())
        return thr.finish_json("alive_audit", mk, thr.call("alive_audit", mk, p, model=other))
    thr.task("alive_audit", mk, audit, [("alive", mk)]); keys.append(("alive_audit", mk))

if __name__ == "__main__":
    thr.run(keys)
