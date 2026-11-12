"""New mechanism: Center grown from the beads, then a Thread written along that Center.
Step 1: python centers.py find <tag> <n_calls>      -> runs/cf_<tag>_<i>/, evaluations/centers/<tag>.json
Step 2: python centers.py write <tag> [<n_per_center>] -> runs/cw_<tag>_<k>_r<j>/ (P0 + center note + D3 material)
"""
import json, sys
import align, evo, gen

OUT = evo.ROOT / "evaluations" / "centers"


WORKNAME = {"op60": "肖邦《船歌》Op.60", "op61": "肖邦《幻想波兰舞曲》Op.61"}


def find(tag, n, work="op60", ver="v1"):
    btxt, beads = align.beads_text(work)
    tpl = evo.rd(evo.ROOT / "prompts" / f"center_from_beads_{ver}.md")
    msg = tpl.replace("{WORK}", WORKNAME[work]).replace("{BEADS}", btxt)
    evo.run_parallel([(f"cf_{tag}_{i}", (lambda i=i: evo.call(f"cf_{tag}_{i}", msg, prompt_text=tpl, meta={"stage": "center_find"})))
                      for i in range(1, n + 1)], n)
    cands = []
    for i in range(1, n + 1):
        r = evo.output(f"cf_{tag}_{i}")
        if not r:
            continue
        for c in evo.parse_json(r).get("candidates", []):
            ok = [e for e in c.get("evidence", []) if e.get("bead") in beads and align.norm(e.get("quote")) in align.norm(beads[e["bead"]])]
            c["evidence_verified"] = f"{len(ok)}/{len(c.get('evidence', []))}"
            c["segments_covered"] = len({e["bead"].split("/")[0] for e in ok})
            c["from"] = f"cf_{tag}_{i}"
            cands.append(c)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{tag}.json").write_text(json.dumps(cands, ensure_ascii=False, indent=1), encoding="utf-8")
    for k, c in enumerate(cands, 1):
        print(k, c["evidence_verified"], "segs", c["segments_covered"], "|", c["center"])


def block(c):
    ev = "\n".join(f"- {e['bead']}：{e['quote']}" for e in c.get("evidence", []))
    hi = "\n".join(f"- {h['segment']}：{h['change']}" for h in c.get("history", []))
    return ("这一次，Thread 所围绕的那件事（Center）已经从这首曲子各段的体验记录里找出来了：\n\n"
            f"**{c['center']}**\n\n它在体验记录中的依据：\n{ev}\n\n它在各段经历中可能的变化线索（只是线索，不必逐条照写，也可以发现它不成立的地方）：\n{hi}\n\n"
            "请沿着这件事写 Thread：各段的转折尽量落在体验记录写到的真实体验上，让前面的经历成为后面感受的理由；"
            "不要另外编造事件、对白或物件来推动情绪，也不要按顺序把体验记录换个说法重讲。")


def write(tag, n_per):
    cands = json.loads((OUT / f"{tag}.json").read_text(encoding="utf-8"))
    base = gen.render("P0", "op60", "orig")
    mat = gen.material("D3", "op60")
    jobs = []
    for k, c in enumerate(cands, 1):
        for j in range(1, n_per + 1):
            rid = f"cw_{tag}_{k}_r{j}"
            msg = base + "\n\n" + block(c) + mat
            jobs.append((rid, (lambda rid=rid, msg=msg, k=k: evo.call(rid, msg, prompt_text=block(cands[k - 1]),
                                                                     meta={"stage": "center_write", "center": cands[k - 1]["center"]}))))
    evo.run_parallel(jobs, 6)


if __name__ == "__main__":
    if sys.argv[1] == "find":
        find(sys.argv[2], int(sys.argv[3]), sys.argv[4] if len(sys.argv) > 4 else "op60", sys.argv[5] if len(sys.argv) > 5 else "v1")
    else:
        write(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 1)
