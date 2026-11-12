"""Segment-by-segment synthesis over the explanation pool (PLAN_解释池_20261023.md 六-2/2.5). Per segment:
  A pick   (model a): judge every pool mechanism (beads explained / premise found in History or 缺 / invented setting /
           would fit any segment / result-only), choose what this segment uses (merge same reasons, keep compatible ones
           side by side, one of mutually exclusive ones), give every bead a fate, add new History with the beads it explains.
  B check  (model b): absolute pass/fail; a failed pick goes back to A once with B's problems; unexplained beads are typed
           池子太窄 / 缺前提 / 听感存疑.
  D fill   (model a, sees the beads): for 池子太窄 only, up to 2 local candidates from the existing History, marked 新增,
           or an honest "找不到"; then A/B once more.
  C back   (model b): for 缺前提 and conditional candidates, look back along the History (no fixed distance) for an earlier
           segment whose pool can supply the premise and still explain that segment; accepted only if that segment and
           every later one re-pass B. At most BACK_MAX per run.
  G global (model b) at checkpoints: valuable relations so far / later segments really use them / still one ongoing thing.
ids: sy<T>_<work>_<sec>_{A|B|D|A2|B2|...}.  usage: python synth.py <T> <work> <a:g6|g56> <pool-tag> [last-sec]
state -> evaluations/synth/<T>_<work>/<sec>.json and run.json"""
import json, sys
import covjudge, draft10, evo, node2b

OUT = evo.ROOT / "evaluations" / "synth"
POOL = evo.ROOT / "evaluations" / "pool"
CHECK = {"op60": ("S05", "S08", "S11", "S14"), "op61": ("S03", "S07", "S11", "S13")}
BACK_MAX = 3
INTRO = ("你在为{NAME}逐段建立一条 Thread：把整首音乐理解成一件持续发生在一个人身上的事；前面真实经历过的东西，"
         "让后面的感受有特定的意义，后面的经历也会让前面显出新的意思。现在处理第{K}段（第{A}–{B}小节）。\n\n")
PICK = """任务：
1. 逐条看候选，写清：它解释了这一段哪几条听感；它需要的前提在已确立的历史里有没有（写出 H 编号，没有就写“缺：缺什么”）；它有没有加入听感撑不住的人物设定（身份、前史、外部事件）；它的理由放到别的段落是否也成立；它是在讲原因，还是只说了结果（例如“更投入了”“更强烈了”）。
2. 选出这一段用哪几条。理由相同的合并成一条；解释不同侧面、又能同时成立的可以并存；互相排斥的只取一条。一段只需要一个理由时就只写一个，不要为了照顾每条听感而多加心理步骤。可以用候选的原话，也可以把几条合起来写，但不能加入候选里没有的新理由。用普通人一遍能懂的话，不要用抽象名词代替具体的在乎，不要复述听感里的声音、比喻和意象。
3. 每条听感判一个去处：被选中的第几条解释了它；或者与选中的解释相容、作为感受独立保留（说明为什么不需要另立理由）；或者是另一种听法，与本段的理解互斥；或者现在没有解释。如果这一段最重要的感受只能“独立保留”或“没有解释”，就直说。
4. 写出这一段新确立的历史（以后可能用到的经历或认识），每条注明它解释了哪些听感。
5. 如果有好的候选只是因为前提“缺”而用不上，单独列出来，写清缺的是什么。

只输出一个 json 代码块：
```json
{"eval": [{"id": "M1", "explains": ["S03-B2"], "premise": "H2 或 缺：……", "invented": "", "any_segment": false, "result_only": false, "note": "一句"}],
 "chosen": [{"text": "这一段的一条解释，一两句", "from": ["M1"], "depends": ["H2"], "explains": ["S03-B2"]}],
 "fate": {"S03-B1": "第1条", "S03-B2": "独立保留：为什么", "S03-B3": "另一种听法", "S03-B4": "没有解释"},
 "new_history": [{"text": "……", "explains": ["S03-B2"]}],
 "conditional": [{"id": "M5", "missing": "……"}]}
```"""
CHECKQ = """下面是这条 Thread 在第{K}段的选择结果。请先给绝对判断：这一段合格吗？不要因为它是几个候选里最好的就判合格。

检查：
1. 每条听感的去处是否合理：“独立保留”是不是借口？这一段最重要的感受有没有被解释？（听感前面的归类不代表重要性，请自己判断哪个最重要。）
2. 选中的解释依赖的历史是否真的成立：历史条目如果当初没有解释过任何听感、只是一个设定，依赖它就等于编造。
3. 有没有加入听感撑不住的人物设定、前史或外部事件。
4. 是在讲原因，还是只说了结果；这个理由是否放到哪一段都成立。
5. 有没有为了照顾每条听感而多加心理步骤；有没有复述听感里的声音、比喻和意象；是不是普通人一遍能懂。

对没有解释的听感，判断原因：池子太窄（历史已经足够，只是候选里没人写到）/ 缺前提（需要前面某段换一种理解）/ 听感存疑（这条听感本身的情绪判断或主次值得怀疑）。

【选择结果】
{PICKED}

只输出一个 json 代码块：
```json
{{"pass": true, "problems": ["……"], "unexplained": [{{"id": "S03-B2", "why": "池子太窄", "note": "……"}}], "reason": "一两句"}}
```"""
FILL = """下面这些听感，在现有的候选解释里都找不到能解释它们的：
{BEADS}

请只根据上面已经确立的历史，为这些听感写最多 2 条解释：经历过前面那些的人，为什么此刻会这样感受。
不能加入历史里没有的经历、人物设定或外部事件；不要给每条听感各安排一个心理步骤，一个理由能解释几条就合在一起；不要复述听感里的声音、比喻和意象；用普通人能懂的话。
如果在现有历史下找不到足够有说服力的解释，就直说找不到，并写清缺的是什么——这本身是有用的结果，不要硬凑。

只输出一个 json 代码块：
```json
{{"cands": [{{"text": "……", "premise": "H 编号或 无", "explains": ["S06-B1"]}}], "none": "找不到时写缺什么；找到了就写空字符串"}}
```"""
BACK = """这条 Thread 在第{K}段有一条好的解释用不上，因为它需要的前提在已确立的历史里没有：
解释：{TEXT}
缺的前提：{MISSING}

下面是前面各段当时的候选解释（以及当时选中的）。请找：有没有某一段，可以改用（或加上）其中一条候选，从而提供这个前提——而且那一段改了以后，仍然能解释它自己的听感，不靠编造设定。离得远也可以。没有就直说没有，不要硬找。

{EARLIER}

只输出一个 json 代码块：
```json
{{"sec": "S04 或 空字符串", "mech": "M3", "why": "一两句：它怎样提供前提、为什么那一段仍成立"}}
```"""
GLOBAL = """下面是一条逐段建立到第{K}段的 Thread（每段选中的解释，以及确立的历史）。不要预设它应该讲什么主题，只回答三件事：
1. 到目前为止，形成了哪些真正有价值的历史关系（前面的经历怎样改变了后面的意义）？
2. 后面的理解有没有真的利用、发展或改变这些历史，而不只是引用前面的情绪？
3. 这些局部解释是否仍属于同一件持续发展的事，还是已经变成一段段各自独立的情绪原因？

{THREAD}

只输出一个 json 代码块：
```json
{{"ok": true, "valuable": ["……"], "problems": [{{"sec": "S04", "why": "……"}}], "reason": "一两句"}}
```"""


class Run:
    def __init__(s, T, w, a, pool):
        s.T, s.w, s.a, s.pool = T, w, a, pool; s.b = "g56" if a == "g6" else "g6"
        s.dir = OUT / f"{T}_{w}"; s.dir.mkdir(parents=True, exist_ok=True)
        s.segs = draft10.segs(w); s.beads = covjudge.beads(w)
        s.state = {}          # sec -> {"pick", "check", "extra", "chosen", "hist"}
        s.backs = 0

    # ---------- inputs ----------
    def seg(s, sec):
        k = next(i for i, x in enumerate(s.segs) if x["id"] == sec); return k, s.segs[k]

    def history(s, upto):
        hs = []
        for x in s.segs:
            if x["id"] == upto:
                break
            hs += s.state.get(x["id"], {}).get("hist", [])
        return hs

    def hist_text(s, hs):
        if not hs:
            return "（这是第一段，还没有历史）"
        return "\n".join(f"{h['id']}（{h['sec']}）{h['text']}" + (f"［解释过 {', '.join(h['explains'])}］" if h.get("explains") else "［没有解释过听感，只是设定］")
                         for h in hs)

    def bead_text(s, sec, ids=None):
        return "\n".join(f"- {b['id']}［{b['role']}］{b['text']}" for b in s.beads
                         if b["sec"] == sec and b["role"] != "演奏条件" and (ids is None or b["id"] in ids))

    def mechs(s, sec):
        p = json.loads((POOL / s.pool / s.w / f"{sec}.json").read_text(encoding="utf-8"))["mechs"]
        return p + s.state.get(sec, {}).get("extra", [])

    def mech_text(s, ms):
        return "\n".join(f"{m['id']}：{m['text']}（需要的前提：{m.get('premise') or '无'}；评审事先认为能解释：{', '.join(m.get('explains') or []) or '无'}"
                         + ("；新增" if m.get("added") else f"；{m.get('n', 1)} 位作者提出") + "）" for m in ms)

    def head(s, sec):
        k, x = s.seg(sec)
        return INTRO.replace("{NAME}", covjudge.NAME[s.w]).replace("{K}", str(k + 1)).replace("{A}", str(x["start"])).replace("{B}", str(x["end"]))

    def pick_msg(s, sec, critique=""):
        m = s.head(sec) + "【已经确立的历史】（编号；方括号里是它当初解释了哪些听感）\n" + s.hist_text(s.history(sec))
        m += "\n\n【这一段的听感记录】（另一批人听这段写下的原文；方括号里的归类只是整理者的分类，不代表重要性）\n" + s.bead_text(sec)
        m += "\n\n【候选解释】（不同作者对这一段的解释，已按机制归并）\n" + s.mech_text(s.mechs(sec)) + "\n\n" + PICK
        if critique:
            m += "\n\n上一次的选择被检查者退回了，理由如下；请据此重选（如果检查者说得不对，可以说明理由后坚持）：\n" + critique
        return m

    def picked_text(s, sec, pk):
        lines = [f"第{i + 1}条：{c['text']}（依赖：{', '.join(c.get('depends') or []) or '无'}；解释：{', '.join(c.get('explains') or [])}）"
                 for i, c in enumerate(pk.get("chosen") or [])]
        lines += [f"听感去处 {b}：{f}" for b, f in (pk.get("fate") or {}).items()]
        lines += [f"新确立的历史：{h['text']}（解释：{', '.join(h.get('explains') or [])}）" for h in pk.get("new_history") or []]
        return "\n".join(lines)

    def check_msg(s, sec, pk):
        m = s.head(sec) + "【已经确立的历史】\n" + s.hist_text(s.history(sec)) + "\n\n【这一段的听感记录】\n" + s.bead_text(sec) + "\n\n"
        k, _ = s.seg(sec)
        return m + CHECKQ.format(K=k + 1, PICKED=s.picked_text(sec, pk))

    # ---------- calls ----------
    def call(s, rid, msg, mdl, meta):
        rid = f"sy{s.T}_{s.w}_{rid}"
        for r in (rid, rid + "_x"):
            if not evo.done(r):
                node2b.job(r, msg, {"stage": "synth", "T": s.T, **meta}, w=mdl)[1]()
            try:
                return evo.parse_json(evo.output(r))
            except Exception:
                continue
        raise RuntimeError(f"{rid}: no parsable answer")

    def commit(s, sec, pk, ck):
        hs = s.history(sec); n0 = len(hs) + sum(len(s.state[x]["hist"]) for x in s.state if x != sec and s.seg(x)[0] > s.seg(sec)[0])
        start = 1 + max([int(h["id"][1:]) for x in s.state.values() for h in x.get("hist", [])] + [0])
        hist = [{"id": f"H{start + i}", "sec": sec, "text": h["text"], "explains": h.get("explains") or []}
                for i, h in enumerate(pk.get("new_history") or [])]
        s.state.setdefault(sec, {}).update(pick=pk, check=ck, chosen=pk.get("chosen") or [], hist=hist)
        (s.dir / f"{sec}.json").write_text(json.dumps(s.state[sec], ensure_ascii=False, indent=1), encoding="utf-8")

    def segment(s, sec, tag=""):
        pk = s.call(f"{sec}{tag}_A", s.pick_msg(sec), s.a, {"sec": sec, "step": "A"})
        ck = s.call(f"{sec}{tag}_B", s.check_msg(sec, pk), s.b, {"sec": sec, "step": "B"})
        if not ck.get("pass"):
            crit = "\n".join(ck.get("problems") or []) + "\n" + (ck.get("reason") or "")
            pk = s.call(f"{sec}{tag}_A2", s.pick_msg(sec, crit), s.a, {"sec": sec, "step": "A2"})
            ck = s.call(f"{sec}{tag}_B2", s.check_msg(sec, pk), s.b, {"sec": sec, "step": "B2"})
        narrow = [u["id"] for u in ck.get("unexplained") or [] if u.get("why") == "池子太窄"]
        if narrow and not s.state.get(sec, {}).get("extra"):
            m = s.head(sec) + "【已经确立的历史】\n" + s.hist_text(s.history(sec)) + "\n\n"
            fl = s.call(f"{sec}{tag}_D", m + FILL.format(BEADS=s.bead_text(sec, narrow)), s.a, {"sec": sec, "step": "D"})
            extra = [{"id": f"G{i + 1}", "text": c["text"], "premise": c.get("premise"), "explains": c.get("explains") or [], "added": True}
                     for i, c in enumerate(fl.get("cands") or []) if c.get("text")]
            s.state.setdefault(sec, {})["fill"] = fl
            if extra:
                s.state[sec]["extra"] = extra
                pk = s.call(f"{sec}{tag}_A3", s.pick_msg(sec), s.a, {"sec": sec, "step": "A3"})
                ck = s.call(f"{sec}{tag}_B3", s.check_msg(sec, pk), s.b, {"sec": sec, "step": "B3"})
        s.commit(sec, pk, ck)
        print(f"{s.T} {s.w} {sec}{tag} pass={ck.get('pass')} chosen={len(pk.get('chosen') or [])} "
              f"unexplained={[u['id'] + ':' + u.get('why', '') for u in ck.get('unexplained') or []]}", flush=True)
        return pk, ck

    def back(s, sec, pk, ck):
        """C: one attempt per conditional / 缺前提 item, while the run has backtracks left"""
        wants = [(c.get("id"), c.get("missing")) for c in pk.get("conditional") or []]
        wants += [(u["id"], u.get("note")) for u in ck.get("unexplained") or [] if u.get("why") == "缺前提"]
        for mid, missing in wants[:1]:
            if s.backs >= BACK_MAX or not missing:
                return False
            k, _ = s.seg(sec)
            text = next((m["text"] for m in s.mechs(sec) if m["id"] == mid), f"（为了解释 {mid}）")
            earlier = "\n\n".join(f"### {x['id']}\n当时选中：{'；'.join(c['text'] for c in s.state[x['id']]['chosen'])}\n候选：\n{s.back_mech_text(s.mechs(x['id']))}"
                                  for x in s.segs[:k])
            r = s.call(f"{sec}_C{s.backs + 1}", BACK.format(K=k + 1, TEXT=text, MISSING=missing, EARLIER=earlier), s.b, {"sec": sec, "step": "C"})
            j = r.get("sec") or ""
            if j not in s.state or s.seg(j)[0] >= k:
                print(f"{s.T} {s.w} {sec} back: none ({r.get('why', '')[:60]})", flush=True); return False
            s.backs += 1
            saved = {x: json.loads(json.dumps(v)) for x, v in s.state.items()}
            hint = f"\n\n回头修改：后面第{k + 1}段需要这个前提——{missing}。请考虑候选 {r.get('mech')}：{r.get('why')}"
            tag = f"_b{s.backs}"
            pk2 = s.call(f"{j}{tag}_A", s.pick_msg(j) + hint, s.a, {"sec": j, "step": "A-back"})
            ck2 = s.call(f"{j}{tag}_B", s.check_msg(j, pk2), s.b, {"sec": j, "step": "B-back"})
            ok = bool(ck2.get("pass"))
            if ok:
                s.commit(j, pk2, ck2)
                for x in s.segs[s.seg(j)[0] + 1: k + 1]:
                    _, c3 = s.segment(x["id"], tag)
                    ok = ok and bool(c3.get("pass"))
            if not ok:
                s.state = saved
                for x, v in saved.items():
                    (s.dir / f"{x}.json").write_text(json.dumps(v, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"{s.T} {s.w} {sec} back to {j} via {r.get('mech')}: {'accepted' if ok else 'rejected'}", flush=True)
            return ok
        return False

    def back_mech_text(s, ms):
        return s.mech_text(ms)

    def glob_check(s, sec):
        k, _ = s.seg(sec)
        th = "\n\n".join(f"### 第{i + 1}段（{x['start']}–{x['end']}）\n" + "\n".join(f"- {c['text']}（依赖：{', '.join(c.get('depends') or []) or '无'}）" for c in s.state[x['id']]['chosen'])
                         for i, x in enumerate(s.segs[:k + 1]))
        th += "\n\n### 已确立的历史\n" + s.hist_text(s.history(s.segs[k + 1]["id"]) if k + 1 < len(s.segs) else [h for v in s.state.values() for h in v["hist"]])
        r = s.call(f"{sec}_G", GLOBAL.format(K=k + 1, THREAD=th), s.b, {"sec": sec, "step": "G"})
        (s.dir / f"global_{sec}.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{s.T} {s.w} global@{sec} ok={r.get('ok')} problems={[p.get('sec') for p in r.get('problems') or []]}", flush=True)
        return r

    def run(s, last=None):
        for x in s.segs:
            sec = x["id"]
            pk, ck = s.segment(sec)
            if not ck.get("pass") or pk.get("conditional"):
                if s.back(sec, pk, ck):
                    pk, ck = s.state[sec]["pick"], s.state[sec]["check"]
            if sec in CHECK[s.w]:
                s.glob_check(sec)
            if sec == last:
                break
        (s.dir / "run.json").write_text(json.dumps({"T": s.T, "work": s.w, "a": s.a, "b": s.b, "backs": s.backs,
                                                    "chosen": {k: v["chosen"] for k, v in s.state.items()},
                                                    "history": [h for v in s.state.values() for h in v["hist"]]},
                                                   ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    Run(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]).run(sys.argv[5] if len(sys.argv) > 5 else None)
