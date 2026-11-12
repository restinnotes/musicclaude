"""Bead-later mechanism: the model first finds its own spine without beads (a D0 draft from the same prompt version),
then a fresh session gets prompt + its own draft + bead material and writes a complete new article.
usage: python late.py <PROMPT_VERSION> <work> <seg_style> <D3|D4|...> <draft_run_id,...>
run id: l_<version>_<work>_<style>_<cond>_from-<draft_run_id>
"""
import sys
import arts, evo, gen

DATA_NAMES = {"D1": "D1", "D2": "D2", "D3": "D3", "D4": "D4"}


def message(version, work, style, cond, draft_id):
    draft = arts.clean(evo.output(draft_id))
    if cond == "D0":   # control: same redraft step, no bead material
        tail = evo.rd(evo.ROOT / "prompts" / "late_self_v1.md").replace("{DRAFT}", draft.strip())
    else:
        mat = gen.material(cond, work).replace(gen.WRAP, "").strip()
        tail = evo.rd(evo.ROOT / "prompts" / "late_bead_v1.md").replace("{DRAFT}", draft.strip()).replace("{MATERIAL}", mat)
    return gen.render(version, work, style) + "\n\n---\n" + tail


if __name__ == "__main__":
    v, work, style, cond, drafts = sys.argv[1:6]
    jobs = []
    for did in drafts.split(","):
        rid = f"l_{v}_{work}_{style}_{cond}_from-{did}"
        if evo.done(rid):
            continue
        msg = message(v, work, style, cond, did)
        meta = {"stage": "generate_late_bead", "prompt_version": v, "work": work, "seg_style": style, "condition": "L" + cond[1:], "draft": did}
        jobs.append((rid, lambda rid=rid, msg=msg, meta=meta: evo.call(rid, msg, prompt_text=evo.rd(evo.ROOT / "prompts" / ("late_self_v1.md" if cond == "D0" else "late_bead_v1.md")), meta=meta)))
    print(f"{len(jobs)} jobs", flush=True)
    evo.run_parallel(jobs, 6)
