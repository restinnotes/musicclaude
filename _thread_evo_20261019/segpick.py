"""10-30: per-segment scorecard across measured versions, from measurements already made (no new calls):
coverage (beads not 说清, both judges), pure bead retelling (items, both judges), alone weak segment (勉强/不成立, both judges),
blind "lost vs v6" (both judges), plus form (items, chars, longest item, arrows). Lower is better for every count.
usage: python segpick.py w31,w34 [pick]  -> prints the table; with pick, prints a merge_tags spec choosing per segment
(fewest coverage misses + lost + retell + weak, ties -> fewer chars)."""
import json, sys
import v6fix as V


def card(tag):
    cov = json.loads((V.OUT / f"cov_{tag}.json").read_text(encoding="utf-8"))
    al = json.loads((V.OUT / f"alone_{tag}.json").read_text(encoding="utf-8"))
    bl = json.loads((V.OUT / f"blind_{tag}.json").read_text(encoding="utf-8"))
    out = {}
    for w in ("op60", "op61"):
        g = V.graph_of(w, tag)
        for s in g["segments"]:
            out[(w, s["sec"])] = {"miss": 0, "lost": 0, "retell": 0, "weak": 0, "n": len(s["items"]),
                                  "chars": sum(len(i["text"]) for i in s["items"]), "maxlen": max(len(i["text"]) for i in s["items"]),
                                  "arrows": len(s["because"])}
        for j in ("g6", "g56"):
            for x in cov[f"{w}_{j}"].get("weak") or []:
                if x[2] != "说清" and (w, x[0]) in out:
                    out[(w, x[0])]["miss"] += 1
            a = al[f"{w}_{j}"]
            for r in a.get("retold") or []:
                if r[1] == "复述珠子":
                    out[(w, r[0].split("-")[0])]["retell"] += 1
            for x in a.get("weak_secs") or []:
                out[(w, x[0])]["weak"] += 1
        for v in bl.values():
            if v["w"] == w:
                for sec, _ in v.get("lost_new") or []:
                    if (w, sec) in out:
                        out[(w, sec)]["lost"] += 1
    return out


def main(tags, pick=False):
    C = {t: card(t) for t in tags}
    keys = list(C[tags[0]])
    print("段 | " + " | ".join(f"{t} 漏/丢/复述/弱 条/字/最长/箭头" for t in tags))
    choice = {}
    for k in keys:
        cells, best = [], None
        for t in tags:
            c = C[t][k]
            bad = c["miss"] + c["lost"] + c["retell"] + c["weak"]
            cells.append(f"{c['miss']}/{c['lost']}/{c['retell']}/{c['weak']} {c['n']}/{c['chars']}/{c['maxlen']}/{c['arrows']}")
            key = (bad, c["chars"])
            if best is None or key < best[0]:
                best = (key, t)
        choice[k] = best[1]
        print(f"{k[0]} {k[1]} | " + " | ".join(cells) + f" | 取 {best[1]}")
    for t in tags:
        tot = {f: sum(C[t][k][f] for k in keys) for f in ("miss", "lost", "retell", "weak", "chars", "arrows")}
        print(t, tot)
    if pick:
        spec = {}
        for (w, sec), t in choice.items():
            if t != tags[0]:
                spec.setdefault((t, w), []).append(sec)
        print("merge_tags spec (base", tags[0] + "):", " ".join(f"{t}:{w}:{','.join(s)}" for (t, w), s in spec.items()))


if __name__ == "__main__":
    main(sys.argv[1].split(","), len(sys.argv) > 2)
