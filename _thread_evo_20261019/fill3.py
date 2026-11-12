"""Gap fill after the pool-only path (PLAN_20261026.md step 5, 10-27): only for beads the path left 没有解释 / 池子太窄,
counted separately and marked 补 in the product. Per segment with gaps:
W (g6): up to 2 explanations from the path's own History before this segment (sees the beads, as synthesis does), plain
   speech, no invented events or backstory; an honest "找不到" is a result;
K (g56): each candidate passes only if its premise is really in that History, it gives a real cause (not 更在乎 / 可以 /
   music-return), and it does not contradict the segment's chosen items.
ids: fl<T>_<work>_<sec>_{W|K}.  usage: THREAD_ROUTE=mimic python fill3.py <T> <work>  -> evaluations/synth/<T>_<work>/fill_<sec>.json"""
import json, sys
import covjudge, draft10, evo, node2b
import finalize3

W = """你在为肖邦{NAME}逐段建立的一条 Thread 补缺。这一段是第{A}–{B}小节。

【这条 Thread 在这一段之前已经确立的经历】
{HIST}

【这一段已经选定的解释】
{CHOSEN}

【这一段还没有被解释的听感】（另一批人听这段写下的原文）
{BEADS}

请只根据上面已经确立的经历，为这些听感写最多 2 条解释：经历过前面那些的人，为什么此刻会这样感受。
- 不能加入前面没有的经历、人物设定或外部事件；不要给每条听感各安排一个心理步骤，一个理由能解释几条就合在一起；
- “更在乎了 / 更有分量了 / 经历过所以不一样了”“可以这样 / 不等于那样”、把音乐回来当成对方回应，都不算原因；
- 不要复述听感里的声音、比喻和意象；写成一个人在讲自己的事那样的大白话：feel 一句，why 一两句；
- 不能和这一段已经选定的解释矛盾；
- 找不到足够有说服力的解释，就直说找不到，写清缺的是什么。

只输出 json：
```json
{{"cands": [{{"feel": "……", "why": "……", "depends": ["H3"], "explains": ["S07-B1"]}}], "none": "找不到时写缺什么，否则空字符串"}}
```"""
K = """下面是给一条 Thread 第{A}–{B}小节补写的解释。请逐条判断能不能用：
1. 它依赖的经历是否真的在下面的历史里（不能借用历史里没有的事）；
2. 是不是真正的原因（不是“更在乎了 / 有了分量 / 经历过所以不一样”，不是“可以这样 / 不等于那样”，不把音乐回来当成对方回应）；
3. 有没有编人物设定、前史或外部事件；
4. 是否和这一段已经选定的解释矛盾；
5. 它是否真的解释了它声称解释的听感。

【历史】
{HIST}

【这一段已经选定的解释】
{CHOSEN}

【听感】
{BEADS}

【补写候选】
{CANDS}

只输出 json：
```json
{{"verdicts": [{{"i": 1, "ok": true, "why": "一句"}}]}}
```"""


def call(rid, msg, mdl):
    for r in (rid, rid + "_x"):
        if not evo.done(r):
            node2b.job(r, msg, {"stage": "fill3"}, w=mdl)[1]()
        try:
            return evo.parse_json(evo.output(r))
        except Exception:
            continue
    return {}


def one(T, w, sec, st):
    segs = draft10.segs(w); k = next(i for i, x in enumerate(segs) if x["id"] == sec); x = segs[k]
    hist = [h for y in segs[:k] for h in (st.get(y["id"]) or {}).get("hist", [])]
    htxt = "\n".join(f"{h['id']}（{h['sec']}）{h['text']}" for h in hist) or "（没有）"
    chosen = "\n".join(c["text"] for c in (st.get(sec) or {}).get("chosen") or []) or "（没有）"
    cov = finalize3.coverage(w, {sec: st.get(sec) or {}})
    gaps = [r["id"] for r in cov["gap"] if r["id"].startswith(sec + "-")]
    if not gaps:
        return None
    beads = "\n".join(f"- {b['id']}［{b['role']}］{b['text']}" for b in covjudge.beads(w) if b["id"] in gaps)
    d = dict(NAME=covjudge.NAME[w], A=x["start"], B=x["end"], HIST=htxt, CHOSEN=chosen, BEADS=beads)
    tag = "_".join(g.split("-")[1] for g in gaps)       # a different gap set never reuses another set's answer
    r = call(f"fl{T}_{w}_{sec}_{tag}_W", W.format(**d), "g6")
    cands = [c for c in r.get("cands") or [] if c.get("feel")]
    ok = []
    if cands:
        v = call(f"fl{T}_{w}_{sec}_{tag}_K", K.format(**d, CANDS="\n".join(f"{i}. 感受：{c['feel']} 为什么：{c['why']}（依赖：{', '.join(c.get('depends') or []) or '无'}；解释：{', '.join(c.get('explains') or [])}）"
                                                             for i, c in enumerate(cands, 1))), "g56")
        good = {int(t["i"]) for t in v.get("verdicts") or [] if t.get("ok")}
        ok = [c | {"verdict": next((t.get("why") for t in v.get("verdicts") or [] if int(t["i"]) == i), "")}
              for i, c in enumerate(cands, 1) if i in good]
    out = {"sec": sec, "gaps": gaps, "cands": cands, "accepted": ok, "none": r.get("none", "")}
    (evo.ROOT / "evaluations" / "synth" / f"{T}_{w}" / f"fill_{sec}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(w, sec, "gaps", gaps, "-> accepted", len(ok), "/", len(cands), flush=True)
    return out


if __name__ == "__main__":
    T, w = sys.argv[1], sys.argv[2]
    _, st = finalize3.load(T, w, fill=False)        # gaps of the path itself, not of an earlier fill
    evo.run_parallel([(s, lambda s=s: one(T, w, s, st)) for s in st], 5)
