"""Judge-strength control (10-27): re-judge some D12 drafts (max writer, max judges on gpt4) with Web High judges, so the
D14 High drop can be split into judge effect vs writer/prompt effect. ids: cvH_<draft>_<judge>."""
import sys, covjudge, evo, node2b
names = sys.argv[1:]
evo.run_parallel([node2b.job(f"cvH_{n}_{j}", covjudge.msg(n), {"stage": "cover-high-control", "draft": n}, w=j)
                  for n in names for j in covjudge.JUDGES if not evo.done(f"cvH_{n}_{j}")], 4)
for n in names:
    old = {j: covjudge.result(n, j) for j in covjudge.JUDGES}
    new = {}
    for j in covjudge.JUDGES:
        try:
            r = evo.parse_json(evo.output(f"cvH_{n}_{j}")); new[j] = {x["id"]: x for x in r.get("beads", [])}
        except Exception:
            new[j] = {}
    bs = [b["id"] for b in covjudge.beads(covjudge.segcheck.work_of(n)) if b["role"] != "演奏条件"]
    for lab in ("解释了", "相反"):
        o = sum(old[j].get(b, {}).get("label") == lab for j in old for b in bs) / 2
        h = sum(new[j].get(b, {}).get("label") == lab for j in new for b in bs) / 2
        print(f"{n} {lab}: max评委 {o:g} -> High评委 {h:g}")
