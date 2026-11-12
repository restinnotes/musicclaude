"""10-29: merge segment-disjoint parallel refixes into one version.
usage: python merge_tags.py <out> <base> <tag>:<w>:<S01,S02> [...]   e.g. w13 w10 w11:op60:S02,S06,S09 w11:op61:S03 w12:op60:S03,S04
Segments not named come from <base>; links to ids that no longer exist are dropped (tidy)."""
import json, sys
import v6fix as V


def main(out, base, specs):
    take = {}
    for sp in specs:
        tag, w, secs = sp.split(":")
        for s in secs.split(","):
            take.setdefault(w, {})[s] = tag
    for w in ("op60", "op61"):
        b = json.loads((V.OUT / f"{w}_{base}.json").read_text(encoding="utf-8"))
        cache = {}; segs = []; rows = dict(b["rows"]); src = []
        for s in b["graph"]["segments"]:
            t = take.get(w, {}).get(s["sec"])
            if t:
                if t not in cache:
                    cache[t] = json.loads((V.OUT / f"{w}_{t}.json").read_text(encoding="utf-8"))
                segs.append(next(x for x in cache[t]["graph"]["segments"] if x["sec"] == s["sec"]))
                rows[s["sec"]] = cache[t]["rows"].get(s["sec"], rows.get(s["sec"]))
                src.append(f"{s['sec']}:{t}")
            else:
                segs.append(s); src.append(f"{s['sec']}:{base}")
        g = V.tidy({"center": b["graph"]["center"], "segments": segs})
        json.dump({"graph": g, "rows": rows, "base": " ".join(src)}, open(V.OUT / f"{w}_{out}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        (V.OUT / f"{w}_{out}.md").write_text(f"# {'Op.60' if w == 'op60' else 'Op.61'}｜关系图（在 v6 上修补，{out}）\n\n" + V.view(g), encoding="utf-8")
        print(w, out, " ".join(src), sum(len(x["items"]) for x in g["segments"]), "条", flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
