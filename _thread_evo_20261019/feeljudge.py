"""How far does the drafter's own "this moment" sit from the beads? (user 10-23: "评定一下这个感受和珠子")
d9L / d9LC drafts write each segment's feeling as a "感受：" line (the listen variant asks for it); for N8 and d9S the
judge infers the feeling the text sets for each segment. Each segment: 一致 / 部分 / 不一致 against the beads.
ids: fj_<draft>_<judge>.  usage: python feeljudge.py  -> evaluations/feeljudge/summary.json"""
import json, re
import evo, node2b, seq, draftjudge, segcheck

DRAFTS = [f"{f}_op60_r{j}" for f in ("d9L", "d9LC", "n8", "d9S") for j in (1, 2, 3)]
OUT = evo.ROOT / "evaluations" / "feeljudge"
EXPL = "这篇稿子每段先写了一行“感受：”，是作者对这一段音乐感受的设想；请以这一行为准。"
INFER = "这篇稿子没有单独写出感受；请从每段的文字里推断作者设想的这一段他此刻是什么感受（一句话），再比较。"


def msg(n):
    segs = segcheck.seg.load("op60")["segments"]
    t = evo.rd(evo.ROOT / "prompts" / "judge_feel_v1.md").replace("{MODE}", EXPL if n.startswith("d9L") else INFER)
    body = "\n\n".join(f"**第{i + 1}段（{s['start']}–{s['end']}）**\n{x}" for i, (s, x) in enumerate(zip(segs, draftjudge.sections(n))))
    return t + "\n\n# 听感记录\n\n" + draftjudge.beads_all() + "\n\n# 稿子\n\n" + body


if __name__ == "__main__":
    evo.run_parallel([node2b.job(f"fj_{n}_{jn}", msg(n), {"stage": "feeljudge"}, w=jn) for n in DRAFTS for jn in ("g6", "g56")
                      if not evo.done(f"fj_{n}_{jn}")], 8)
    OUT.mkdir(parents=True, exist_ok=True); res = {}
    for n in DRAFTS:
        for jn in ("g6", "g56"):
            r = seq.parse(evo.output(f"fj_{n}_{jn}"))
            if r:
                res[f"{n}|{jn}"] = r
    (OUT / "summary.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    for k, r in res.items():
        ms = [s.get("match") for s in r.get("segments", [])]
        print(k, {m: ms.count(m) for m in ("一致", "部分", "不一致")}, flush=True)
