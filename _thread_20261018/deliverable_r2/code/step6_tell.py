"""Round 2: for each Thread candidate, try to actually tell the whole piece (GPT-6 and GPT-5.6, fresh sessions),
then cross-audit each telling adversarially (the other GPT model, fresh session)."""
import json
import thr, common
import step3_inner_outer as s3

T24 = thr.zip_of("T_research24", {f"T/{k}.md": v for k, v in thr.load_T().items()})
assert len(thr.load_T()) == 24
SELT = {t["id"]: t for t in s3.SEL}


def inner_draft(tid):
    d = thr.load("inner_final", tid)
    return "\n\n".join(f"［{m.get('where')}］{m.get('inner')}" for m in d["moments"]) + f"\n\n［曲终回看］{d.get('retrospective')}"


CANDS = {
    "TA": lambda: f"{SELT['TA']['label']}。\n\n上一轮的说明：\n{SELT['TA']['text']}\n\n上一轮按这条线写的 Inner 草稿（可参考、可推翻）：\n{inner_draft('TA')}",
    "TB": lambda: f"{SELT['TB']['label']}。\n\n上一轮的说明：\n{SELT['TB']['text']}\n\n上一轮按这条线写的 Inner 草稿（可参考、可推翻）：\n{inner_draft('TB')}",
    "TC": lambda: f"{SELT['TC']['label']}。\n\n上一轮的说明：\n{SELT['TC']['text']}\n\n上一轮按这条线写的 Inner 草稿（可参考、可推翻）：\n{inner_draft('TC')}",
    "TD": lambda: ("美好正在发生，时间却不会停下：人怎样真正拥有已经感受过的美好。\n\n"
                   "这一候选是附件里多份纵向研究的中心说法（例如 T-gpt6w-int-1、T-luna-web-1、T-gpt56w-web-2），"
                   "也是上一轮只看 Bead 的寻找在去掉一句去偏置提示后自己提出的候选，原话是："
                   "「快乐还在，人已经开始舍不得——一个人仍与眼前的美好贴得很近，就已经开始舍不得它从身边流过。它最有力量的时候，幸福仍然完整地在场。」"
                   "请先读这些研究，再判断这条线在这首曲子里的真实分量。"),
    "TE": lambda: ("离开与归来：经历过别处以后，回来的还是不是原来那个“家”。\n\n"
                   "这一候选来自附件里 T-gpt56w-int-1、T-gpt56w-int-2、T-gpt56w-int-3 等纵向研究，原话包括："
                   "「它一直在问：归属和自由能不能同时成立？……只有当你确实出去过，发现‘别处也可以成立’，最后还能够回来，"
                   "而且把在别处得到的东西也带回来，这个‘回来’才不再是退回原样」，以及「经历会不会永久改变‘家’的含义」。"
                   "请先读这些研究，再判断这条线在这首曲子里的真实分量。"),
}
MODELS = {"g6": thr.G6, "g56": thr.G56}
TELL = (thr.ROOT / "prompts" / "tell_v1.md").read_text(encoding="utf-8")
AUD = (thr.ROOT / "prompts" / "audit_v1.md").read_text(encoding="utf-8")
keys = []
for cid in CANDS:
    for mk, model in MODELS.items():
        name = f"{cid}-{mk}"

        def tell(cid=cid, name=name, model=model):
            p = TELL.replace("{CAND}", CANDS[cid]()).replace("{BEADS}", common.beads_text())
            return thr.finish_text("tell", name, thr.call("tell", name, p, [T24], model=model))
        thr.task("tell", name, tell, kind="text"); keys.append(("tell", name))

        other = thr.G56 if mk == "g6" else thr.G6

        def audit(name=name, other=other):
            p = AUD.replace("{TELL}", thr.text("tell", name)).replace("{BEADS}", common.beads_text())
            return thr.finish_json("audit", name, thr.call("audit", name, p, model=other))
        thr.task("audit", name, audit, [("tell", name)]); keys.append(("audit", name))

if __name__ == "__main__":
    thr.run(keys)
