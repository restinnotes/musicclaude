"""Cheap objective signals (not quality scores): section count, 117-as-bar, bold aphorisms, insight-ending rate, preamble thesis."""
import re, sys, glob
from statistics import mean
import arts, analyze

INSIGHT = re.compile(r"(明白|知道了|原来|第一次|发现|意识到|终于|才懂|看清)")


def sections(t):
    parts = re.split(r"\n(?=#{1,4} |\*\*第?\s*\d+\s*[—–-])", t)
    return [p for p in parts if re.match(r"(#{1,4} |\*\*)", p) and re.search(r"\d", p.split("\n", 1)[0])]


def m(t):
    secs = sections(t)
    ends = []
    for s in secs:
        paras = [p.strip() for p in s.strip().split("\n") if p.strip() and not p.startswith("#")]
        ends.append(bool(paras) and (bool(INSIGHT.search(paras[-1])) or paras[-1].startswith("**")))
    pre = t.split("\n#", 1)[0] if "\n#" in t else ""
    return {"n_sec": len(secs), "has117": bool(re.search(r"(第\s*117\s*小节|117\s*小节\s*[｜|])", t)),
            "bold": len(re.findall(r"\*\*[^*\n]{6,}\*\*", t)), "insight_end": mean(ends) if ends else 0,
            "chars": len(t), "preamble": len(pre)}


if __name__ == "__main__":
    pool = arts.pool(sys.argv[1:])
    by = {}
    for n, t in pool.items():
        by.setdefault(analyze.cond_of(n), []).append(m(t))
    by["B0"] = [m(arts.b0())]
    print("| cond | n | sections | 117-as-bar | bold lines | insight-ending | chars | preamble chars |")
    print("|---|---|---|---|---|---|---|---|")
    for c, v in by.items():
        print(f"| {c} | {len(v)} | {mean(x['n_sec'] for x in v):.1f} | {sum(x['has117'] for x in v)} | {mean(x['bold'] for x in v):.1f} | {mean(x['insight_end'] for x in v):.2f} | {mean(x['chars'] for x in v):.0f} | {mean(x['preamble'] for x in v):.0f} |")
