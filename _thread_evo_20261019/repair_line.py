"""P7 (10-28): independent line + bead-aware local repair, whole piece. Experiment 2 showed bead-aware local repair lets key
segments match package 3 (strict 10/10, bridge 7/7 judged 不差于), and that the bridge boundary of the gpt-5.6 advisor
(a local cause tied to established history; no new backstory or events, no music-as-cause, no change of the centre)
mostly stays in bounds. T0 = P4d, frozen: its Center and history are left alone, so every segment is repaired at the same
time. Per segment: edit (g6) -> boundary check (g56); a segment out of bounds or not readable without beads gets one
revision with the checker's notes. Then the line is assembled (T0 Center and labels, repaired items) and judged as a whole
against package 3 by finalize3's two regression judges. Package 3 is never shown to the editor.
ids: pe7_/pc7_/pe7r_/pc7r_<work>_<sec>, fn7_<work>_R_<judge>.  usage: THREAD_ROUTE=gpt3s python repair_line.py -> evaluations/repair/"""
import json, os
os.environ["PRECISE_MODE"] = "bridge"
import covjudge, deliver_halfdone as D, draft10, evo, node2b, finalize3, precise as P

OUT = evo.ROOT / "evaluations" / "repair"
# 10-28 evening: the first P7 edits wrote H/M ids, notes on the edit ("原解释第1条……") and bead bar positions into feel/why.
REVISE = """

【上一次修准被核对者退回】
{NOTES}
请据此重做这一段的修准：只改被指出的问题（越界的地方去掉或改成有依据的说法，和已确立历史冲突的地方改成一致，指向音乐段落的“它”“这次”之类说清是什么感受），其余照旧。
另外，feel 和 why 是给读者看的正文：不写 H、M 编号（依据只写在 basis 里），不写小节号，不写对修改本身的说明（例如“原解释……”“这条解释……”）。"""
# 10-28 evening: segments whose E2b edit passed (checker found nothing out of bounds, both judges 不差于 package 3) keep it,
# as deliver_halfdone does; they are neither re-checked nor revised.
PASSED = {(w, s["id"]) for w in ("op60", "op61") for s in draft10.segs(w) if D.e2b_passed(w, s["id"])}


def parse(rid):
    try:
        return evo.parse_json(evo.output(rid))
    except Exception:
        return None


def new_text(items):
    return "\n".join(f"{i}. 感受：{x.get('feel', '')} 为什么：{x.get('why', '')}（依据：{json.dumps(x.get('basis'), ensure_ascii=False)}）" for i, x in enumerate(items, 1))


def run():
    OUT.mkdir(exist_ok=True)
    ctx = {}
    for w in ("op60", "op61"):
        fin, st = P.t0(w); bs = covjudge.beads(w)
        for s in draft10.segs(w):
            sec = s["id"]
            beads = "\n".join(f"- {b['id']}［{b['role']}］{b['text']}" for b in bs if b["sec"] == sec and b["role"] != "演奏条件")
            ms = json.loads((evo.ROOT / "evaluations" / "pool" / P.POOL / w / f"{sec}.json").read_text(encoding="utf-8"))["mechs"]
            cands = "\n".join(f"{m['id']}{'（转折）' if ('#t' in m['rep']['src'] or '#c' in m['rep']['src']) else ''}：感受：{m['rep']['feel']} 为什么：{m['rep']['thread']}" for m in ms)
            cur = P.cur_items(fin, sec); hist = P.hist_before(w, st, sec)
            msg = P.E.format(NAME=covjudge.NAME[w], A=s["start"], B=s["end"], CENTER=fin.get("center", ""), HIST=hist,
                             CUR="\n".join(f"{i}. {c}" for i, c in enumerate(cur, 1)), BEADS=beads, CANDS=cands)
            ctx[(w, sec)] = dict(s=s, ms={m["id"]: m for m in ms}, cur=cur, hist=hist, msg=msg, fin=fin)

    def edit_jobs(tag, extra=lambda k: ""):
        return [node2b.job(f"{tag}_{w}_{sec}", c["msg"] + extra((w, sec)), {"stage": "repair"}, w="g6")
                for (w, sec), c in ctx.items() if not evo.done(f"{tag}_{w}_{sec}") and (tag == "pe7" or c.get("revise"))]

    def check_jobs(etag, ctag):
        jobs = []
        for (w, sec), c in ctx.items():
            e = parse(f"{etag}_{w}_{sec}")
            if not e or (w, sec) in PASSED or (ctag == "pc7r" and not c.get("revise")):
                continue
            c["edit"] = e; items = e.get("items") or []
            src = "\n".join(f"{m}：{c['ms'][m]['rep']['thread']}" for x in items for m in (x.get("basis") or {}).get("M") or [] if m in c["ms"]) or "（没有引候选）"
            if not evo.done(f"{ctag}_{w}_{sec}"):
                jobs.append(node2b.job(f"{ctag}_{w}_{sec}", P.C.format(HIST=c["hist"], CUR="\n".join(f"{i}. {t}" for i, t in enumerate(c["cur"], 1)),
                                                                        SRC=src, NEW=new_text(items)), {"stage": "repair-check"}, w="g56"))
        return jobs

    evo.run_parallel(edit_jobs("pe7"), 27)
    if os.environ.get("REPAIR_PROBE"):                # 10-28 after the account-protection stop: one real call first, then exit
        jobs = check_jobs("pe7", "pc7")
        print("待核对：", [j[0] for j in jobs], flush=True)
        evo.run_parallel(jobs[:1], 1)
        return
    evo.run_parallel(check_jobs("pe7", "pc7"), 27)
    for (w, sec), c in ctx.items():
        if (w, sec) in PASSED:
            continue
        k = parse(f"pc7_{w}_{sec}") or {}
        over = [x for x in k.get("items") or [] if x.get("label") != "ok"]
        c["check"] = k
        if over or k.get("readable") == "否":
            c["revise"] = "\n".join([f"- 第{x.get('i')}条：{x.get('why', '')}" for x in over]
                                    + ([f"- 拿掉听感记录读不懂：{k.get('readable_why', '')}"] if k.get("readable") == "否" else []))
    print("需要退改的段：", [f"{w} {s}" for (w, s), c in ctx.items() if c.get("revise")], flush=True)
    evo.run_parallel(edit_jobs("pe7r", lambda key: REVISE.format(NOTES=ctx[key]["revise"])), 27)
    evo.run_parallel(check_jobs("pe7r", "pc7r"), 27)
    rows = {}
    for (w, sec), c in ctx.items():
        if (w, sec) in PASSED:
            final, k = parse(f"peE2b_{w}_{sec}"), parse(f"pcE2b_{w}_{sec}") or {}
        else:
            final = parse(f"pe7r_{w}_{sec}") if c.get("revise") else parse(f"pe7_{w}_{sec}")
            k = (parse(f"pc7r_{w}_{sec}") if c.get("revise") else c.get("check")) or {}
        if not final:
            final = parse(f"pe7_{w}_{sec}") or {"items": []}
        over = [x for x in k.get("items") or [] if x.get("label") != "ok"]
        rows[(w, sec)] = dict(edit=final, over=over, readable=k.get("readable"), revised=bool(c.get("revise")), e2b=(w, sec) in PASSED)
        print(f"{w} {sec}: {'用 E2b' if (w, sec) in PASSED else '退改 ' + str(bool(c.get('revise')))} | 越界 {len(over)} | 能独立读懂 {k.get('readable')} | 条数 {len(final.get('items') or [])}", flush=True)
    for w in ("op60", "op61"):
        fin = next(c["fin"] for (ww, _), c in ctx.items() if ww == w)
        lines = [f"{covjudge.NAME[w]}", f"Center：{fin.get('center', '')}", ""]
        for s in draft10.segs(w):
            lab = next((x.get("label", "") for x in fin["sections"] if x["sec"] == s["id"]), "")
            lines += [f"{s['id']} ｜ {s['start']}–{s['end']}小节 ｜ {lab}", ""]
            for x in rows[(w, s["id"])]["edit"].get("items") or []:          # ids / edit notes dropped (deliver_halfdone.clean)
                lines += [f"• {D.clean(x.get('feel', ''))}", f"  → {D.clean(x.get('why', ''))}"]
            lines.append("")
        txt = "\n".join(lines)
        (OUT / f"P7_{w}.txt").write_text(txt, encoding="utf-8")
        old = finalize3.PKG3[w].read_text(encoding="utf-8-sig")
        evo.run_parallel([node2b.job(f"fn7_{w}_R_{j}", finalize3.R.format(NAME=covjudge.NAME[w], OLD=old, NEW=txt), {"stage": "repair-R"}, w=j)
                          for j in ("g6", "g56") if not evo.done(f"fn7_{w}_R_{j}")], 2)
        reg = {j: parse(f"fn7_{w}_R_{j}") or {} for j in ("g6", "g56")}
        json.dump({"rows": {f"{ww}_{s}": r for (ww, s), r in rows.items() if ww == w}, "regression": reg},
                  open(OUT / f"P7_{w}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(w, "整首对照包3：", {j: r.get("verdict") for j, r in reg.items()}, flush=True)


if __name__ == "__main__":
    run()
