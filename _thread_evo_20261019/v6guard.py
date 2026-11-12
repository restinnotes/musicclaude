"""DAG N10g (11-01): coverage guard after any rewrite round — coverage may not drop below the base, segment by segment.
  alias <tag> <newtag>    : copy a line under a new tag (so it can be measured again with the current route/judges)
  fix <base> <tag> <out>  : per segment, score = Σ judges (说清 2 / 偏弱 1 / else 0) over its beads (cov_<w>_<j>_<tag>);
                            segments whose score fell ≥2 below the base are re-said by the writer with: the base text of the
                            segment, the beads that lost their link (bead text + the judge's reason) — keep the current
                            wording style, restore only the reasons that let those beads attach (related is enough; no bead
                            imagery, no new events). Others stay word for word. ids gd_<w>_<out>.
  revert <base> <tag> <out>: segments still ≥2 below the base (after measuring <tag>) go back to the base text.
usage: python v6guard.py alias h13 h13g | fix h13g h17g h18 | revert h13g h18 h18k"""
import json, os, shutil, sys
import covjudge, evo, v6fix as V
from v6gen import build, gloss_text
from v6human import line_json

PTS = {"说清": 2, "偏弱": 1}

FIX = """下面是肖邦{NAME}的一条“线”里的几段：一个人在这首曲子里经历的一件事，按段写成条目。线的作用是把每段的听感记录（“珠子”）串起来：只要线里有能让人感到和珠子情境相近的原因就行，不需要逐颗解释珠子。
这几段刚改过语言，读起来更顺了，但核对的评委发现，有些珠子和线接不上了——早一版的这一段接得上（见每段的【早一版】和【接不上的珠子】）。
请重写这几段：
- 找回让这些珠子接得上的那层意思（早一版里是怎么说的，可以参考），只要相关即可，不要逐颗解释珠子，不要把珠子里的画面、声音、比喻写进线，不要加新的事件或人物。
- 保持现在这版的说话口气和顺畅程度，不要退回早一版的写法；字数大致和现在这版相当。
- 每条的 cite 照现在这版填；第三人称“他”。

{SEGS}

【Center 各部分指什么】
{GLOSS}

只输出这几段改好的 json：
```json
{{"segments": [{{"sec": "S01", "items": [{{"text": "……", "cite": []}}]}}]}}
```"""


def bead_status(w, tag):
    """{(sec, bead): [points per judge]} and {(sec, bead): row} from the coverage judges of <tag>"""
    st, rows = {}, {}
    for j in V.JUDGES:
        for x in (V.parse(f"cov_{w}_{j}_{tag}") or {}).get("beads") or []:
            k = (x.get("sec"), str(x.get("bead")).split("-")[-1])
            st.setdefault(k, {})[j] = PTS.get(x.get("status"), 0); rows.setdefault(k, {})[j] = x
    return st, rows


def drops(w, base, tag):
    sb, _ = bead_status(w, base); st, rows = bead_status(w, tag)
    judges = [j for j in V.JUDGES if any(j in v for v in sb.values()) and any(j in v for v in st.values())]
    seg = {}
    for k in set(sb) | set(st):
        b = sum(sb.get(k, {}).get(j, 0) for j in judges); t = sum(st.get(k, {}).get(j, 0) for j in judges)
        seg.setdefault(k[0], [0, 0, []]); seg[k[0]][0] += b; seg[k[0]][1] += t
        if t < b:
            seg[k[0]][2].append((k[1], b, t, rows.get(k, {})))
    return {sec: v for sec, v in seg.items() if v[1] <= v[0] - 2}, judges


def fix(base, tag, out):
    beads = {w: {(b["sec"], b["id"].split("-")[-1]): b for b in covjudge.beads(w)} for w in ("op60", "op61")}
    def piece(w):
        bad, judges = drops(w, base, tag)
        A = {s["sec"]: s for s in json.loads(line_json(V.graph_of(w, base)))["segments"]}
        B = {s["sec"]: s for s in json.loads(line_json(V.graph_of(w, tag)))["segments"]}
        print(w, out, "评委", judges, "覆盖比底版低≥2 的段", {s: (v[0], v[1]) for s, v in sorted(bad.items())}, flush=True)
        rid = f"gd_{w}_{out}"; e = {}
        if bad:
            segs = []
            for sec, (b, t, lost) in sorted(bad.items()):
                lines = [f"### {sec}", "【早一版】"] + [f"- {it['text']}" for it in A[sec]["items"]]
                lines += ["【现在这版】（json）", json.dumps(B[sec]["items"], ensure_ascii=False), "【接不上的珠子】"]
                for bid, pb, pt, rr in lost:
                    why = "；".join(x.get("why", "") for x in rr.values())
                    lines.append(f"- {bid}：{beads[w].get((sec, bid), {}).get('text', '')[:220]}（评委：{why}）")
                segs.append("\n".join(lines))
            msg = FIX.format(NAME=covjudge.NAME[w], SEGS="\n\n".join(segs), GLOSS=gloss_text(w))
            if not evo.done(rid):
                evo.call_argon_direct(rid, msg, meta={"stage": "v6-guard-fix"}) if os.environ.get("HUMAN_WRITER", "argon") == "argon" else evo.call(rid, msg, model=evo.G6, meta={"stage": "v6-guard-fix"})
            e = V.parse(rid) or {}
            e["segments"] = [s for s in e.get("segments") or [] if s.get("sec") in bad]
        G, _ = build(w, tag, out, e, allow_empty=True)
        print(w, out, "重写了", [s["sec"] for s in e.get("segments") or []], "字数", sum(len(i["text"]) for s in G["segments"] for i in s["items"]), flush=True)
    evo.run_parallel([(w, (lambda w=w: piece(w))) for w in ("op60", "op61")], 2)


def revert(base, tag, out):
    for w in ("op60", "op61"):
        bad, judges = drops(w, base, tag)
        A = {s["sec"]: s for s in json.loads(line_json(V.graph_of(w, base)))["segments"]}
        e = {"segments": [{"sec": sec, "items": [{"text": it["text"], "cite": it["cite"]} for it in A[sec]["items"]]} for sec in bad if sec in A]}
        G, _ = build(w, tag, out, e, allow_empty=True)
        print(w, out, "仍比底版低、退回底版的段", sorted(bad), "字数", sum(len(i["text"]) for s in G["segments"] for i in s["items"]), flush=True)


def alias(tag, new):
    for w in ("op60", "op61"):
        for ext in ("json", "md"):
            shutil.copy(V.OUT / f"{w}_{tag}.{ext}", V.OUT / f"{w}_{new}.{ext}")
    print("alias", tag, "->", new)


if __name__ == "__main__":
    a = sys.argv[1:]
    {"alias": lambda: alias(a[1], a[2]), "fix": lambda: fix(a[1], a[2], a[3]), "revert": lambda: revert(a[1], a[2], a[3])}[a[0]]()
