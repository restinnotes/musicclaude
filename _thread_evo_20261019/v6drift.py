"""10-31 general check (from reading Op.61: 旧梦 narrowed to 亲近 over several rewrites): does a rewritten line keep what each
part of the Center means in the ORIGINAL line? The judge sees the original line (v6), the Center, and the new line (no beads,
no glossary from the writer side — it reads both lines itself). Per segment of the new line: 守住 / 改窄 / 换掉, with a reason.
ids: dr_<w>_<j>_<tag>.  usage: python v6drift.py <tag> -> evaluations/v6fix/drift_<tag>.json/.md
drift_<tag>.json = {w: [{"sec", "label", "why"}]} for segments BOTH judges call 改窄 or 换掉 (used by v6gen.py fix)."""
import json, sys
import covjudge, evo, v6fix as V

P = """下面是肖邦{NAME}的一条“线”（Thread）的两个版本：原来那一版，和改写后的一版。两版的 Center（贯穿全曲的那个问题）相同：{CENTER}

改写只该改写法，不该改 Center 各部分在这条线里指什么。请先读原来那一版，弄清 Center 的每一部分在那里指什么（包括哪几面）；再逐段读改写后的一版，判断：
- 守住：这一段说到 Center 的那部分时，意思和原来一致（可以换说法、可以只说当下相关的一面，但没有让读者以为它就只是那一面）；
- 改窄：把原来一整件事缩成了其中一面，或者用一件更小、更日常的事情顶替了它；
- 换掉：说成了另一件原来没有的事。
不涉及 Center 的段落判“守住”。写一句理由，说出原来指什么、这里变成了什么。最后整体说：改写后的一版，Center 的哪一部分被改得最多。

【原来那一版】
{OLD}

【改写后的一版】（方括号里是条目编号）
{NEW}

只输出 json：
```json
{{"sections": [{{"sec": "S01", "label": "守住", "why": "……"}}], "whole": "……"}}
```"""


def run(T):
    jobs = []
    for w in ("op60", "op61"):
        g = V.graph_of(w, T)
        for j, m in V.JUDGES.items():
            rid = f"dr_{w}_{j}_{T}"
            if not evo.done(rid):
                jobs.append((rid, (lambda rid=rid, m=m, w=w, g=g: evo.call(rid, P.format(NAME=covjudge.NAME[w], CENTER=g["center"], OLD=V.view(V.v6(w), center=False),
                                                                                   NEW=V.view(g, ids=True, center=False)), model=m, meta={"stage": "v6-drift"}))))
    evo.run_parallel(jobs, 4)
    out, md = {}, [f"# Center 的意思有没有被改窄：{T}", ""]
    for w in ("op60", "op61"):
        lab = {}
        for j in V.JUDGES:
            e = V.parse(f"dr_{w}_{j}_{T}") or {}
            S = e.get("sections") or []
            bad = [s for s in S if s.get("label") in ("改窄", "换掉")]
            print(T, w, j, "段", len(S), "改窄/换掉", len(bad), [s.get("sec") for s in bad], flush=True)
            md += [f"## {w} · {'gpt-6' if j == 'g6' else '5.6'}", "", e.get("whole", ""), ""] + [f"- {s.get('sec')}：{s.get('label')}　{s.get('why', '')}" for s in S] + [""]
            for s in bad:
                lab.setdefault(s["sec"], []).append(s)
        out[w] = [{"sec": sec, "label": xs[0]["label"], "why": xs[0].get("why", "")} for sec, xs in lab.items() if len(xs) == len(V.JUDGES)]
    (V.OUT / f"drift_{T}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    (V.OUT / f"drift_{T}.md").write_text("\n".join(md), encoding="utf-8")


if __name__ == "__main__":
    run(sys.argv[1])
