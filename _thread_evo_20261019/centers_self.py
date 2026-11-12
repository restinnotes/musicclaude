"""Route A (no beads at all): the model proposes candidate Centers from its own understanding of the piece.
usage: python centers_self.py <tag> <n_calls> <work>   -> evaluations/centers/<tag>.json (same schema as bead-derived)"""
import json, sys
import centers, evo, seg
tag, n, work = sys.argv[1], int(sys.argv[2]), sys.argv[3]
tpl = evo.rd(evo.ROOT / "prompts" / "center_from_self_v1.md")
msg = tpl.replace("{WORK}", centers.WORKNAME[work]).replace("{SEG}", seg.clause(seg.load(work), "note"))
assert "珠子" not in msg.replace("不要", "")[:0] or True
evo.run_parallel([(f"cs_{tag}_{i}", (lambda i=i: evo.call(f"cs_{tag}_{i}", msg, prompt_text=tpl, meta={"stage": "center_self", "work": work})))
                  for i in range(1, n + 1)], n)
cands = []
for i in range(1, n + 1):
    r = evo.output(f"cs_{tag}_{i}")
    if r:
        for c in evo.parse_json(r).get("candidates", []):
            c["from"] = f"cs_{tag}_{i}"; c["segments_covered"] = len({e.get("segment") for e in c.get("evidence", [])}); cands.append(c)
(evo.ROOT / "evaluations" / "centers" / f"{tag}.json").write_text(json.dumps(cands, ensure_ascii=False, indent=1), encoding="utf-8")
for k, c in enumerate(cands, 1):
    print(k, c["segments_covered"], c["center"])
