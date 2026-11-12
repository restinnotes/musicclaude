"""Per-draft 解释了 counts by bead role (主体验 / 段内变化 / 另一侧面 / 另一种理解), both judges averaged (10-27: does a
draft family explain the within-segment changes better?). usage: python by_role.py <work> <draft-glob> ..."""
import fnmatch, sys
import covjudge, draft10

w = sys.argv[1]; pats = sys.argv[2:]
bs = [b for b in covjudge.beads(w) if b["role"] != "演奏条件"]
roles = sorted({b["role"] for b in bs})
print(f"{'draft':18}" + "".join(f"{r}({sum(b['role'] == r for b in bs)})".rjust(12) for r in roles) + "   相反")
for p in sorted(draft10.OUT.glob(f"d1*_{w}_*.json")):
    n = p.stem
    if not any(fnmatch.fnmatch(n, x) for x in pats):
        continue
    rs = [covjudge.result(n, j) for j in covjudge.JUDGES]
    if not all(rs):
        continue
    row = [sum(r.get(b["id"], {}).get("label") == "解释了" for r in rs for b in bs if b["role"] == ro) / 2 for ro in roles]
    opp = sum(r.get(b["id"], {}).get("label") == "相反" for r in rs for b in bs) / 2
    print(f"{n:18}" + "".join(f"{x:g}".rjust(12) for x in row) + f"   {opp:g}")
