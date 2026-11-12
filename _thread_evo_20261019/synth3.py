"""Path assembly from the pool only (PLAN_20261026.md step 4, 10-27). synth.Run with three changes:
- candidates are pool3 groups shown in their representative member's own words (feel + why), with premise / bridge /
  result labels for matching only;
- the line must reuse those words: allowed edits are a pronoun or reference, dropping a repeat, joining two compatible
  candidates' sentences; the pick lists every edit, the check fails a text that is more abstract than its source or
  carries a reason no candidate gave; the check also fails pseudo-causes ("更在乎/更有分量/经历过所以不一样"),
  permission-as-cause ("可以/不等于") and music-returns-as-world-fact;
- no fill step: beads the pool cannot explain on this path stay as gaps (counted at the end), back-tracking as before.
ids: sy<T>_<work>_<sec>_{A|B|A2|B2|C*|G}.  usage: THREAD_ROUTE=mimic python synth3.py <T> <work> <pool-tag> [last-sec]"""
import json, sys
import synth, pool
synth.BACK_MAX = 3      # 10-27 evening: back-tracking fully on again (it was 2 for the 8-hour deadline)

PICK = """任务：
1. 候选很多。先通读，再只对你认真考虑过的候选（最多 10 条，包括最后选中的）写评估，写清：它解释了这一段哪几条听感；它需要的前提在已确立的历史里有没有（写出 H 编号，没有就写“缺：缺什么”）；它有没有加入听感撑不住的人物设定（身份、前史、外部事件）；它的理由放到别的段落是否也成立；它是在讲原因，还是只说了结果。
   下面几种不算原因：“经历过前面那些，所以不一样了”“更在乎了 / 更珍惜了 / 有了新的分量 / 不是原来的自己”（没有说出前面具体发生了什么、为什么造成现在）；“可以这样 / 不等于那样 / 允许……”（只排除了一种理解）；把音乐回来、变亮、变强当成对方回应了、关系恢复了、得到了保证。
2. 选出这一段用哪几条。几条解释力相当时，选原话更具体、更像普通人说话的那条（例如说出“这一刻会过去”比“需要没有被安顿”好）。解释不同侧面、又能同时成立的可以并存；互相排斥的只取一条；一段只需要一个理由时就只写一个。
3. 这一段的文字必须直接用所选候选的原话（感受和为什么）。只允许这几种改动：把“他/那个人”之类的指代补清楚；删掉和前一段重复的半句；把两条相容候选的原话前后接起来。不许改写成概括的说法，不许加入候选里没有的理由。每一处改动都要在 edits 里写出来。
4. 每条听感判一个去处：被选中的第几条解释了它；或者与选中的解释相容、作为感受独立保留（说明为什么不需要另立理由）；或者是另一种听法，与本段的理解互斥；或者现在没有解释。如果这一段最重要的感受只能“独立保留”或“没有解释”，就直说。
5. 写出这一段新确立的历史（以后可能用到的经历），尽量用所选候选自己写的“新增历史”原话，每条注明它解释了哪些听感。只写他心里真实发生过的具体事。
6. 如果有好的候选只是因为前提“缺”而用不上，单独列出来，写清缺的是什么。

只输出一个 json 代码块：
```json
{"eval": [{"id": "M1", "explains": ["S03-B2"], "premise": "H2 或 缺：……", "invented": "", "any_segment": false, "result_only": false, "note": "一句"}],
 "chosen": [{"text": "用候选原话写成的这一段解释", "from": ["M1"], "depends": ["H2"], "explains": ["S03-B2"], "edits": ["补了指代：……"]}],
 "fate": {"S03-B1": "第1条", "S03-B2": "独立保留：为什么", "S03-B3": "另一种听法", "S03-B4": "没有解释"},
 "new_history": [{"text": "……", "explains": ["S03-B2"]}],
 "conditional": [{"id": "M5", "missing": "……"}]}
```"""
CHECK_EXTRA = """
另外检查（任何一条不满足就判不合格）：
6. 选中的文字是否就是候选原话，只做了补指代、删重复、前后接起来这几种改动？如果被改写得比原话更抽象（例如换成“延续需要”“安顿”“承托”“分量”这类词），或者加了候选里没有的理由，判不合格。
7. 理由是不是空的：“经历过所以不一样了”“更在乎了 / 更有分量了”“可以这样 / 不等于那样”，或者把音乐回来当成对方回应、关系恢复，都不算原因。

【候选原话】（用来核对第 6 条）
{SOURCES}"""


CAUSE_RULE = """
   不同的原因不要合并：一种感受可能来自时间（留不住、正在过去），来自另一个人和两人之间（对方怎么想、以后不由他一个人决定），也可能来自他自己（力气、身体、自己能做到什么）。它们是不同的原因，不能互相代替。判断这一段指向哪一种，只看这一段的听感记录本身写了什么：听感写到另一个人、要说出口的话、关系，才用和另一个人有关的原因；听感写的是用力、撑住、抗拒、愤怒、疲惫、身体，就用他自己的原因，不要因为前面的历史里有那个人，就把它说成和那个人有关。这条 Thread 前面用得最多的那个理由，不能自动拿来解释这一段。听感里有具体的对象（一个人、一句话、一段关系）时，选把这个对象说出来的候选，不选把它说成“事情”“获得”“满足”“需要”“答案”“着落”的候选。"""
CAUSE_CHECK = """
8. 所选解释有没有把听感指向的另一种原因（例如和另一个人、两人之间有关，或和他自己的力气、身体有关）并进这条 Thread 一直在用的那个原因，或者把听感里具体的对象说成了“事情”“获得”“满足”“需要”“答案”“着落”？有就判不合格，并写出听感指向的是哪种原因。"""


FEW_RULE = """
   一段最多选 4 条。几条候选说的是同一个变化、同一个原因时，只留原话最清楚的一条；宁可少而清楚，不要把相近的说法并排。"""
FRAME_HINT = """

【第一段的起点】建池时有一位评审读了全曲各段的听感记录，认为下面这几条候选的起点最能让后面各段的听感顺下来、被前后连贯地解释（评审没有看作者人数）：
{TOP}
第一段确立的处境和原因会成为整条 Thread 的起点。请优先在这几条里选第一段的主要解释；如果它们解释不了这一段自己的听感，可以说明理由后另选。不要因为别的候选作者多就选它。"""
METAPHOR_CHECK = """
9. 听感记录里写成比喻的地方（像……、仿佛……）是在描述感受，不能因为它是比喻就判“听感存疑”；要看的是比喻背后的感受有没有被解释。选中的条数多于 4 条，或者几条说的是同一个变化、同一个原因，也判不合格。"""


TURN_RULE = """
   段内转折：选定整段解释以后，逐条看这一段里写着变化的听感（先怎样、后来怎样，突然、渐渐、一下子、刚……就……）。如果整段解释没有具体说出这一处为什么恰好在此刻发生，而某条【段内转折候选】说出了，就把它也选上，和整段解释并存；不要因为“整段解释大体也能涵盖”就不选。转折候选说的“刚才”如果是这一段里刚发生的事，不算缺前提；如果指的是这条 Thread 前面没有确立过的事，照常算缺。"""


class Run(synth.Run):
    turns = False      # 10-27 P4c: D21's in-segment turns shown as their own list, and the picker must look at them
    frame = False      # 10-28 P5: S01 hinted by a whole-piece frame ranking; metaphors are feelings; at most 4 items
    causes = False     # 10-27 P4e: P4a folded "the other's will / their future" into "time can't be held"; keep causes apart

    def mechs(s, sec):
        out = []
        for m in json.loads((pool.OUT / s.pool / s.w / f"{sec}.json").read_text(encoding="utf-8"))["mechs"]:
            r = m["rep"]
            out.append({"id": m["id"], "text": f"感受：{r['feel']} 为什么：{r['thread']}", "premise": m.get("premise"),
                        "bridge": m.get("bridge"), "result": m.get("result"), "weak": m.get("weak"), "n": m.get("n", 1),
                        "explains": m.get("explains") or [], "new": r.get("new") or [], "turn": "#t" in r["src"] or "#c" in r["src"]})
        return out

    def mech_text(s, ms):
        """P4a showed turn groups mixed in with "评审事先认为能解释：无"; the picker looked at 17 of them out of 256 and chose 3.
        With turns on, whole-segment candidates and turns are two lists, and a turn says it was never judged on its own."""
        if not s.turns:
            return s.mech_list(ms)
        whole = [m for m in ms if not m.get("turn")]; turn = [m for m in ms if m.get("turn")]
        out = "【整段解释候选】\n" + s.mech_list(whole)
        if turn:
            labeled = any(m.get("explains") for m in turn)          # pool P27t: turns judged on their own (tlabel.py)
            out += ("\n\n【段内转折候选】（每条只解释这一段里的一处变化：先怎样、后来怎样，以及为什么恰好在这时；"
                    + ("评审单独判过每条转折能解释哪些听感）\n" if labeled else "它们没有被单独评审过，所以没有“评审事先认为能解释”）\n")
                    + "\n".join(
                        f"{m['id']}：［原话］{m['text']}\n    （前提：{m.get('premise') or '无'}；桥：{m.get('bridge') or '—'}；"
                        + (f"评审事先认为能解释：{', '.join(m['explains']) or '无'}；" if labeled else "") + f"{m['n']} 位作者提出"
                        + (f"；建池时提示理由可能是空的：{m['weak']}" if m.get("weak") else "") + "）" for m in turn))
        return out

    def mech_list(s, ms):
        return "\n".join(
            f"{m['id']}：［原话］{m['text']}\n    （前提：{m.get('premise') or '无'}；桥：{m.get('bridge') or '—'}；"
            f"作者自己写的新增历史：{'；'.join(m.get('new') or []) or '无'}；评审事先认为能解释：{', '.join(m['explains']) or '无'}；"
            f"{m['n']} 位作者提出" + (f"；建池时提示理由可能是空的：{m['weak']}" if m.get("weak") else "") + "）" for m in ms)

    def back_mech_text(s, ms):
        """10-27 evening: C listed every earlier candidate in full; with P27 (~50 groups a segment) the prompt passed gpt3's
        65,536-character limit at Op.61 S06. A missing premise is looked up by what a candidate would establish, so C now
        sees only candidates with new history: result label, premise, and their own new-history words (<= ~55k at S13)."""
        return "\n".join(f"{m['id']}：{m.get('result') or m['text'][:60]}（前提：{m.get('premise') or '无'}；能确立的历史：{'；'.join(m['new'])}）"
                         for m in ms if m.get("new"))

    def call(s, rid, msg, mdl, meta):
        """C also gets every earlier candidate in its own words as an attachment (10-27 user: attach, do not cut)"""
        if meta.get("step") == "C" and not meta.get("attach") and s.seg(meta["sec"])[0] > 0:     # S01 has nothing earlier
            k, _ = s.seg(meta["sec"]); d = synth.evo.RUNS / f"sy{s.T}_{s.w}_{rid}_att"; d.mkdir(exist_ok=True)
            f = d / "earlier_candidates.txt"
            f.write_text("\n\n".join(f"### {x['id']}\n当时选中：{'；'.join(c['text'] for c in s.state[x['id']]['chosen'])}\n候选：\n"
                                     f"{s.mech_text(s.mechs(x['id']))}" for x in s.segs[:k]), encoding="utf-8")
            msg = msg.replace("\n\n只输出一个 json 代码块：", "\n\n（上面每段只列了能确立历史的候选摘要；各段全部候选的完整原话在附件 "
                              "earlier_candidates.txt 里，判断某条候选能否提供前提、那一段改了以后是否仍成立时，请读附件里的原话。）"
                              "\n\n只输出一个 json 代码块：", 1)
            meta = dict(meta, attach=[str(f)])
        return synth.Run.call(s, rid, msg, mdl, meta)

    def pick_msg(s, sec, critique=""):
        m = synth.Run.pick_msg(s, sec, critique)
        p = PICK
        if s.turns and any(x.get("turn") for x in s.mechs(sec)):
            p = p.replace("（最多 10 条，包括最后选中的）", "（整段候选最多 8 条，另外至少认真看 4 条段内转折候选；包括最后选中的）")
            p = p.replace("\n3. 这一段的文字必须", TURN_RULE + "\n3. 这一段的文字必须", 1)
            assert TURN_RULE in p and "至少认真看 4 条" in p
        if s.causes:
            p = p.replace("\n3. 这一段的文字必须", CAUSE_RULE + "\n3. 这一段的文字必须", 1)
            assert CAUSE_RULE in p
        if s.frame:
            p = p.replace("\n3. 这一段的文字必须", FEW_RULE + "\n3. 这一段的文字必须", 1)
            assert FEW_RULE in p
            if s.seg(sec)[0] == 0:
                p += s.frame_hint()
        return m.replace(synth.PICK, p)

    def frame_hint(s):
        top = json.loads((pool.OUT / s.pool / s.w / "frame.json").read_text(encoding="utf-8"))["top"]
        return FRAME_HINT.format(TOP="\n".join(f"- {t['id']}：{t.get('why', '')}（和后面 {', '.join(t.get('fits') or [])} 的听感最对得上）" for t in top))

    def check_msg(s, sec, pk):
        used = {i for c in pk.get("chosen") or [] for i in c.get("from") or []}
        src = "\n".join(f"{m['id']}：{m['text']}" for m in s.mechs(sec) if m["id"] in used) or "（没有选中候选）"
        extra = CHECK_EXTRA.replace("\n\n【候选原话】", CAUSE_CHECK + "\n\n【候选原话】", 1) if s.causes else CHECK_EXTRA
        if s.frame:
            extra = extra.replace("\n\n【候选原话】", METAPHOR_CHECK + "\n\n【候选原话】", 1)
        return synth.Run.check_msg(s, sec, pk).replace("\n\n只输出一个 json 代码块：", extra.format(SOURCES=src) + "\n\n只输出一个 json 代码块：", 1)

    def ctl(s):
        """runs/synth_ctl.json, read every segment (10-27 deadline): {"op61": {"a2": false, "back_max": 0}}"""
        try:
            c = json.loads((synth.evo.RUNS / "synth_ctl.json").read_text(encoding="utf-8")).get(s.w, {})
        except Exception:
            c = {}
        if "back_max" in c:
            synth.BACK_MAX = int(c["back_max"])
        return c

    def segment(s, sec, tag=""):
        pk = s.call(f"{sec}{tag}_A", s.pick_msg(sec), s.a, {"sec": sec, "step": "A"})
        ck = s.call(f"{sec}{tag}_B", s.check_msg(sec, pk), s.b, {"sec": sec, "step": "B"})
        if not ck.get("pass") and (s.ctl().get("a2", True) or synth.evo.done(f"sy{s.T}_{s.w}_{sec}{tag}_A2")):
            crit = "\n".join(ck.get("problems") or []) + "\n" + (ck.get("reason") or "")
            pk = s.call(f"{sec}{tag}_A2", s.pick_msg(sec, crit), s.a, {"sec": sec, "step": "A2"})
            ck = s.call(f"{sec}{tag}_B2", s.check_msg(sec, pk), s.b, {"sec": sec, "step": "B2"})
        s.commit(sec, pk, ck)
        print(f"{s.T} {s.w} {sec}{tag} pass={ck.get('pass')} chosen={len(pk.get('chosen') or [])} "
              f"unexplained={[u['id'] + ':' + u.get('why', '') for u in ck.get('unexplained') or []]}", flush=True)
        return pk, ck


if __name__ == "__main__":
    import os                      # 10-27: SYNTH_A / SYNTH_B pick the picker and checker (P4b = 5.6 for both, to test speed)
    r = Run(sys.argv[1], sys.argv[2], os.environ.get("SYNTH_A", "g6"), sys.argv[3])
    r.b = os.environ.get("SYNTH_B", r.b)
    r.turns = os.environ.get("SYNTH_TURNS") == "1"
    r.causes = os.environ.get("SYNTH_CAUSES") == "1"
    r.frame = os.environ.get("SYNTH_FRAME") == "1"
    r.run(sys.argv[4] if len(sys.argv) > 4 else None)
