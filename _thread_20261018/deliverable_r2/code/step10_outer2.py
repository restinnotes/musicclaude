"""Round 2 Outer: only for the moments of the chosen final (keys/g6). Per moment: GPT-6 x2, GPT-5.6 x1, Gemini x2 lanes,
4 candidates each -> GPT-6 picks at most two (may pick none) and says whether the Inner itself is the problem."""
import json, random, re
import thr

SRC = thr.text("keys", "g6")


def moments():
    part = SRC.split("## 时刻")[1].split("## 曲终")[0]
    out = []
    for blk in re.split(r"\n### ", "\n" + part.strip())[1:]:
        title, rest = blk.split("\n", 1)
        out.append((title.strip(), rest.strip()))
    return out


MOM = moments()
TPL = (thr.ROOT / "prompts" / "outer2_v1.md").read_text(encoding="utf-8")
PICK = (thr.ROOT / "prompts" / "outer2_pick_v1.md").read_text(encoding="utf-8")
LANES = [("g6", 1), ("g6", 2), ("g56", 1), ("gem", 1), ("gem", 2)]
keys = []
for i, (title, text) in enumerate(MOM, 1):
    mid = f"K{i}"
    mtext = f"### {title}\n\n{text}"
    lane_keys = []
    for mk, j in LANES:
        name = f"{mid}-{mk}-{j}"

        def gen(name=name, mk=mk, mtext=mtext):
            p = TPL.replace("{MOMENT}", mtext)
            r = thr.call_gemini("outer2", name, p) if mk == "gem" else thr.call("outer2", name, p, model=thr.G6 if mk == "g6" else thr.G56)
            return thr.finish_json("outer2", name, r)
        thr.task("outer2", name, gen); keys.append(("outer2", name)); lane_keys.append(("outer2", name))

    def pick(mid=mid, mtext=mtext):
        allc = []
        for mk, j in LANES:
            d = thr.load("outer2", f"{mid}-{mk}-{j}") or {}
            allc += [dict(c, _model=mk) for c in d.get("candidates", []) if c.get("text")]
        random.Random(f"o2-{mid}").shuffle(allc)
        lab = {f"C{n+1:02d}": c for n, c in enumerate(allc)}
        (thr.RUNS / "outer2" / f"{mid}.pool.json").write_text(json.dumps(lab, ensure_ascii=False, indent=1), encoding="utf-8")
        p = PICK.replace("{MOMENT}", mtext).replace("{CANDS}", "\n".join(f"- {k}：{c['text']}" for k, c in lab.items()))
        return thr.finish_json("outer2_pick", mid, thr.call("outer2_pick", mid, p))
    thr.task("outer2_pick", mid, pick, lane_keys); keys.append(("outer2_pick", mid))

if __name__ == "__main__":
    import sys
    if "dry" in sys.argv:
        for t, x in MOM: print(t, len(x))
    else:
        thr.run(keys)
