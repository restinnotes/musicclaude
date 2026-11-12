"""DAG N10c (11-01): raise coverage — the content gap between a fresh DAG run (覆盖 23–39) and the repaired h-line (35–48).
Beads enter here only through the coverage judges' verdicts, i.e. at the synthesis step (THREAD_SPEC §十: 珠子只在综合这一步进来).
  fix <tag> <out>     : per segment, the beads both/any judge called 偏弱 / 没有 / 相反 (cov_<w>_<j>_<tag>) go to the writer with the
                        bead text and the judges' reasons, together with the beads already 说清 and the items that carry them
                        (must not be lost). The writer adds only the reason in his experience that lets those beads attach
                        (related is enough), keeps the current wording style, copies no bead imagery, adds no events or people.
                        ids bo_<w>_<out>.
  keep <tag> <new> <out>: after measuring <new>, per segment keep the new text only where its coverage score (说清 2 / 偏弱 1,
                        summed over the judges) is higher than <tag>'s; elsewhere the old segment stays.
usage: python v6boost.py fix d4 d5 ; python v6cov.py d5 ; python v6boost.py keep d4 d5 d5k"""
import json, os, sys
import covjudge, evo, v6fix as V
from v6gen import build, gloss_text
from v6human import line_json

PTS = {"说清": 2, "偏弱": 1}
FIX1 = """下面是肖邦{NAME}的一条“线”里的几段：一个人在这首曲子里经历的一件事，按段写成条目。线和逐段的听感记录（“珠子”）放在一起读：线讲他自己的经历，作用是把珠子串起来——线里要有能让人感到和这颗珠子的情境相近的原因或处境，不需要逐颗解释珠子。
评委逐颗核对后发现，这几段里有些珠子和线接不上（见每段【接不上的珠子】，附评委的理由）。请重写这几段，让它们接得上：
- 补的是他经历里的原因、处境或感受的来由，用平常话说；只要相关即可，不要逐颗解释珠子，不要把珠子里的画面、比喻、声音写进线，不要加新的事件或人物。
- 【已经接得上的珠子】靠的那几条的意思必须保留，不能为了补新的把它们弄丢。
- 和前后段的衔接、每段他此刻与整件事的关系不变；保持现在的说话口气；字数最多比现在多两成；每条的 cite 照现在这版填；第三人称“他”。

{SEGS}

【Center 各部分指什么】
{GLOSS}

只输出这几段改好的 json：
```json
{{"segments": [{{"sec": "S01", "items": [{{"text": "……", "cite": []}}]}}]}}
```"""
FIX2 = """下面是肖邦{NAME}的一条“线”里的几段：一个人在这首曲子里经历的一件事，按段写成条目。线和逐段的听感记录（“珠子”）放在一起读：线讲他自己的经历，作用是把珠子串起来——线里要有能让人感到和这颗珠子的情境相近的原因或处境，不需要逐颗解释珠子。
评委逐颗核对后发现，这几段里有些珠子和线接不上（见每段【接不上的珠子】，附评委的理由）。请重写这几段，让它们接得上：
- 补的是他经历里的原因、处境或感受的来由，用平常话说；只要相关即可，不要逐颗解释珠子，不要把珠子里的画面、比喻、声音写进线，不要加新的事件或人物。
- 【已经接得上的珠子】靠的那几条的意思必须保留，不能为了补新的把它们弄丢。
- 每条只说一件事，一两个短句说完。要补的意思多，就在这一段加一条（每段最多 4 条），不要用逗号、分号把几层意思或“这样，却那样”的转折压进同一句。
- 和前后段的衔接不变；每段【他此刻与整件事的关系】不变：标着“没在想”的段，补的原因不能是他在想那件事。
- 保持现在的说话口气；字数最多比现在多三成；原有条目的 cite 照现在这版填，新加的条目 cite 留空；第三人称“他”。

{SEGS}

【Center 各部分指什么】
{GLOSS}

只输出这几段改好的 json：
```json
{{"segments": [{{"sec": "S01", "items": [{{"text": "……", "cite": []}}]}}]}}
```"""
FIX3 = """下面是肖邦{NAME}的一条“线”里的几段：一个人在这首曲子里经历的一件事，按段写成条目。线和逐段的听感记录（“珠子”）放在一起读：线讲他自己的经历，作用是把珠子串起来——线里要有能让人感到和这颗珠子的情境相近的原因或处境，不需要逐颗解释珠子。
评委逐颗核对后发现，这几段里有些珠子和线接不上（见每段【接不上的珠子】，附评委的理由）。请重写这几段，让它们接得上：
- 补的是他经历里的原因、处境或感受的来由，用平常话说；只要相关即可，不要逐颗解释珠子，不要把珠子里的画面、比喻、声音写进线，不要加新的事件或人物。
- 【已经接得上的珠子】靠的那几条的意思必须保留，不能为了补新的把它们弄丢。
- 每条只说一件事，一两个短句说完。要补的意思多，就在这一段加一条（每段最多 4 条），不要用逗号、分号把几层意思或“这样，却那样”的转折压进同一句。
- 和前后段的衔接不变；每段【他此刻与整件事的关系】不变：标着“没在想”的段，补的原因不能是他在想那件事。
- 不加长：每段字数不超过现在。一个原因能同时接上几颗珠子，就只写这一个；写不下的宁可少接一颗，也不要把句子塞满。
- 保持现在的说话口气；原有条目的 cite 照现在这版填，新加的条目 cite 留空；第三人称“他”。

{SEGS}

【Center 各部分指什么】
{GLOSS}

只输出这几段改好的 json：
```json
{{"segments": [{{"sec": "S01", "items": [{{"text": "……", "cite": []}}]}}]}}
```"""

BOOST_V = os.environ.get("BOOST_V", "1")
FIX = {"2": FIX2, "3": FIX3}.get(BOOST_V, FIX1)   # 11-01: v2 = one point per item, may add an item, keep relation; v3 = v2 but no longer than now



def verdicts(w, tag):
    out = {}
    for j in V.JUDGES:
        for x in (V.parse(f"cov_{w}_{j}_{tag}") or {}).get("beads") or []:
            out.setdefault((x.get("sec"), str(x.get("bead")).split("-")[-1]), {})[j] = x
    return out


def seg_score(w, tag, judges=None):
    sc = {}
    for (sec, b), d in verdicts(w, tag).items():
        sc[sec] = sc.get(sec, 0) + sum(PTS.get(x.get("status"), 0) for j, x in d.items() if judges is None or j in judges)
    return sc


def common_judges(w, a, b):
    """only judges that returned a verdict on both versions (a failed judge must not tilt the comparison)"""
    has = lambda t: {j for d in verdicts(w, t).values() for j in d}
    return has(a) & has(b)


def fix(tag, out):
    def piece(w):
        beads = {(b["sec"], b["id"].split("-")[-1]): b for b in covjudge.beads(w) if b["role"] != "演奏条件"}
        vd = verdicts(w, tag); B = {s["sec"]: s for s in json.loads(line_json(V.graph_of(w, tag)))["segments"]}
        weak, good = {}, {}
        for (sec, bid), d in vd.items():
            if (sec, bid) not in beads:
                continue
            sts = [x.get("status") for x in d.values()]
            if any(s in ("偏弱", "没有", "相反") for s in sts):
                weak.setdefault(sec, []).append((bid, d))
            elif all(s == "说清" for s in sts):
                good.setdefault(sec, []).append((bid, d))
        segs = []
        for sec in sorted(weak):
            if sec not in B:
                continue
            L = [f"### {sec}"] + ([f"【他此刻与整件事的关系】{B[sec].get('relation', '')}"] if BOOST_V in ("2", "3") else []) + ["【现在这版】（json）", json.dumps(B[sec]["items"], ensure_ascii=False), "【接不上的珠子】"]
            for bid, d in weak[sec]:
                why = "；".join(f"{x.get('status')}，{x.get('why', '')}" for x in d.values())
                L.append(f"- {bid}：{beads[(sec, bid)]['text'][:260]}（评委：{why}）")
            if good.get(sec):
                L.append("【已经接得上的珠子】（靠的条目必须保留）")
                L += [f"- {bid}：靠「{'；'.join(str(x.get('items', '')) for x in d.values())}」" for bid, d in good[sec]]
            segs.append("\n".join(L))
        rid = f"bo_{w}_{out}"; e = {}
        print(w, out, "有接不上的珠子的段", {s: len(v) for s, v in sorted(weak.items())}, flush=True)
        if segs:
            msg = FIX.format(NAME=covjudge.NAME[w], SEGS="\n\n".join(segs), GLOSS=gloss_text(w))
            if not evo.done(rid):
                evo.call(rid, msg, model=evo.G6, meta={"stage": "v6-boost"}) if os.environ.get("BOOST_WRITER", "gpt") == "gpt" else evo.call_argon_direct(rid, msg, meta={"stage": "v6-boost"})
            e = V.parse(rid) or {}
            e["segments"] = [s for s in e.get("segments") or [] if s.get("sec") in weak]
        G, _ = build(w, tag, out, e, allow_empty=True)
        print(w, out, "重写了", [s["sec"] for s in e.get("segments") or []], "字数", sum(len(i["text"]) for s in G["segments"] for i in s["items"]), flush=True)
    evo.run_parallel([(w, (lambda w=w: piece(w))) for w in ("op60", "op61")], 2)


def keep(tag, new, out):
    for w in ("op60", "op61"):
        J = common_judges(w, tag, new)
        a, b = seg_score(w, tag, J), seg_score(w, new, J)
        N = {s["sec"]: s for s in json.loads(line_json(V.graph_of(w, new)))["segments"]}
        better = [sec for sec in N if b.get(sec, 0) > a.get(sec, 0)]
        e = {"segments": [{"sec": sec, "items": [{"text": it["text"], "cite": it["cite"]} for it in N[sec]["items"]]} for sec in better]}
        G, _ = build(w, tag, out, e, allow_empty=True)
        print(w, out, "覆盖变好、采用新写法的段", better, f"（{sum(b.get(s, 0) for s in better) - sum(a.get(s, 0) for s in better):+d} 分）",
              "其余沿用", tag, "字数", sum(len(i["text"]) for s in G["segments"] for i in s["items"]), flush=True)


if __name__ == "__main__":
    x = sys.argv[1:]
    {"fix": lambda: fix(x[1], x[2]), "keep": lambda: keep(x[1], x[2], x[3])}[x[0]]()
