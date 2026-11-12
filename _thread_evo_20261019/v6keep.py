"""10-31 guard for the language pass (user: "不要丢了西瓜捡了芝麻"): a polished line must say the same things as its base.
Piece-agnostic, three steps:
  check  <base> <tag>        : both judges compare base vs polished segment by segment: 保住 / 丢了 / 加了 / 改了, with the items
                               and a reason (kp_<w>_<j>_<tag>) -> keep_<tag>.json {w: {sec: [notes...]}} (flagged by ANY judge,
                               "both" lists those flagged by both).
  redo   <base> <tag> <out>  : the writer (Gemini, or gpt-6 with HUMAN_WRITER=gpt) re-says only the flagged segments, with the judges' notes and the base text
                               (kr_<w>_<out>); unflagged segments are copied from <tag>.
  revert <base> <tag> <out>  : segments flagged by BOTH judges in keep_<tag>.json go back to the base text.
KEEP_SEV=1 check: judges also weigh each flag 要紧/细微 (ids kq_*); only 要紧 counts as flagged.
usage: python v6keep.py check b0 h3 | redo b0 h3 h3r | revert b0 h3r h3k"""
import json, sys
import covjudge, evo, v6fix as V
from v6gen import build, gloss_text
from v6human import line_json, WRITE3, INNER

CHECK = """下面是肖邦{NAME}的一条“线”的两个版本：原版，和润色后的一版。润色只该改说法，不该改意思。Center（贯穿全曲的那个问题）：{CENTER}

请逐段对照，判断润色版的这一段：
- 保住：原段每条的意思都还在；没有加原文没有的事件、感受、因果；可能的没说成确定，相关的没说成因果；Center 的词没被改窄或换成另一件事；
- 丢了：原段某条独有的意思没了；
- 加了：多了原段没有的事件、感受或因果；
- 改了：意思变了（方向反了、程度明显变了、Center 的某部分被改窄）。
换了说法、合并了重复的意思、删掉了不带信息的否定半句，都算保住。只看意思，不看文笔。不是“保住”的，写出是哪几条（用润色版的编号），一句话说清原来是什么、现在成了什么。

{SEV}
{PAIRS}

只输出 json：
```json
{{"sections": [{{"sec": "S01", "label": "保住", {SEVF}"items": [], "why": "……"}}]}}
```"""

# 10-31: the plain check flags nearly every segment (把“亲近”说成“呆在一起”也算改了), so reverting on it undoes the whole
# language pass. KEEP_SEV=1 adds a weight: only 要紧 (a reader would understand his experience differently) counts.
SEV = """每个不是“保住”的段，再标轻重 sev：
- 要紧：读者会因此对他这段经历理解不同——Center 的某部分被改窄或换成另一件事、某条独有的意思丢了、方向或因果反了、加了一件原来没有的事；
- 细微：措辞上的小偏差，抽象说法换成了具体说法但没改窄，读者对这段经历的理解基本不变。
"""

REDO = """下面是肖邦{NAME}的一条“线”里的几段。每段有原版和一版润色稿。润色稿读起来更像人话，但核对的编辑发现它丢了、加了或改了原版的意思（见每段的【编辑意见】）。
请把这几段重新润色：意思以原版为准，一点不能变；说法照下面的要求改成平常话。

{RULES}

{SEGS}

【Center 各部分指什么】
{GLOSS}

只输出这几段改好的 json（每条的 cite 照原版填）：
```json
{{"segments": [{{"sec": "S01", "items": [{{"text": "……", "cite": []}}]}}]}}
```"""


def pairs(A, B):
    a = {s["sec"]: s for s in A["segments"]}
    out = []
    for s in B["segments"]:
        o = a.get(s["sec"])
        out.append(f"### {s['sec']}\n【原版】\n" + ("\n".join(f"- {it['text']}" for it in o["items"]) if o else "（无）")
                   + "\n【润色版】\n" + "\n".join(f"- [{it['id']}] {it['text']}" for it in s["items"]))
    return "\n\n".join(out)


PFX = "kq" if __import__("os").environ.get("KEEP_SEV") else "kp"


def check(base, tag):
    jobs = []
    for w in ("op60", "op61"):
        A, B = V.graph_of(w, base), V.graph_of(w, tag)
        for j, m in V.JUDGES.items():
            rid = f"{PFX}_{w}_{j}_{tag}"
            if not evo.done(rid):
                jobs.append((rid, (lambda rid=rid, m=m, w=w, A=A, B=B: evo.call(rid, CHECK.format(NAME=covjudge.NAME[w], CENTER=A["center"], PAIRS=pairs(A, B),
                                                                              SEV=SEV if PFX == "kq" else "", SEVF='"sev": "要紧", ' if PFX == "kq" else ""),
                                                                              model=m, meta={"stage": "v6-keep"}))))
    evo.run_parallel(jobs, 4)
    res, md = {}, [f"# 润色有没有丢意思：{tag} 对 {base}", ""]
    for w in ("op60", "op61"):
        fl = {}
        for j in V.JUDGES:
            S = (V.parse(f"{PFX}_{w}_{j}_{tag}") or {}).get("sections") or []
            bad = [s for s in S if s.get("label") and s.get("label") != "保住" and (PFX == "kp" or s.get("sev") != "细微")]
            print(tag, w, j, "段", len(S), "不是保住", len(bad), [f"{s.get('sec')}{s.get('label')}" for s in bad], flush=True)
            md += [f"## {w} · {'gpt-6' if j == 'g6' else '5.6'}", ""] + [f"- {s.get('sec')}：{s.get('label')}{'（' + s['sev'] + '）' if s.get('sev') else ''} {s.get('items') or ''}　{s.get('why', '')}" for s in S] + [""]
            for s in bad:
                fl.setdefault(s["sec"], []).append({"judge": j, "label": s["label"], "items": s.get("items") or [], "why": s.get("why", "")})
        res[w] = {"any": fl, "both": [sec for sec, xs in fl.items() if len({x["judge"] for x in xs}) == len(V.JUDGES)]}
        print(tag, w, "任一位判有问题的段", sorted(fl), "两位都判", res[w]["both"], flush=True)
    (V.OUT / f"keep_{tag}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    (V.OUT / f"keep_{tag}.md").write_text("\n".join(md), encoding="utf-8")


def rules():
    s = WRITE3.split("改法（每一条都按这几点过一遍）：")[1].split("另一位编辑找出的问题")[0]
    return "改法：" + s.replace("{EXTRA}", "").replace("{{", "{").replace("}}", "}")


def redo(base, tag, out):
    K = json.loads((V.OUT / f"keep_{tag}.json").read_text(encoding="utf-8"))
    def piece(w):
        fl = K[w]["any"]
        A, B = V.graph_of(w, base), V.graph_of(w, tag)
        a = {s["sec"]: s for s in json.loads(line_json(A))["segments"]}
        b = {s["sec"]: s for s in B["segments"]}
        rid = f"kr_{w}_{out}"
        if fl and not evo.done(rid):
            segs = "\n\n".join(f"### {sec}\n【原版】（json）\n{json.dumps(a[sec]['items'], ensure_ascii=False)}\n【润色稿】\n"
                               + "\n".join(f"- [{it['id']}] {it['text']}" for it in b[sec]["items"])
                               + "\n【编辑意见】\n" + "\n".join(f"- {x['label']} {x['items']}：{x['why']}" for x in xs)
                               for sec, xs in fl.items() if sec in a and sec in b)
            msg = REDO.format(NAME=covjudge.NAME[w], RULES=rules(), SEGS=segs, GLOSS=gloss_text(w))
            if __import__("os").environ.get("HUMAN_WRITER") == "gpt":
                evo.call(rid, msg, model=evo.G6, meta={"stage": "v6-keep-redo"})
            elif __import__("os").environ.get("HUMAN_WRITER") == "argon":
                evo.call_argon_direct(rid, msg, meta={"stage": "v6-keep-redo"})
            else:
                evo.call_gemini_direct(rid, msg, meta={"stage": "v6-keep-redo"})
        e = (V.parse(rid) or {}) if fl else {}
        e["segments"] = [s for s in e.get("segments") or [] if s.get("sec") in fl]
        G, kept = build(w, tag, out, e, allow_empty=True)
        print(w, out, "重改段", sorted(fl), "字数", sum(len(i["text"]) for s in G["segments"] for i in s["items"]), flush=True)
    evo.run_parallel([(w, (lambda w=w: piece(w))) for w in ("op60", "op61")], 2)


def revert(base, tag, out):
    K = json.loads((V.OUT / f"keep_{tag}.json").read_text(encoding="utf-8"))
    for w in ("op60", "op61"):
        a = {s["sec"]: s for s in json.loads(line_json(V.graph_of(w, base)))["segments"]}
        e = {"segments": [{"sec": sec, "items": [{"text": it["text"], "cite": it["cite"]} for it in a[sec]["items"]]} for sec in K[w]["both"] if sec in a]}
        G, kept = build(w, tag, out, e, allow_empty=True)
        print(w, out, "还原成底版的段", K[w]["both"], "字数", sum(len(i["text"]) for s in G["segments"] for i in s["items"]), flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    {"check": lambda: check(a[1], a[2]), "redo": lambda: redo(a[1], a[2], a[3]), "revert": lambda: revert(a[1], a[2], a[3])}[a[0]]()
