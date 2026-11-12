"""10-30: repeated-blind summary (blind_<T>.json + blind_<T>_r2..r4.json): per piece, how many of the 8 reports prefer the new
line, judge it not a regression, mean listed losses, and mean per-segment net wins (new - v6) on cover / lean / plain.
usage: python blind_rep_table.py w24 w37"""
import json, sys
import v6fix as V


def rows(T):
    S = {}
    for suf in ("", "_r2", "_r3", "_r4"):
        f = V.OUT / f"blind_{T}{suf}.json"
        if f.exists():
            S.update({k + suf: v for k, v in json.loads(f.read_text(encoding="utf-8")).items()})
    out = []
    for w, W in (("op60", "Op.60（14 段）"), ("op61", "Op.61（13 段）")):
        xs = [v for v in S.values() if v["w"] == w]
        if not xs:
            continue
        n = len(xs); net = lambda k: sum(v["cnt"][k]["new"] - v["cnt"][k]["base"] for v in xs) / n
        out.append(f"| {T} | {W} | {sum(v['better'] == '新版' for v in xs)}/{n} | {sum(str(v['new_regress']).startswith('否') for v in xs)}/{n} | "
                   f"{sum(len(v['lost_new']) for v in xs) / n:.1f} | {net('cover'):+.1f} | {net('lean'):+.1f} | {net('plain'):+.1f} |")
    return out


if __name__ == "__main__":
    print("| 版本 | 曲 | 选新版 | 判“不算退步” | 每份列出的丢失（平均） | 覆盖净胜 | 啰嗦净胜 | 人话净胜 |\n|---|---|---|---|---|---|---|---|")
    for t in sys.argv[1:]:
        print("\n".join(rows(t)))
