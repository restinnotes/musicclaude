"""Turn labels for pool P27 -> P27t (10-27 evening). In P4a the D21 turns were ~40% of the pool but picked 3 times; they
carried no judge labels ("评审事先认为能解释：无") while whole-segment candidates did. One g56 call per segment labels every
turn group: which beads it explains (says why that bead's feeling comes exactly then), one line of reason each.
Whole-segment groups keep their covjudge labels. ids: tl_<work>_<sec>.  usage: THREAD_ROUTE=gpt3s python tlabel.py"""
import json, shutil
import covjudge, evo, node2b, pool

import sys as _s
SRC, DST = (_s.argv[1], _s.argv[2]) if len(_s.argv) > 2 else ("P27", "P27t")
Q = """下面是肖邦{NAME}一段音乐的听感记录（另一批人听这段写下的原文），以及若干条“段内转折”解释：每条解释这一段里的一处变化——先怎样、后来怎样，以及为什么恰好在这时。

请对每条转折判断它解释了哪几条听感。“解释了”是指：它说清了这条听感里的感受为什么会在此刻出现；只说到同样的结果、只是换了个说法、或者方向相反，都不算。一条转折可以一条都没解释。每条写一句理由。

【听感记录】
{BEADS}

【段内转折】
{TURNS}

只输出 json：
```json
{{"items": [{{"id": "M3", "explains": ["S07-B2"], "why": "……"}}]}}
```"""


def turns(w, sec):
    return [m for m in json.loads((pool.OUT / SRC / w / f"{sec}.json").read_text(encoding="utf-8"))["mechs"] if "#t" in m["rep"]["src"] or "#c" in m["rep"]["src"]]


def main():
    jobs, segs = [], []
    for w in ("op60", "op61"):
        bs = covjudge.beads(w)
        for f in sorted((pool.OUT / SRC / w).glob("S*.json")):
            sec = f.stem; ts = turns(w, sec)
            if not ts:
                continue
            beads = "\n".join(f"- {b['id']}［{b['role']}］{b['text']}" for b in bs if b["sec"] == sec and b["role"] != "演奏条件")
            tt = "\n".join(f"{m['id']}：感受：{m['rep']['feel']} 为什么：{m['rep']['thread']}" for m in ts)
            segs.append((w, sec))
            if not evo.done(f"tl{'' if SRC == 'P27' else SRC}_{w}_{sec}"):
                jobs.append(node2b.job(f"tl{'' if SRC == 'P27' else SRC}_{w}_{sec}", Q.format(NAME=covjudge.NAME[w], BEADS=beads, TURNS=tt), {"stage": "tlabel"}, w="g56"))
    evo.run_parallel(jobs, 27)
    for w in ("op60", "op61"):
        shutil.copytree(pool.OUT / SRC / w, pool.OUT / DST / w, dirs_exist_ok=True)
    for w, sec in segs:
        f = pool.OUT / DST / w / f"{sec}.json"; d = json.loads(f.read_text(encoding="utf-8"))
        try:
            lab = {x["id"]: x for x in evo.parse_json(evo.output(f"tl{'' if SRC == 'P27' else SRC}_{w}_{sec}"))["items"]}
        except Exception:
            print(w, sec, "no labels", flush=True); continue
        n = 0
        for m in d["mechs"]:
            if ("#t" in m["rep"]["src"] or "#c" in m["rep"]["src"]) and m["id"] in lab:
                m["explains"] = sorted(set(lab[m["id"]].get("explains") or [])); m["label_why"] = lab[m["id"]].get("why", ""); n += bool(m["explains"])
        f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        print(w, sec, "turns labeled;", n, "explain at least one bead", flush=True)


if __name__ == "__main__":
    main()
