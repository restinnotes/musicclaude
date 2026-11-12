"""10-31: one table for the language-pass versions against the base b0 (Op.60 = f8, Op.61 = g1).
Per piece: chars, language problems per 100 chars (GPT find), coverage 说清/相反 (two judges), alone 段成立, checklist
lost_both, and the repeated blind vs b0 (choose new / not a regression / net wins cover, lean, plain).
usage: python htable.py h3 h4 h5 h7 h9"""
import json, sys
from pathlib import Path
import v6fix as V

O = V.OUT
SRC = {"b0": {"op60": "f8", "op61": "g1"}}


def j(n):
    p = O / n
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def src(t, w):
    return SRC.get(t, {}).get(w, t)


def blind(t, w):
    xs = []
    for suf in ("", "_r2", "_r3", "_r4"):
        d = j(f"blind_{t}_vsb0{suf}.json") or {}
        xs += [v for v in d.values() if v["w"] == w]
    if not xs:
        return "—"
    n = len(xs); net = lambda k: sum(v["cnt"][k]["new"] - v["cnt"][k]["base"] for v in xs) / n
    return (f"{sum(v['better'] == '新版' for v in xs)}/{n} | {sum(str(v['new_regress']).startswith('否') for v in xs)}/{n} | "
            f"{net('cover'):+.1f} | {net('lean'):+.1f} | {net('plain'):+.1f}")


def row(t, w):
    s = src(t, w)
    g = V.graph_of(w, t)
    ch = sum(len(i["text"]) for x in g["segments"] for i in x["items"])
    h = (j(f"human_{s}.json") or {}).get(w)
    c = j(f"cov_{s}.json") or {}
    a = j(f"alone_{s}.json") or {}
    k = (j(f"checklist_{s}.json") or {}).get(w)
    cv = " / ".join(f"{c[f'{w}_{jj}']['total'].get('说清', 0)}（反{c[f'{w}_{jj}']['total'].get('相反', 0)}）" if c.get(f"{w}_{jj}") and sum(c[f"{w}_{jj}"]["total"].values()) else "—" for jj in V.JUDGES)
    al = " / ".join(f"{a[f'{w}_{jj}']['self'].get('成立', 0)}" if a.get(f"{w}_{jj}") else "—" for jj in V.JUDGES)
    return (f"| {t} | {w} | {ch} | {h['per100'] if h and h.get('problems') else '—'} | {cv} | {al} | "
            f"{len(k['lost_both']) if k else '—'} | {blind(t, w) if t != 'b0' else '— | — | — | — | —'} |")


if __name__ == "__main__":
    print("| 版本 | 曲 | 字数 | 语言问题/百字 | 覆盖 说清（相反）两位 | 单独读 段成立 两位 | 清单两位都判丢 | 盲评选新版 | 不算退步 | 覆盖净胜 | 啰嗦净胜 | 人话净胜 |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for t in ["b0"] + sys.argv[1:]:
        for w in ("op60", "op61"):
            try:
                print(row(t, w))
            except Exception as e:
                print(f"| {t} | {w} | 出错 {e!r} |")
