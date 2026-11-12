"""DAG N03i (11-01, user: "珠子而言也是的 … 你可以继续变好一点"): language pass on the beads, content untouched.
  review : open review (same three steps as N09 v2: read the whole, local issues, cumulative issues with several quotes and a
           boundary), adapted to listening notes; several hearings per segment are intended. ids bl_<w>_<j>_r1 (+gem).
  fix    : the writer re-says only what the review pointed at; every image, feeling, hearing, bar reference stays; no merging,
           no dropping a hearing, no new images. ids blf_<w>.
  check  : per changed bead, two judges: is the listening content the same (images, feelings, the hearings offered, bars)?
           any judge says no -> that bead keeps its previous text. ids blc_<w>_<j>.
Input: beads after N03h (evaluations/beads_clean/<w>.json, else the STRUCT text). Output evaluations/beads_lang/<w>.json + .md.
usage: python bead_lang.py review | fix | check"""
import json, sys
import covjudge, evo, v6fix as V

OUT = evo.ROOT / "evaluations" / "beads_lang"; OUT.mkdir(parents=True, exist_ok=True)
CLEAN = evo.ROOT / "evaluations" / "beads_clean"

REVIEW = """请阅读下面这组中文听感记录。每条（方括号里是编号）写的是肖邦{NAME}某一段听起来像什么、让人想到什么。同一段常常给出几种听法，这是有意的：读者可以从中挑一种进入音乐，不需要拼成一个故事。这些文字会原样给听众看。

请作为第一次读到它的普通中文读者，独立评审它的语言质量，不要预先假定它有哪些毛病。
第一步：从头到尾连续读一遍，注意哪里自然、哪里费劲、读完有没有不舒服或单调的感觉。
第二步：逐处指出真正读起来不通顺、不像人话、别扭或要停下来想一想的表达，引原文，说为什么，给一个更自然的说法（意思、意象、感受都不能变）。没有问题的不用提，不要凑数。
第三步：单独检查全篇的累积效果：某种写法单独看没错、反复出现后让阅读变差的，引多处原文作证，说明为什么连起来才成问题，并划出同类写法在哪些情况下自然或必要，标轻重。
最后打分（1–10），说最影响阅读的是什么。

{TEXT}

只输出 json：
```json
{{"issues": [{{"id": "S01-B1", "quote": "原文", "why": "…", "better": "…"}}], "cumulative": [{{"phenomenon": "…", "evidence": [{{"id": "…", "quote": "…"}}], "effect": "…", "boundary": "…", "severity": "轻微/中等/严重", "suggestion": "…"}}], "score": 0, "main": "…"}}
```"""

FIX = """下面是一组音乐听感记录（每条一颗“珠子”），以及几位读者指出的语言问题（见【读者意见】）。请只改语言：
- 被指出的地方都改，同类毛病一并改；读着顺的地方原样保留。
- 每颗珠子的意象、比喻、感受、给出的几种听法、提到的小节都必须保留：不合并听法，不删掉任何一种听法或意象，不新增原文没有的画面、比喻或解释。
- 字数和原来大致相当；不加编辑说明。
只输出改动了的珠子。

【读者意见】
{ISSUES}

【珠子】
{TEXT}

只输出 json：
```json
{{"beads": [{{"id": "S01-B1", "text": "改好的完整正文"}}]}}
```"""

CHECK = """下面每组是同一颗音乐听感记录（珠子）的原文和改写。改写只该改语言。请逐组判断听感内容是否一致：意象和比喻、感受、给出的几种听法、提到的小节，是否都还在、没有被改掉或加进新的。说法换了、句子顺了不算变化。

{PAIRS}

只输出 json：
```json
{{"items": [{{"id": "S01-B1", "same": "是", "why": "不一致时说出哪里变了"}}]}}
```"""


def current(w):
    base = {b["id"]: b["text"] for b in covjudge.beads(w)}
    f = CLEAN / f"{w}.json"
    if f.exists():
        base.update(json.loads(f.read_text(encoding="utf-8")))
    return base


def text(d):
    return "\n".join(f"[{i}] {t}" for i, t in d.items())


def review():
    jobs = []
    for w in ("op60", "op61"):
        msg = REVIEW.format(NAME=covjudge.NAME[w], TEXT=text(current(w)))
        for j, m in V.JUDGES.items():
            rid = f"bl_{w}_{j}_r1"
            if not evo.done(rid):
                jobs.append((rid, (lambda rid=rid, msg=msg, m=m: evo.call(rid, msg, model=m, meta={"stage": "bead-lang-review"}))))
        rid = f"bl_{w}_gem_r1"
        if not evo.done(rid):
            jobs.append((rid, (lambda rid=rid, msg=msg: evo.call_gemini_direct(rid, msg, meta={"stage": "bead-lang-review"}))))
    evo.run_parallel(jobs, 6)
    for w in ("op60", "op61"):
        for j in ("g6", "g56", "gem"):
            e = V.parse(f"bl_{w}_{j}_r1") or {}
            print(w, j, "分", e.get("score"), "单句", len(e.get("issues") or []), "累积", len(e.get("cumulative") or []), "|", (e.get("main") or "")[:120], flush=True)


def issues(w):
    out = []
    for j in ("g6", "g56", "gem"):
        e = V.parse(f"bl_{w}_{j}_r1") or {}
        out += [f"- [{x.get('id')}]「{x.get('quote')}」——{x.get('why')}（可以考虑：{x.get('better')}）" for x in e.get("issues") or []]
        out += [f"- 全篇累积（{c.get('severity')}）：{c.get('phenomenon')}——{c.get('effect')}；哪些可以保留：{c.get('boundary')}；建议：{c.get('suggestion')}" for c in e.get("cumulative") or []]
    return "\n".join(out)


def fix():
    jobs = [(f"blf_{w}", (lambda w=w: evo.done(f"blf_{w}") or evo.call_argon_direct(f"blf_{w}", FIX.format(ISSUES=issues(w), TEXT=text(current(w))), meta={"stage": "bead-lang-fix"})))
            for w in ("op60", "op61")]
    evo.run_parallel(jobs, 2)
    for w in ("op60", "op61"):
        n = len((V.parse(f"blf_{w}") or {}).get("beads") or []); print(w, "改写的珠子", n, flush=True)


def check():
    for w in ("op60", "op61"):
        old = current(w); new = dict(old)
        for x in (V.parse(f"blf_{w}") or {}).get("beads") or []:
            if x.get("id") in old and x.get("text"):
                new[x["id"]] = x["text"]
        changed = [i for i in old if new[i] != old[i]]
        pairs = "\n\n".join(f"### {i}\n【原文】{old[i]}\n【改写】{new[i]}" for i in changed)
        jobs = [(f"blc_{w}_{j}", (lambda w=w, j=j, m=m: evo.call(f"blc_{w}_{j}", CHECK.format(PAIRS=pairs), model=m, meta={"stage": "bead-lang-check"})))
                for j, m in V.JUDGES.items() if changed and not evo.done(f"blc_{w}_{j}")]
        evo.run_parallel(jobs, 2)
        bad = {}
        for j in V.JUDGES:
            for x in (V.parse(f"blc_{w}_{j}") or {}).get("items") or []:
                if str(x.get("same", "")).startswith("否"):
                    bad.setdefault(x.get("id"), []).append(f"{j}: {x.get('why', '')}")
        md = [f"# {w}｜珠子语言改写", ""]
        for i in changed:
            ok = i not in bad
            md += [f"## {i} {'采用' if ok else '退回（' + '；'.join(bad[i]) + '）'}", f"- 原文：{old[i]}", f"- 改写：{new[i]}", ""]
            if not ok:
                new[i] = old[i]
        (OUT / f"{w}.json").write_text(json.dumps(new, ensure_ascii=False, indent=1), encoding="utf-8")
        (OUT / f"{w}.md").write_text("\n".join(md), encoding="utf-8")
        print(w, "改写", len(changed), "颗，内容核对不过退回", len(bad), "颗", flush=True)


if __name__ == "__main__":
    {"review": review, "fix": fix, "check": check}[sys.argv[1]]()
