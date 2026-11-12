"""Final product from a synth3 path (PLAN_20261026.md step 6, 10-27).
F  (g6): per segment the 还说不清 / 正在面对 / 没在想 label, light edits only (pronoun / repeat / joining; every edit listed),
    three Center candidates written last (one plain sentence, never previewing an answer);
V  (g56): fidelity of every edited item against the path's original text (no new reason, not more abstract) + Center pick;
R  (g6, g56): non-regression against the 10-25 package-3 line: per segment, where the new line explains less;
then render txt (package-3 layout: Center, segment header with label, bullets, ← arrows to earlier causes) and a bead annex.
usage: THREAD_ROUTE=gpt3s THREAD_ROUTE_G56=mimic python finalize3.py <T> <work>  -> evaluations/synth/<T>_<work>/final.*"""
import json, sys
from pathlib import Path
import covjudge, draft10, evo, node2b

PKG3 = {"op60": Path("C:/Users/zuoyi/Documents/Codex/2026-10-25/n-n/outputs/Op60_船歌_Thread.txt"),
        "op61": Path("C:/Users/zuoyi/Documents/Codex/2026-10-25/n-n/outputs/Op61_幻想波兰舞曲_Thread.txt")}
F = """下面是为肖邦{NAME}逐段建立好的一条 Thread（每段的解释都摘自独立写成的稿子，括号里是它依赖的前面经历的编号）。

【Thread】
{THREAD}

请做三件事：
1. 每一段标出他和这件事的关系：还说不清 / 正在面对 / 没在想（开头可以还说不清；没在想的段属于同一件事，只是这时他不在想它）。
2. 把每一条压短，让整条读起来简洁、连得上。只许用原文里的词句：可以删去重复、铺陈和与前一段重复的话，可以调换原文句子的顺序，可以补清楚指代、加一个连接词；不许换成原文没有的概括说法（例如“延续需要”“安顿”“分量”），不许加新的理由，原文里每一步原因都要保留。每条写成两部分：feel 是他此刻的感受（一句），why 是为什么（一两句）。每一处删改写进 edits。
3. 全部读完以后，写 3 个 Center 候选：用一句普通人能懂的话，说出这整件事是什么（不是列表，不是预告答案，不用抽象词）。

只输出 json：
```json
{{"sections": [{{"sec": "S01", "label": "还说不清", "items": [{{"id": "S01-1", "feel": "……", "why": "……", "edits": ["……"]}}]}}], "centers": ["……", "……", "……"]}}
```"""
V = """下面是一条 Thread 的修改前后对照，以及 3 个 Center 候选。

请检查：
1. 每一条压短后的文字是否只用了原文的词句（删去重复和铺陈、调换顺序、补指代、加连接词）？有没有加新理由、漏掉原文里的某一步原因、或者换成了比原文更抽象的说法？逐条列出有问题的，写清漏了或加了什么。
2. 3 个 Center 里哪个最好：一句话说出这整件事、普通人能懂、不预告答案、和每一段都对得上。

{PAIRS}

【Center 候选】
{CENTERS}

只输出 json：
```json
{{"bad": [{{"id": "S03-1", "why": "……"}}], "center": 1, "center_why": "……"}}
```"""
R = """下面是肖邦{NAME}的两版 Thread（解释每段感受为什么会这样出现）：旧版是上一轮的成品，新版是这一轮的成品。
请逐段比较：新版有没有把旧版已经解释清楚的东西丢掉，或者退回到更空泛的说法（例如“更在乎了”“有了新的分量”）？新版哪里比旧版更好？
不要因为字多或故事完整就判好；看谁更说得清“为什么此刻会这样”。最后给总判断。

【旧版】
{OLD}

【新版】
{NEW}

只输出 json：
```json
{{"worse": [{{"sec": "S04", "lost": "……"}}], "better": [{{"sec": "S05", "gain": "……"}}], "verdict": "新版不差于旧版 / 新版有实质退步", "why": "……"}}
```"""


def load(T, w, fill=True):
    d = evo.ROOT / "evaluations" / "synth" / f"{T}_{w}"
    st = {x["id"]: json.loads((d / f"{x['id']}.json").read_text(encoding="utf-8")) for x in draft10.segs(w) if (d / f"{x['id']}.json").exists()}
    for sec, v in st.items():                        # fill3.py results: counted apart, marked 补
        f = d / f"fill_{sec}.json"
        if fill and f.exists():
            for c in json.loads(f.read_text(encoding="utf-8")).get("accepted") or []:
                v.setdefault("chosen", []).append({"text": f"感受：{c['feel']} 为什么：{c['why']}", "depends": c.get("depends") or [],
                                                   "explains": c.get("explains") or [], "added": True})
                fate = v.setdefault("pick", {}).setdefault("fate", {})
                for b in c.get("explains") or []:
                    if not str(fate.get(b, "没有解释")).startswith("第"):
                        fate[b] = "补：" + c["feel"][:30]
    return d, st


def thread_text(w, st):
    hsec = {h["id"]: s for s, v in st.items() for h in v.get("hist", [])}
    out = []
    for x in draft10.segs(w):
        v = st.get(x["id"]) or {}
        out.append(f"### {x['id']}（{x['start']}–{x['end']}小节）")
        for i, c in enumerate(v.get("chosen") or [], 1):
            dep = [f"{h}（{hsec.get(h, '?')}）" for h in c.get("depends") or []]
            out.append(f"{x['id']}-{i}：{c['text']}" + ("（补缺）" if c.get("added") else "") + (f"　［依赖：{'、'.join(dep)}］" if dep else ""))
        for h in v.get("hist", []):
            out.append(f"（这一段确立的经历 {h['id']}：{h['text']}）")
    return "\n".join(out)


def coverage(w, st):
    rows = {"explained": [], "filled": [], "compatible": [], "alternative": [], "doubtful": [], "gap": []}
    for b in covjudge.beads(w):
        if b["role"] == "演奏条件":
            continue
        v = st.get(b["sec"]) or {}
        f = (v.get("pick") or {}).get("fate", {}).get(b["id"], "没有解释")
        # the check (model b) overrules the pick's own claim: a bead it lists as unexplained is a gap or a doubtful bead
        un = {u["id"]: u for u in (v.get("check") or {}).get("unexplained") or []}
        if b["id"] in un and not f.startswith("补"):
            why = un[b["id"]].get("why", "")
            f = ("听感存疑：" if "存疑" in why else "没有解释（检查：" + why + "）：") + (un[b["id"]].get("note") or "")[:60]
        k = "explained" if f.startswith("第") else "filled" if f.startswith("补") else "doubtful" if f.startswith("听感存疑") else "compatible" if f.startswith("独立") else "alternative" if "另一种" in f else "gap"
        rows[k].append({"id": b["id"], "fate": f})
    return rows


def call(rid, msg, mdl):
    for r in (rid, rid + "_x"):
        if not evo.done(r):
            node2b.job(r, msg, {"stage": "final3"}, w=mdl)[1]()
        try:
            return evo.parse_json(evo.output(r))
        except Exception:
            continue
    raise RuntimeError(rid)


def run(T, w):
    d, st = load(T, w); name = covjudge.NAME[w]; th = thread_text(w, st)
    f = call(f"fn{T}_{w}_F", F.format(NAME=name, THREAD=th), "g6")
    orig = {f"{s}-{i}": c["text"] for s, v in st.items() for i, c in enumerate(v.get("chosen") or [], 1)}
    for sx in f["sections"]:
        for it in sx["items"]:
            it["text"] = f"感受：{it.get('feel', '')} 为什么：{it.get('why', '')}" if it.get("feel") else it.get("text", "")
    pairs = "\n".join(f"{it['id']}\n  原文：{orig.get(it['id'], '（无对应原文）')}\n  压短后：{it['text']}"
                      for s in f["sections"] for it in s["items"])
    v = call(f"fn{T}_{w}_V", V.format(PAIRS=pairs, CENTERS="\n".join(f"{i}. {c}" for i, c in enumerate(f["centers"], 1))), "g56")
    bad = {b["id"] for b in v.get("bad") or []}
    for s in f["sections"]:
        for it in s["items"]:
            if it["id"] in bad and it["id"] in orig:
                it["text"] = orig[it["id"]]; it["reverted"] = True       # a failed edit falls back to the path's own words
                it.pop("feel", None); it.pop("why", None)
    center = f["centers"][max(0, min(len(f["centers"]), int(v.get("center") or 1)) - 1)]
    new_txt = render(w, st, f, center, with_annex=False)
    old = PKG3[w].read_text(encoding="utf-8-sig") if PKG3[w].exists() else ""
    reg = {}
    if old:                                   # 10-27: the two regression judges run at the same time
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(2) as ex:
            fs = {j: ex.submit(call, f"fn{T}_{w}_R_{j}", R.format(NAME=name, OLD=old, NEW=new_txt), j) for j in ("g6", "g56")}
            reg = {j: f.result() for j, f in fs.items()}
    cov = coverage(w, st)
    final = {"T": T, "work": w, "center": center, "center_why": v.get("center_why"), "sections": f["sections"],
             "fidelity_bad": v.get("bad"), "regression": reg, "coverage": {k: len(x) for k, x in cov.items()}, "beads": cov}
    (d / "final.json").write_text(json.dumps(final, ensure_ascii=False, indent=1), encoding="utf-8")
    (d / "final.txt").write_text(render(w, st, f, center, with_annex=True, cov=cov), encoding="utf-8")
    print(w, "coverage", final["coverage"], "| regression", {j: r.get("verdict") for j, r in reg.items()}, flush=True)


def render(w, st, f, center, with_annex, cov=None):
    hsec = {h["id"]: s for s, v in st.items() for h in v.get("hist", [])}
    segs = {x["id"]: x for x in draft10.segs(w)}
    out = ["肖邦" + covjudge.NAME[w], f"Center：{center}", ""]
    for s in f["sections"]:
        x = segs.get(s["sec"]); v = st.get(s["sec"]) or {}
        out.append(f"{s['sec']} ｜ {x['start']}–{x['end']}小节 ｜ {s.get('label', '')}" if x else s["sec"])
        out.append("")
        for i, it in enumerate(s["items"], 1):
            c0 = (v.get("chosen") or [])[i - 1] if i <= len(v.get("chosen") or []) else {}
            mark = "（补）" if c0.get("added") else ""
            if it.get("feel"):
                out += [f"• {mark}{it['feel']}", f"  → {it['why']}"]
            else:
                t = it["text"].replace("感受：", "", 1)
                a, _, b = t.partition(" 为什么：")
                out += [f"• {mark}{a.strip()}"] + ([f"  → {b.strip()}"] if b else [])
            c = (v.get("chosen") or [{}] * i)[i - 1] if i <= len(v.get("chosen") or []) else {}
            for h in c.get("depends") or []:
                src = hsec.get(h)
                txt = next((x["text"] for vv in st.values() for x in vv.get("hist", []) if x["id"] == h), "")
                if src and src != s["sec"]:
                    out.append(f"  ← {segs[src]['start']}–{segs[src]['end']}「{txt[:40]}」")
        out.append("")
    if with_annex and cov:
        n = sum(len(x) for x in cov.values())
        out += ["———", f"听感去处（{n} 颗，不含演奏条件）：解释了 {len(cov['explained'])}，补缺解释 {len(cov['filled'])}，相容保留 {len(cov['compatible'])}，"
                f"另一种听法 {len(cov['alternative'])}，听感存疑 {len(cov['doubtful'])}，没有解释 {len(cov['gap'])}"]
        out += [f"  {r['id']}：{r['fate']}" for k in ("gap", "filled", "doubtful", "alternative", "compatible") for r in cov[k]]
        failed = [(s, v.get("check") or {}) for s, v in st.items() if not (v.get("check") or {}).get("pass")]
        out += ["", f"逐段检查未通过：{len(failed)} 段（选文仍取自池中原句，检查意见如下）"]
        for s, ck in failed:
            out.append(f"  {s}：{ck.get('reason', '')}")
    return "\n".join(out)


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2])
