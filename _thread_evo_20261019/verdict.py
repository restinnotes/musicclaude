"""11-02 迭代准则 第五节的判定线，脚本化。 usage: python verdict.py <tag> [base=m6w]
底线：覆盖任何一段两位评委都掉 2 分以上，或单独读少成立一段（两位评委都少），就不过。
快筛：盲比 4 份至少 3 份选新版；单独成立、啰嗦、人话净胜都不为负。
验收：盲比 8 份至少 6 份选新版，净胜同上，至少 6 份判不算退步。
净胜 = “新版赢段数 − 旧版赢段数”的平均。只读已有结果，不调用模型。"""
import json, os, sys
os.environ.setdefault("JV", "2")
import v6fix as V

WORKS = ("op60", "op61")
J2 = ("g6", "g56")


def bead_keys(w):
    import covjudge
    return {(b["sec"], b["id"].split("-")[-1]) for b in covjudge.beads(w) if b["role"] != "演奏条件"}


def cov_secs(w, j, tag):
    d = V.parse(f"cov2_{w}_{j}_{tag}") or {}
    beads = d.get("beads") or []
    keys = [(x.get("sec"), str(x.get("bead"))) for x in beads]
    if (len(keys) != len(bead_keys(w)) or set(keys) != bead_keys(w)
            or any(x.get("status") not in ("说清", "偏弱", "相反", "没有") for x in beads)):
        return None
    out = {}
    for x in beads:
        s = x.get("sec")
        out[s] = out.get(s, 0) + (1 if x.get("status") == "说清" else 0)
    return out


def alone_count(w, j, tag):
    expected = {s["sec"] for s in V.graph_of(w, tag)["segments"]}
    sections = (V.parse(f"al2_{w}_{j}_{tag}") or {}).get("sections") or []
    keys = [s.get("sec") for s in sections]
    if (len(keys) != len(expected) or set(keys) != expected
            or any(s.get("self") not in ("成立", "勉强", "不成立") for s in sections)):
        return None
    return sum(s.get("self") == "成立" for s in sections)


def floor(tag, base):
    bad = []
    for w in WORKS:
        a, b = {j: cov_secs(w, j, tag) for j in J2}, {j: cov_secs(w, j, base) for j in J2}
        if any(x is None for x in (*a.values(), *b.values())):
            bad.append(f"{w} 覆盖没测全")
            continue
        for s in b["g6"]:
            drops = [b[j].get(s, 0) - a[j].get(s, 0) for j in J2]
            if all(d >= 2 for d in drops):
                bad.append(f"{w} {s} 覆盖两位评委都掉 2 分以上（{drops[0]}、{drops[1]}）")
    for w in WORKS:
        ds = []
        for j in J2:
            na, nb = alone_count(w, j, tag), alone_count(w, j, base)
            if isinstance(na, int) and isinstance(nb, int):
                ds.append(nb - na)
            else:
                bad.append(f"{w} {j} 单独读没测全")
        if len(ds) == 2 and all(d >= 1 for d in ds):
            bad.append(f"{w} 单独读两位评委都少成立（{ds[0]}、{ds[1]}）段")
    return bad


def rows(tag, base):
    out = {}
    for suf in ("", "_r2"):
        p = V.OUT / f"blind2_{tag}_vs{base}{suf}.json"
        if p.exists():
            out.update(json.loads(p.read_text(encoding="utf-8")))
    return list(out.values())


def main(tag, base="m6w"):
    print(f"== {tag} 对 {base}")
    fl = floor(tag, base)
    print("底线：", "过" if not fl else "不过 " + "；".join(fl))
    rs = rows(tag, base)
    if not rs:
        print("盲比：没有结果"); return
    n = len(rs); pick = sum(1 for r in rs if r.get("better") == "新版"); noreg = sum(1 for r in rs if r.get("new_regress") == "否")
    from collections import Counter
    pairs = Counter((r.get("w"), r.get("j")) for r in rs)
    expected = {(w, j) for w in WORKS for j in J2}
    incomplete = (n not in (4, 8) or set(pairs) != expected or any(v != n // 4 for v in pairs.values()))
    for r in rs:
        if (r.get("better") not in ("新版", base, "差不多") or r.get("new_regress") not in ("是", "否")
                or any(sum((r.get("cnt", {}).get(k) or {}).values()) != len(V.graph_of(r["w"], tag)["segments"])
                       for k in ("alone", "lean", "plain", "cover"))):
            incomplete = True
    if incomplete:
        print(f"测量未完成或不完整：盲比 {n} 份，需双曲双评委各一份（快筛4份）或各两份（验收8份）；不判通过")
        return
    nets = {k: sum(r["cnt"][k]["new"] - r["cnt"][k]["base"] for r in rs) / n for k in ("alone", "lean", "plain", "cover")}
    print(f"盲比 {pick}/{n} 选新版；不算退步 {noreg}/{n}；净胜 单独{nets['alone']:+.2f} 啰嗦{nets['lean']:+.2f} 人话{nets['plain']:+.2f} 覆盖{nets['cover']:+.2f}")
    ok_net = all(nets[k] >= 0 for k in ("alone", "lean", "plain"))
    if n == 8:
        print("验收：", "过" if (not fl and pick >= 6 and noreg >= 6 and ok_net) else "不过")
    else:
        print("快筛：", "过" if (not fl and pick >= 3 and ok_net) else "不过", "（底线也算在内）")


if __name__ == "__main__":
    main(*sys.argv[1:3])
