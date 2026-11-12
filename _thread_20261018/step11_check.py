"""Independent adversarial check of the chosen final (keys/g6) by GPT-5.6 (fresh session)."""
import thr, common
AUD = (thr.ROOT / "prompts" / "audit_v1.md").read_text(encoding="utf-8")
def fn():
    p = AUD.replace("{TELL}", thr.text("keys", "g6")).replace("{BEADS}", common.beads_text())
    return thr.finish_json("keys_audit", "g6", thr.call("keys_audit", "g6", p, model=thr.G56))
thr.task("keys_audit", "g6", fn)
if __name__ == "__main__":
    thr.run([("keys_audit", "g6")])
