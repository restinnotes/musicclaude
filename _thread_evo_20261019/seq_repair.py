"""P8 (10-28 evening): sequential bead-aware repair. Experiment 3 put the bottleneck in the core line: P7 (every segment
repaired at once on T0's frozen history) keeps falling back on the same standing reasons (在乎 / 时间在走 / 对方心意未知), so
it cannot say why the same uncertainty does different things in different segments; package 3 is a chain where each
segment changes a condition the next one builds on. P7 also wrote bead imagery (旧家园, 那个人) as his experience, and is long.
Here segments are repaired in order; each states what it newly establishes (new), and its why-now must come from an earlier
segment's new change (from). Standing reasons alone are not a cause. Bridge boundary as E2b; bead imagery stays a simile.
Per segment: edit (g6) -> check (g56: bounds, progression, readable) -> one revision with the notes if any check fails.
Pilot: Op.60 S01–S07 (where package 3's chain is and P7 lost most), then a blind core comparison of that stretch
(package 3 / P7 / P8, anonymised, random order; split_judge.CORE). Pass (set before running): both judges rank P8 above P7
on why, and at least one ranks P8 level with or above package 3 -> extend to both pieces.
ids: sq8_/sk8_/sq8r_<work>_<sec>, sj8_<work>_core_<judge>.
usage: THREAD_ROUTE=mimic MG_SLOTS=2 python seq_repair.py <work> <last sec> [judge] -> evaluations/seq8/"""
import json, random, sys
import covjudge, deliver_halfdone as D, draft10, evo, precise as P, split_judge as SJ

OUT = evo.ROOT / "evaluations" / "seq8"
E = """下面是肖邦{NAME}第{A}–{B}小节这一段。请写出这一段的 Thread：他此刻感到什么，以及为什么偏偏此刻会这样。

【Center】{CNOTE}{CENTER}

【前面各段已经确立的变化】（按顺序；每条是那一段让他的处境、需要或认识发生的新变化）
{HIST}

【独立稿主线在这一段原来的解释】（写的时候没看过听感记录；说得对的可以保留）
{CUR}

【这一段的听感记录】（另一批人听这段写下的原文）
{BEADS}

【这一段的候选】（各篇独立稿的原话，已按机制归并；“转折”是段内某一处变化的解释）
{CANDS}

要求：
1. 递进：此刻的感受要从前面某一段新确立的变化推出，在 from 里写出是哪几段。全曲一直成立的背景理由（他在乎、时间在走、对方心意未知之类）不能单独当此刻的原因；
   要用，就说出它此刻因为前面哪一步变了而起了新的作用。第一段没有前面的段，from 留空。
2. new：这一段让他的处境、需要或认识发生了什么新变化，后面的段落可以接着用。要具体（例如“他发现X也能Y”“原来的Z不够了”“他开始想要W”），不重复已经确立的；没有新变化就留空。
3. 可以补一座局部的心理过程（身体先于念头、某个做法反过来改变了感受、刚才的什么让此刻变了）；不许新增前史、往事、身份、外部事件、具体的人物关系或场景。
   听感里的地点、人物、往事画面只能当感受的比喻，不能写成他真实的经历或关系。不把音乐本身的变化当成心理原因。
4. 最多 4 条；feel 一句，不超过 40 字；why 一两句，不超过 90 字。用普通人的话；正文里不写编号、小节号，也不写对修改的说明。
5. 真正解释不了的听感标成缺口，不要硬补。

只输出 json：
```json
{{"items": [{{"feel": "……", "why": "……", "from": ["S02"], "explains": ["B1"], "basis": {{"M": ["M3"], "orig": [1]}}}}],
 "new": ["……"], "gaps": [{{"bead": "B2", "why": "……"}}]}}
```"""
K = """下面是一条 Thread 在某一段的解释，以及它前面各段已经确立的变化。请核对：
1. 每条：ok / 越界（新增了前史、往事、身份、外部事件、具体人物关系或场景；把听感里的意象写成了他的经历；把音乐本身的变化当成心理原因）——越界写出是哪一处。
2. 递进：这一段此刻的原因，是不是接在前面某段新确立的变化上（是），还是只在重复全曲一直成立的背景理由（否）？第一段直接判“是”。一句理由。
3. readable：只读这几条、不看听感记录，能不能读懂（是 / 否，一句理由）。

【前面各段已经确立的变化】
{HIST}

【这一段的解释】
{NEW}

【这一段新确立的变化】
{NEWH}

只输出 json：
```json
{{"items": [{{"i": 1, "label": "ok", "why": "……"}}], "progress": "是", "progress_why": "……", "readable": "是", "readable_why": "……"}}
```"""
# 10-28: Op.61's T0 Center is the axis both judges called off (package 3: 曾珍惜的生活不能原样回到现在). For works in
# SEQ_FREE (env, comma list) the Center is only a reference and is written back from the finished line (THREAD_SPEC §十 4).
import os
FREE = [x for x in os.environ.get("SEQ_FREE", "").split(",") if x]
T = os.environ.get("SEQ_TAG", "8")                 # P9 = SEQ_TAG=9 SEQ_NO_T0=1: no T0 line at all (pool + beads + history only)
NO_T0 = os.environ.get("SEQ_NO_T0") == "1"
if NO_T0:
    FREE = ["op60", "op61"]
# P10 = P9 + SEQ_GRAPH=1 (user 10-28: write the relation graph directly, not convert later; P8 was ~2x package 3's length and
# the judges called its key turns too broad): items become graph steps (text <= 45 chars, follows = led by the previous step,
# from = the earlier segment whose new change causes it); key turns must name the concrete mechanism.
GRAPH = os.environ.get("SEQ_GRAPH") == "1"
if GRAPH:
    _e = E
    E = E.replace("4. 最多 4 条；feel 一句，不超过 40 字；why 一两句，不超过 90 字。用普通人的话；正文里不写编号、小节号，也不写对修改的说明。",
                  "4. 写成关系图的步子：每一步一句话，只说一个念头或一步变化，不超过 45 字；由这一段上一步直接引出的，标 follows: true；"
                  "这一步的原因来自前面某段新确立的变化，就在 from 写出那一段。感受和它的原因可以是相连的两步。\n"
                  "   关键转折要写出具体的机制（例如“一直绷着的事刚放下，身体反而先觉出累”），不用“更珍贵了”“更有分量了”“放下得失”这类概括。\n"
                  "   一段的步数跟这一段真正发生了多少相称，一般 2–6 步。用普通人的话；正文里不写编号、小节号，也不写对修改的说明。")
    E = E.replace('{{"items": [{{"feel": "……", "why": "……", "from": ["S02"], "explains": ["B1"], "basis": {{"M": ["M3"], "orig": [1]}}}}],',
                  '{{"items": [{{"text": "……", "follows": false, "from": ["S02"], "explains": ["B1"], "basis": {{"M": ["M3"], "orig": [1]}}}}],')
    assert E != _e and E.count("关系图的步子") == 1 and '"text": "……", "follows"' in E
# P11 = P10 + SEQ_CAUSE=1. P10 pilot: 5.6 put it last on why ("转折主要靠'越……越……'串起，缺具体前因"); the whole-piece
# judges said P8/P9 turned concrete objects (对方的心意, 两人的以后, 回不来的过去) into general 保证 / 安心 / 留不留得住.
if os.environ.get("SEQ_CAUSE") == "1":
    _e = E
    E = E.replace("   一段的步数跟这一段真正发生了多少相称，一般 2–6 步。",
                  "   每个感受后面，紧接一步写出它的具体前因：是前面哪一段确立的哪一个变化引出的（from 写那一段）；不许用“越……越……”“更……了”顶替前因。\n"
                  "   原因要落在具体的对象上（某个人、他的心意、两人的以后、已经回不来的东西、他自己的力气或身体）；听感或候选里有这样的对象，就说出它，"
                  "不要泛化成“有没有保证”“能不能安心”“留不留得住”“有没有着落”这类笼统说法。\n"
                  "   一段的步数跟这一段真正发生了多少相称，一般 2–6 步。", 1)
    assert E != _e
# P12 (Op.61): P11's object list made Op.61 S05–S08 hang everything on 对方 / 对方是否愿意继续靠近, a person the beads never name
# (the P4e failure again; S07 lost 熟悉感闯入 and repeated one sentence five times). Same rule, only objects already there.
if os.environ.get("SEQ_OBJ2") == "1":
    _e = E
    E = E.replace("原因要落在具体的对象上（某个人、他的心意、两人的以后、已经回不来的东西、他自己的力气或身体）；听感或候选里有这样的对象，就说出它，",
                  "原因要落在具体的对象上，但只用听感和前面已经确立的变化里本来就有的对象，不要为了具体另外给他添出一个人或一段关系；"
                  "同一个原因在一段里只说一次，", 1)
    assert E != _e


def show(x, n=1):
    """one item as the line shows it: P8/P9 feel + why; P10 graph step (→ when led by the previous step)."""
    if "text" in x:
        return f"{'→' if x.get('follows') and n else '•'} {x['text']}"
    return f"• {x.get('feel', '')}\n→ {x.get('why', '')}"


def size(x):
    return len(x.get("text", "")) or len(x.get("feel", "")) + len(x.get("why", ""))
CNOTE = {False: "（独立稿形成的主线，不要改）", True: "（独立稿形成的主线，仅作参考：全曲写完后会按写出来的线重写 Center。这一段以前面确立的变化和本段听感为准，不必迁就它的说法）"}
CW = """下面是肖邦{NAME}一条 Thread 的逐段解释，以及各段新确立的变化。请为它写 Center：
一句话，不超过 50 字，说出这条线从头到尾都在围绕的那件事——他在乎什么、它和他之间是什么关系。不预告结局，不概括各段经过，不加线里没有的东西，用普通人的话。

{LINE}

只输出 json：
```json
{{"center": "……", "why": "一句理由"}}
```"""
REV = """

【上一次被核对者退回】
{NOTES}
请据此重写这一段：只改被指出的问题，其余照旧；格式和要求同上。"""


def write(rid, msg, stage):
    """g6 edit; on MimicGate gpt-6 often returns an empty turn (10-28: S01 3 times, S06 4 times), then gpt-5.6 once."""
    if evo.done(rid):
        return parse(rid)
    import os                                         # SEQ_G56=S06,...: segments where gpt-6 already failed, go straight to 5.6
    for model in ((evo.G56,) if rid.split("_")[-1] in os.environ.get("SEQ_G56", "").split(",") else (evo.G6, evo.G56)):
        if evo.call(rid, msg, model=model, meta={"stage": stage}):
            return parse(rid)
    return None


def parse(rid):
    try:
        return evo.parse_json(evo.output(rid))
    except Exception:
        return None


def items_text(e):
    return "\n".join((f"{i}. {'（由上一步引出）' if x.get('follows') else ''}{x['text']}" if "text" in x
                      else f"{i}. 感受：{x.get('feel', '')} 为什么：{x.get('why', '')}") + f"（接在：{'、'.join(x.get('from') or []) or '无'}）"
                     for i, x in enumerate(e.get("items") or [], 1))


def run(w, last):
    OUT.mkdir(exist_ok=True)
    fin, _ = P.t0(w); bs = covjudge.beads(w); hist = []; rows = {}
    for s in draft10.segs(w):
        sec = s["id"]
        beads = "\n".join(f"- {b['id'].split('-')[-1]}［{b['role']}］{b['text']}" for b in bs if b["sec"] == sec and b["role"] != "演奏条件")
        ms = json.loads((evo.ROOT / "evaluations" / "pool" / P.POOL / w / f"{sec}.json").read_text(encoding="utf-8"))["mechs"]
        cands = "\n".join(f"{m['id']}{'（转折）' if ('#t' in m['rep']['src'] or '#c' in m['rep']['src']) else ''}：感受：{m['rep']['feel']} 为什么：{m['rep']['thread']}" for m in ms)
        cur = "（这次没有底稿：请直接根据前面确立的变化、听感和候选来写）" if NO_T0 else "\n".join(f"{i}. {D.clean(c)}" for i, c in enumerate(P.cur_items(fin, sec), 1))
        H = "\n".join(hist) or "（这是第一段，前面还没有）"
        msg = E.format(NAME=covjudge.NAME[w], A=s["start"], B=s["end"], CNOTE="" if NO_T0 else CNOTE[w in FREE], CENTER="（还没有 Center：全曲写完后按写出的线再写）" if NO_T0 else fin.get("center", ""), HIST=H, CUR=cur, BEADS=beads, CANDS=cands)
        e = write(f"sq{T}_{w}_{sec}", msg, "seq8")
        if not e:
            print(w, sec, "修准没有结果，停", flush=True); return rows
        k = check(w, sec, f"sk{T}", e, H)
        bad = [x for x in (k or {}).get("items") or [] if x.get("label") != "ok"]
        notes = [f"- 第{x.get('i')}条越界：{x.get('why', '')}" for x in bad]
        if (k or {}).get("progress") == "否":
            notes.append(f"- 递进不够：{k.get('progress_why', '')}")
        if (k or {}).get("readable") == "否":
            notes.append(f"- 拿掉听感记录读不懂：{k.get('readable_why', '')}")
        final, revised = e, False
        if notes:
            r = write(f"sq{T}r_{w}_{sec}", msg + REV.format(NOTES="\n".join(notes)), "seq8-rev")
            final, revised = (r or e), bool(r)
        hist += [f"（{sec}）{h}" for h in final.get("new") or []]
        n = sum(size(x) for x in final.get("items") or [])
        rows[sec] = dict(edit=final, check=k, notes=notes, revised=revised)
        print(f"{w} {sec}: 越界 {len(bad)} | 递进 {(k or {}).get('progress')} | 读懂 {(k or {}).get('readable')} | 退改 {revised} | 条数 {len(final.get('items') or [])} | {n} 字 | 新变化 {final.get('new')}", flush=True)
        json.dump(rows, open(OUT / f"P{T}_{w}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        if sec == last:
            break
    return rows


def check(w, sec, tag, e, H):
    rid = f"{tag}_{w}_{sec}"
    if not evo.done(rid):
        evo.call(rid, K.format(HIST=H, NEW=items_text(e), NEWH="\n".join(e.get("new") or []) or "（无）"), model=evo.G56, meta={"stage": "seq8-check"})
    return parse(rid)


def judge(w, last):
    rows = json.loads((OUT / f"P{T}_{w}.json").read_text(encoding="utf-8"))
    segs = [s for s in draft10.segs(w)][: [s["id"] for s in draft10.segs(w)].index(last) + 1]
    keep = lambda body: "\n\n".join("### " + p.lstrip("# ") for p in body.split("\n\n### ") if any(p.lstrip("# ").startswith(s["id"] + " ") for s in segs))
    body = lambda rs: "\n".join(f"### {s['id']} ｜ {s['start']}–{s['end']} 小节\n\n" + "\n".join(show(x, n) for n, x in enumerate(rs[s["id"]]["edit"].get("items") or [])) + "\n" for s in segs)
    fin, _ = P.t0(w)
    if T == "8":
        vs = {k: (c, keep(b)) for k, (c, b) in {"包3": SJ.pkg3(w), "P7": SJ.p7(w)}.items()}
        vs["P8"] = (fin.get("center", ""), body(rows)); extra = ""
    else:   # P9 has no Center until the whole piece is written: compare 包3 / P8 / P9 without any Center
        B = os.environ.get("SEQ_BASE", "8")          # P10 pilot is compared with P9 (same no-T0 path, only the output form differs)
        base = json.loads((OUT / f"P{B}_{w}.json").read_text(encoding="utf-8"))
        vs = {"包3": ("", keep(SJ.pkg3(w)[1])), f"P{B}": ("", body(base)), f"P{T}": ("", body(rows))}
        extra = "三版都不给 Center，center 一项不用比，ranks 里照样给出排名即可。"
    order = {}
    for j in ("g6", "g56"):
        rid = f"sj{T}_{w}_core_{j}"
        ks = list(vs); random.Random(rid).shuffle(ks); order[rid] = dict(zip(SJ.NAMES, ks))
        vt = "\n\n".join(f"========== {n} 版 ==========\n" + (f"Center：{vs[k][0]}\n\n" if vs[k][0] else "") + vs[k][1] for n, k in zip(SJ.NAMES, ks))
        note = f"（这里只给出全曲前 {len(segs)} 段，请只就这几段比较。{extra}）\n\n"
        if not evo.done(rid):
            evo.call(rid, SJ.CORE.format(NAME=covjudge.NAME[w], VERSIONS=note + vt), model=evo.G6 if j == "g6" else evo.G56, meta={"stage": "seq8-judge"})
        r = parse(rid) or {}; o = order[rid]; un = lambda xs: [o.get(x, x) for x in xs or []]
        print(rid, "总排名", un(r.get("overall")), "|", "；".join(f"{k} {un(v)}" for k, v in (r.get("ranks") or {}).items()), flush=True)
        print("  ", r.get("overall_why"), flush=True)
    json.dump(order, open(OUT / f"order{T}_{w}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def recheck(w):
    """10-28: a revised segment was not checked again. Re-check each revised segment against the history before it
    (rebuilt in order, as run() did). ids: sk8r_<work>_<sec>."""
    rows = json.loads((OUT / f"P{T}_{w}.json").read_text(encoding="utf-8")); hist, jobs, H = [], [], {}
    for s in draft10.segs(w):
        r = rows.get(s["id"])
        if not r:
            break
        H[s["id"]] = "\n".join(hist) or "（这是第一段，前面还没有）"
        if r["revised"] and not evo.done(f"sk{T}r_{w}_{s['id']}"):
            m = K.format(HIST=H[s["id"]], NEW=items_text(r["edit"]), NEWH="\n".join(r["edit"].get("new") or []) or "（无）")
            jobs.append((f"sk{T}r_{w}_{s['id']}", (lambda rid=f"sk{T}r_{w}_{s['id']}", m=m: evo.call(rid, m, model=evo.G56, meta={"stage": "seq8-recheck"}))))
        hist += [f"（{s['id']}）{h}" for h in r["edit"].get("new") or []]
    evo.run_parallel(jobs, 2)
    for sec, r in rows.items():
        if r["revised"]:
            k = parse(f"sk{T}r_{w}_{sec}") or {}
            bad = [f"第{x.get('i')}条：{x.get('why', '')[:80]}" for x in k.get("items") or [] if x.get("label") != "ok"]
            r["recheck"] = k
            print(f"{w} {sec} 复核：越界 {len(bad)} | 递进 {k.get('progress')} | 读懂 {k.get('readable')}", *bad, sep="\n  ", flush=True)
    json.dump(rows, open(OUT / f"P{T}_{w}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def center(w, rows):
    """T0's Center for fixed works; for SEQ_FREE works one g56 call writes it back from the finished line."""
    fin, _ = P.t0(w)
    if w not in FREE:
        return fin.get("center", "")
    line = "\n\n".join(f"### {s['id']}\n" + items_text(rows[s["id"]]["edit"]) + "\n新确立的变化：" + "；".join(rows[s["id"]]["edit"].get("new") or []) for s in draft10.segs(w))
    if not evo.done(f"sc{T}_{w}"):
        evo.call(f"sc{T}_{w}", CW.format(NAME=covjudge.NAME[w], LINE=line), model=evo.G56, meta={"stage": "seq8-center"})
    c = (parse(f"sc{T}_{w}") or {}).get("center") or fin.get("center", "")
    print(w, "Center：", c, flush=True)
    return c


def full(w):
    """Whole piece: package 3 regression (finalize3.R, both judges) and experiment 3's split review with 包3 / P7 / P8.
    ids: fn8_<work>_R_<judge>, sj8f_<work>_<core|align>_<judge>."""
    import finalize3
    rows = json.loads((OUT / f"P{T}_{w}.json").read_text(encoding="utf-8")); c = center(w, rows)
    body = "\n".join(f"### {s['id']} ｜ {s['start']}–{s['end']} 小节\n\n" + "\n".join(show(x, n) for n, x in enumerate(rows[s["id"]]["edit"].get("items") or [])) + "\n" for s in draft10.segs(w))
    (OUT / f"P{T}_{w}.txt").write_text(f"{covjudge.NAME[w]}\nCenter：{c}\n\n{body}", encoding="utf-8")
    jobs = [(f"fn{T}_{w}_R_{j}", finalize3.R.format(NAME=covjudge.NAME[w], OLD=finalize3.PKG3[w].read_text(encoding="utf-8-sig"), NEW=f"Center：{c}\n\n{body}"), j) for j in ("g6", "g56")]
    if T == "8":
        vs = {"包3": SJ.pkg3(w), "P7": SJ.p7(w), "P8": (c, body)}
    else:   # later variants are compared with P8 (its finished text, Center included)
        B = os.environ.get("SEQ_BASE", "8")
        t8 = (OUT / f"P{B}_{w}.txt").read_text(encoding="utf-8").split("\n", 2)
        vs = {"包3": SJ.pkg3(w), f"P{B}": (t8[1].replace("Center：", "", 1), t8[2].strip()), f"P{T}": (c, body)}
    beads = "\n".join(f"- {b['id']}［{b['role']}］{b['text']}" for b in covjudge.beads(w) if b["role"] != "演奏条件")
    mechs = "\n".join(f"{i}. {m}" for i, m in enumerate(SJ.mech_check.MECH[w], 1)); order = {}
    for kind in ("core", "align"):
        for j in ("g6", "g56"):
            rid = f"sj{T}f_{w}_{kind}_{j}"; ks = list(vs); random.Random(rid).shuffle(ks); order[rid] = dict(zip(SJ.NAMES, ks))
            vt = "\n\n".join(f"========== {n} 版 ==========\nCenter：{vs[k][0]}\n\n{vs[k][1]}" for n, k in zip(SJ.NAMES, ks))
            jobs.append((rid, (SJ.CORE if kind == "core" else SJ.ALIGN).format(NAME=covjudge.NAME[w], VERSIONS=vt, MECHS=mechs, BEADS=beads), j))
    json.dump(order, open(OUT / f"order{T}_full_{w}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    evo.run_parallel([(rid, (lambda rid=rid, m=m, j=j: evo.call(rid, m, model=evo.G6 if j == "g6" else evo.G56, meta={"stage": "seq8-full"})))
                      for rid, m, j in jobs if not evo.done(rid)], 2)
    for j in ("g6", "g56"):
        print(f"{w} 整首对照包3 {j}：", (parse(f"fn{T}_{w}_R_{j}") or {}).get("verdict"), flush=True)
    for rid, o in order.items():
        r = parse(rid) or {}; un = lambda xs: [o.get(x, x) for x in xs or []]
        line = f"{rid}: 总排名 {un(r.get('overall'))}"
        if "_core_" in rid:
            line += " | " + "；".join(f"{k} {un(v)}" for k, v in (r.get("ranks") or {}).items())
        else:
            line += f" | 主体验说清 { {o.get(k, k): v for k, v in (r.get('b1_clear') or {}).items()} } | 写反 { {o.get(k, k): v for k, v in (r.get('reversed') or {}).items()} }"
            line += " | 机制“有” " + str({o[n]: sum(1 for m in r.get("mechs") or [] if m.get(n) == "有") for n in SJ.NAMES})
        print(line, flush=True)


if __name__ == "__main__":
    w, last = sys.argv[1], sys.argv[2]
    if last == "recheck":
        recheck(w); sys.exit()
    done_ = run(w, last)
    if "judge" in sys.argv[3:] and last in done_:
        judge(w, last)
    if "full" in sys.argv[3:] and last in done_ and last == draft10.segs(w)[-1]["id"]:
        full(w)
