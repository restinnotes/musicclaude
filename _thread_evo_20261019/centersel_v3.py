"""Content acceptance for Center v3 round 3: same specificity + fit tests as centersel, with the previous best
sentence-form Centers as comparison. Separate run ids (prefix v3) and output dir evaluations/centersel_v3."""
import json, sys
import centersel, evo

centersel.OUT = evo.ROOT / "evaluations" / "centersel_v3"
OLD = {"op60": ("OLD", "他想安心享受眼前的幸福，却总想到它终会过去。"), "op61": ("OLD", "他想挺直腰杆走出去，却总被旧梦拉回，分不清哪边才是自己。")}

if __name__ == "__main__":
    ph = sys.argv[1]
    if ph == "pool":
        centersel.OUT.mkdir(parents=True, exist_ok=True)
        for w in ("op60", "op61"):
            j = json.loads((evo.ROOT / "evaluations" / "centers" / f"v3_r3_{w}.json").read_text(encoding="utf-8"))
            p = [{"id": f"V{k}", "center": c["center"], "src": "v3"} for k, c in enumerate(j["centers"], 1)] + [{"id": OLD[w][0], "center": OLD[w][1], "src": "上一轮最好"}]
            (centersel.OUT / f"pool_{w}.json").write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8")
            print(w, [(c["id"], c["center"]) for c in p])
        sys.exit()
    orig = evo.call
    def call(rid, *a, **k):   # keep run ids distinct from the earlier centersel runs
        return orig("v3" + rid, *a, **k)
    evo.call = call
    orig_out = evo.output
    evo.output = lambda rid: orig_out("v3" + rid) if rid.startswith(("csp_", "cfit_")) else orig_out(rid)
    sys.argv = [sys.argv[0], ph]
    exec(open("centersel.py", encoding="utf-8").read().split('if __name__ == "__main__":')[1].replace("\n    ", "\n"), {**vars(centersel), "sys": sys})
