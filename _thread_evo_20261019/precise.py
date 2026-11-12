"""Experiment 2 (10-28, advisor gpt-6): restricted bead-aware precision edits on a frozen independent line. T0 = P4d (pool-only
path, beads unseen when drafting). For 10 key segments the editor (g6) sees T0's history up to the segment, the segment's
current items, the segment's pool candidates and its beads, never package 3. Allowed: switch to a more precise existing
candidate, make a cause the existing text already contains explicit, tie an item to a bead, mark a real gap. Not allowed:
new backstory or events, a new cause found in neither T0's history nor the candidates, a change of the line's centre.
Every item cites its basis (H ids / M ids / original item). A g56 checker flags items that go beyond their basis; two
judges (g6, g56) compare the edited segment with package 3's segment, anonymised in random order.
Pass (set before running): >= 6 of 10 segments with no out-of-basis item and both judges "不差于".
ids: peE2_/pcE2_/pjE2_<work>_<sec>[_<judge>].  usage: THREAD_ROUTE=gpt3s python precise.py -> evaluations/precise/"""
import json, random, re
from pathlib import Path
import covjudge, draft10, evo, node2b

import os
MODE = os.environ.get("PRECISE_MODE", "strict")      # strict = gpt-6 顾问的边界；bridge = gpt-5.6 顾问的边界
TAG = "E2" if MODE == "strict" else "E2b"
OUT = evo.ROOT / "evaluations" / ("precise" if MODE == "strict" else "precise_bridge")
T0, POOL = "P4d", "P27t"
SEGS = {"op60": ["S03", "S04", "S05", "S06"], "op61": ["S02", "S04", "S06", "S07", "S10", "S11"]}
PKG3 = {"op60": Path("C:/Users/zuoyi/Documents/Codex/2026-10-25/n-n/outputs/Op60_船歌_Thread.txt"),
        "op61": Path("C:/Users/zuoyi/Documents/Codex/2026-10-25/n-n/outputs/Op61_幻想波兰舞曲_Thread.txt")}

BRIDGE_E = '4. 真正没有解释、也找不到依据的听感，标成缺口，不要硬补。\n5. 如果某颗重要听感的“此刻为什么”在候选里没有，可以补一座局部的因果桥：它必须接在【已经确立的历史】上（写出 H 编号），说出这一刻具体的心理过程（例如身体先于念头、某个办法反过来改变了感受、刚才的什么让此刻变了），而不是编新的经历。'
BRIDGE_NO = '- 给他新增前史、往事、身份或外部事件；\n- 把音乐本身的变化直接当成心理原因；\n- 改变整条 Thread 的主线（见【Center】）。'
E_STRICT = """下面是一条已经独立写成的 Thread（写的时候没看过任何听感记录）在肖邦{NAME}第{A}–{B}小节这一段的样子，以及这一段的听感记录（另一批人听这段写下的原文）。
请对这一段做“受限修准”：让这一段的解释更准确地说清听感里的感受为什么此刻会这样出现。

允许做的：
1. 换成【这一段的候选】里更准确的一条（写出 M 编号），或者加上一条；
2. 改写已有的解释，把它原本就包含的因果说清楚、说具体（例如把“更在乎了”说成前面具体发生了什么、它怎样造成此刻）；
3. 说明每条解释对应哪颗听感；
4. 真正没有解释、也找不到依据的听感，标成缺口，不要硬补。
不允许做的：
- 给他新增前史、往事、身份或外部事件；
- 加入【已经确立的历史】和【这一段的候选】里都没有的新原因；
- 改变整条 Thread 的主线（见【Center】）。
每条修准后的解释都要写出依据：用到了哪几条已确立的历史（H 编号）、来自哪条候选（M 编号）、或是原来的第几条。一段最多 4 条，用普通人的话。

【Center】{CENTER}

【已经确立的历史】
{HIST}

【这一段现在的解释】
{CUR}

【这一段的听感记录】
{BEADS}

【这一段的候选】（独立稿里的原话，已按机制归并；“转折”是段内某一处变化的解释）
{CANDS}

只输出 json：
```json
{{"items": [{{"feel": "他此刻的感受，一句", "why": "为什么，一两句", "op": "换候选 / 说清已有因果 / 保留", "basis": {{"H": ["H3"], "M": ["M12"], "orig": [1]}}, "explains": ["S03-B1"]}}],
 "gaps": [{{"bead": "S03-B2", "why": "需要的原因在历史和候选里都没有：……"}}]}}
```"""
E = E_STRICT if MODE == "strict" else E_STRICT.replace("4. 真正没有解释、也找不到依据的听感，标成缺口，不要硬补。", BRIDGE_E).replace("""- 给他新增前史、往事、身份或外部事件；
- 加入【已经确立的历史】和【这一段的候选】里都没有的新原因；
- 改变整条 Thread 的主线（见【Center】）。""", BRIDGE_NO)
C_STRICT = """下面是一条 Thread 某一段的“受限修准”。修准只允许：换成已有候选、把已有解释里本来就有的因果说清楚；不允许新增前史或外部事件，不允许加入依据里没有的新原因。
请逐条核对修准后的解释：它说的每一个原因，能不能在它写的依据（已确立的历史、所引候选的原话、原来的解释）里找到？
- ok：都找得到（换了说法、说得更具体都可以）；
- 越界：加了依据里没有的前史、事件或原因——写出加了什么。
每条写一句理由。

【已经确立的历史】
{HIST}

【原来的解释】
{CUR}

【所引候选的原话】
{SRC}

【修准后的解释】
{NEW}

只输出 json：
```json
{{"items": [{{"i": 1, "label": "ok", "why": "……"}}]}}
```"""
C_BRIDGE = """下面是一条 Thread 某一段的“局部修准”。修准允许：换成已有候选、把已有因果说清楚，以及补一座接在已确立历史上的局部因果桥（说出此刻具体的心理过程）；
不允许：新增前史、往事、身份或外部事件，把音乐本身的变化直接当成心理原因，改变整条 Thread 的主线。
请逐条核对修准后的解释：
- ok：没有越过上面的边界（新的局部心理过程是允许的，只要它接在已确立的历史上）；
- 越界：新增了前史/事件、把音乐当原因、或改了主线——写出是哪一处。
另外判断：拿掉听感记录，只读这几条，能不能独立读懂（readable：是 / 否，一句理由）。每条写一句理由。

【已经确立的历史】
{HIST}

【原来的解释】
{CUR}

【所引候选的原话】
{SRC}

【修准后的解释】
{NEW}

只输出 json：
```json
{{"items": [{{"i": 1, "label": "ok", "why": "……"}}], "readable": "是", "readable_why": "……"}}
```"""
C = C_STRICT if MODE == "strict" else C_BRIDGE
J = """下面是肖邦{NAME}第{A}–{B}小节这一段的听感记录，以及两个版本对这一段的解释（顺序随机，不代表先后或好坏）。
请判断哪个版本更说得清“他此刻为什么会这样感受”：具体的因果、此刻的转折、身体先于念头的反应、应对办法反过来改变感受这类机制；不要因为字多或故事完整就判好，也不要因为说得笃定就扣分。
先逐个版本说它解释清楚了什么、漏掉或说空了什么，再给结论：{X} 版是否不差于 {Y} 版。每个判断写一句理由。

【听感记录】
{BEADS}

【{P} 版】
{TP}

【{Q} 版】
{TQ}

只输出 json：
```json
{{"notes": {{"{P}": "……", "{Q}": "……"}}, "verdict": "{X} 版不差于 {Y} 版 / {X} 版有实质退步", "why": "……"}}
```"""


def pkg3_seg(w, sec):
    t = PKG3[w].read_text(encoding="utf-8-sig")
    parts = re.split(r"\n(?=S\d\d ｜)", t)
    return next((p.strip() for p in parts if p.startswith(sec + " ｜")), "")


def t0(w):
    fin = json.loads((evo.ROOT / "evaluations" / "synth" / f"{T0}_{w}" / "final.json").read_text(encoding="utf-8"))
    st = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in (evo.ROOT / "evaluations" / "synth" / f"{T0}_{w}").glob("S[0-9][0-9].json")}
    return fin, st


def hist_before(w, st, sec):
    order = [s["id"] for s in draft10.segs(w)]
    hs = [h for s in order[:order.index(sec)] for h in st.get(s, {}).get("hist") or []]
    return "\n".join(f"{h['id']}：{h['text']}" for h in hs) or "（这是第一段，没有更早的历史）"


def cur_items(fin, sec):
    s = next(x for x in fin["sections"] if x["sec"] == sec)
    return [it.get("text") or f"感受：{it.get('feel', '')} 为什么：{it.get('why', '')}" for it in s["items"]]


def run():
    OUT.mkdir(exist_ok=True)
    jobs, ctx = [], {}
    for w, secs in SEGS.items():
        fin, st = t0(w); bs = covjudge.beads(w)
        for sec in secs:
            s = next(x for x in draft10.segs(w) if x["id"] == sec)
            beads = "\n".join(f"- {b['id']}［{b['role']}］{b['text']}" for b in bs if b["sec"] == sec and b["role"] != "演奏条件")
            ms = json.loads((evo.ROOT / "evaluations" / "pool" / POOL / w / f"{sec}.json").read_text(encoding="utf-8"))["mechs"]
            cands = "\n".join(f"{m['id']}{'（转折）' if ('#t' in m['rep']['src'] or '#c' in m['rep']['src']) else ''}：感受：{m['rep']['feel']} 为什么：{m['rep']['thread']}"
                              for m in ms)
            cur = cur_items(fin, sec); hist = hist_before(w, st, sec)
            ctx[(w, sec)] = dict(s=s, beads=beads, ms={m["id"]: m for m in ms}, cur=cur, hist=hist)
            if not evo.done(f"pe{TAG}_{w}_{sec}"):
                jobs.append(node2b.job(f"pe{TAG}_{w}_{sec}", E.format(NAME=covjudge.NAME[w], A=s["start"], B=s["end"], CENTER=fin.get("center", ""), HIST=hist,
                                                                   CUR="\n".join(f"{i}. {c}" for i, c in enumerate(cur, 1)), BEADS=beads, CANDS=cands),
                                       {"stage": "precise"}, w="g6"))
    evo.run_parallel(jobs, 10)
    jobs = []
    for (w, sec), c in ctx.items():
        try:
            c["new"] = evo.parse_json(evo.output(f"pe{TAG}_{w}_{sec}"))
        except Exception:
            print(w, sec, "edit failed", flush=True); continue
        items = c["new"].get("items") or []
        new = "\n".join(f"{i}. 感受：{x.get('feel', '')} 为什么：{x.get('why', '')}（依据：{json.dumps(x.get('basis'), ensure_ascii=False)}）" for i, x in enumerate(items, 1))
        src = "\n".join(f"{m}：{c['ms'][m]['rep']['thread']}" for x in items for m in (x.get("basis") or {}).get("M") or [] if m in c["ms"]) or "（没有引候选）"
        c["new_text"] = "\n".join(f"• {x.get('feel', '')}\n  → {x.get('why', '')}" for x in items)
        if not evo.done(f"pc{TAG}_{w}_{sec}"):
            jobs.append(node2b.job(f"pc{TAG}_{w}_{sec}", C.format(HIST=c["hist"], CUR="\n".join(f"{i}. {t}" for i, t in enumerate(c["cur"], 1)), SRC=src, NEW=new),
                                   {"stage": "precise-check"}, w="g56"))
        rnd = random.Random(f"{w}{sec}"); first_new = rnd.random() < 0.5
        P, Q = ("甲", "乙"); TP, TQ = (c["new_text"], pkg3_seg(w, sec)) if first_new else (pkg3_seg(w, sec), c["new_text"])
        c["new_is"] = P if first_new else Q; X, Y = c["new_is"], (Q if first_new else P)
        for j in ("g6", "g56"):
            if not evo.done(f"pj{TAG}_{w}_{sec}_{j}"):
                jobs.append(node2b.job(f"pj{TAG}_{w}_{sec}_{j}", J.format(NAME=covjudge.NAME[w], A=c["s"]["start"], B=c["s"]["end"], BEADS=c["beads"],
                                                                       P=P, Q=Q, TP=TP, TQ=TQ, X=X, Y=Y), {"stage": "precise-judge"}, w=j))
    evo.run_parallel(jobs, 30)
    ok = 0
    for (w, sec), c in ctx.items():
        if "new" not in c:
            continue
        try:
            chk = evo.parse_json(evo.output(f"pc{TAG}_{w}_{sec}"))["items"]
            js = {j: evo.parse_json(evo.output(f"pj{TAG}_{w}_{sec}_{j}")) for j in ("g6", "g56")}
        except Exception as e:
            print(w, sec, "check/judge failed", e, flush=True); continue
        over = [x for x in chk if x.get("label") != "ok"]
        notworse = {j: ("不差于" in (r.get("verdict") or "")) for j, r in js.items()}
        passed = not over and all(notworse.values()); ok += passed
        rec = {"work": w, "sec": sec, "original": c["cur"], "edited": c["new"], "check": chk, "judges": js, "edited_label": c["new_is"],
               "out_of_basis": len(over), "not_worse": notworse, "pass": passed, "pkg3": pkg3_seg(w, sec)}
        (OUT / f"{w}_{sec}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{w} {sec}: 越界 {len(over)} 条 | 不差于包3 {notworse} | 过关 {passed} | 缺口 {[g.get('bead') for g in c['new'].get('gaps') or []]}", flush=True)
    print(f"实验 {TAG}：10 段里过关 {ok} 段（过关线 6 段）", flush=True)


if __name__ == "__main__":
    run()
