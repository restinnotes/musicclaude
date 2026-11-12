"""11-02 scheme P2 (GPT-6's revision after P1, evaluations/v6fix/followup_pb.md): three candidate experiences without beads (A0) →
each written out as a full line without beads (A2 × 3, coverage plan left empty) → only then read the beads: compare the finished
lines, pick one (A1). No rewriting after that. Prompts verbatim in schemes/<PFX>_A*.txt.
usage: PFX=P2 TAG=pd python schemes_p2.py"""
import json, os
from pathlib import Path
import covjudge, evo, pipe, v6fix as V

HERE = Path(__file__).parent
PFX = os.environ.get("PFX", "P2"); TAG = os.environ.get("TAG", "pd"); REF = os.environ.get("REF", "m6w")
S = lambda k: (HERE / "schemes" / f"{PFX}_{k}.txt").read_text(encoding="utf-8")
CTX = "（没有另外提供；可以用你对这首作品的了解，也可以联网查。）"


def call(rid, msg):
    if not evo.done(rid):
        evo.call(rid, msg, model=evo.G6, meta={"stage": f"scheme-{PFX}"})
    out = V.parse(rid)
    if not out:
        raise RuntimeError(f"{rid}: no usable json")
    return out


def piece(w):
    g = V.graph_of(w, REF); C = g["center"]
    seg = "\n".join(f"{s['sec']}：第 {s['bars']} 小节" for s in g["segments"])
    info = f"作曲家：肖邦（Chopin）\n作品：{covjudge.NAME[w]}\nCenter（上游已定，不改）：{C}"
    cand = call(f"sc{TAG}_{w}_A0", S("A0").replace("{WORK_INFO}", info).replace("{SEGMENTS}", seg).replace("{INDEPENDENT_MUSIC_CONTEXT}", CTX))
    cs = cand.get("candidates") or []
    print(w, TAG, "候选", [c.get("id") for c in cs], flush=True)
    done = {}

    def write(c):
        rid = f"sc{TAG}_{w}_A2_{c['id']}"
        done[c["id"]] = call(rid, S("A2").replace("{WORK_INFO}", info).replace("{SEGMENTS}", seg)
                             .replace("{CANDIDATES_JSON}", json.dumps({"candidates": [c]}, ensure_ascii=False, indent=1)).replace("{COVERAGE_PLAN_JSON}", "{}"))
    evo.run_parallel([(c["id"], (lambda c=c: write(c))) for c in cs], 3)
    for k, c in enumerate(cs, 1):
        if c["id"] in done:
            pipe.save(w, g, done[c["id"]], f"方案 {PFX} 候选 {c['id']}：不看珠子写成完整的线", f"{TAG}{k}", REF)
    if not done:
        raise RuntimeError(f"{w}: no candidate written")
    sel = call(f"sc{TAG}_{w}_A1", S("A1").replace("{CANDIDATES_JSON}", json.dumps({"candidates": [{"id": k, **v} for k, v in done.items()]}, ensure_ascii=False, indent=1))
               .replace("{BEADS_JSON}", covjudge.bead_text(w)).replace("{SEGMENTS}", seg))
    pref = sel.get("preferred"); pref = pref[0] if isinstance(pref, list) and pref else pref
    if pref not in done:
        print(w, "A1 没选出可用候选：", str(sel.get("selection_reason"))[:300], "；用第一条", flush=True)
        pref = next(iter(done))
    print(w, TAG, "选中", pref, "理由", str(sel.get("selection_reason"))[:300], flush=True)
    pipe.save(w, g, done[pref], f"方案 {PFX}：三条经历各写成完整的线（不看珠子）→ 读珠子挑一条（选 {pref}）；无后续改写", TAG, REF)


if __name__ == "__main__":
    r = evo.run_parallel([(w, (lambda w=w: piece(w))) for w in ("op60", "op61")], 2)
