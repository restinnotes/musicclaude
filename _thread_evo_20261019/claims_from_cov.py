"""10-30: after several in-order passes the items' bead claims (explains, inherited through src) drift. Re-derive them from the
coverage judges, who name for every bead the line items that explain it ("第2条「…」" = the 2nd item of that segment):
an item explains a bead if either judge cited it for a bead it judged 说清 or 偏弱. Items no judge cited keep no claim; beads
nobody explains show as not explained in the joined product. Rewrites evaluations/v6fix/<w>_<tag>.json in place (backup .bak).
usage: python claims_from_cov.py <tag>"""
import json, re, shutil, sys
import v6fix as V
from v6weave import item_nums


def main(T):
    for w in ("op60", "op61"):
        f = V.OUT / f"{w}_{T}.json"; d = json.loads(f.read_text(encoding="utf-8"))
        shutil.copy(f, f.with_suffix(".json.bak"))
        claim = {}; texts = {s["sec"]: [i["text"] for i in s["items"]] for s in d["graph"]["segments"]}
        for j in V.JUDGES:
            for x in (V.parse(f"cov_{w}_{j}_{T}") or {}).get("beads") or []:
                if x.get("status") not in ("说清", "偏弱"):
                    continue
                for n in item_nums(x.get("items"), x["sec"], texts.get(x["sec"])):
                    claim.setdefault((x["sec"], n), set()).add(str(x["bead"]).split("-")[-1])
        moved = 0
        for s in d["graph"]["segments"]:
            for i, it in enumerate(s["items"], 1):
                new = sorted(claim.get((s["sec"], i), set()))
                moved += new != sorted(it.get("explains") or [])
                it["explains"] = new
        f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        print(w, T, "按覆盖评委重定珠子认领，改动条目", moved, flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
