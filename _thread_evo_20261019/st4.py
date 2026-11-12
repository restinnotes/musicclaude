"""Structured Thread v4 (user 10-21: the show layer is too descriptive; why-now must be visible, but not via stiff
because/so sentences; don't over-compress — the structure serves later steps, so e.g. which concrete histories led to
what can live in fields). Source: the original line + its skeleton (not a compressed version).
ids: st4_<t>_r<j> -> evaluations/st4/<id>.json/.md"""
import json, re, sys
import arts, evo, fmt4, node2b, plain, stateinc, structured

OUT = evo.ROOT / "evaluations" / "st4"
P = ("请把下面的原稿整理成结构化 Thread，供之后做视频使用。这是结构化数据，不是成稿：不需要压得很短，但每个字段都必须有实在内容、不写空话。"
     "后面附有原稿的骨架，作为不能丢的清单。\n"
     "每段字段：\n"
     "- now：他此刻的心理（一两句，具体：他在想什么、怕什么、想要什么）。不能比原稿更确定：原稿里他还说不清的，这里也保持说不清。\n"
     "- why_now：这是最重要的字段——为什么偏偏此刻会这样。用一两句人话把其中的道理讲出来，让读者一读就明白“原来如此”："
     "讲清前面得到、相信、试过或发现的某件事，怎样在此刻变成了这种感受或选择。不要写成“因为……所以……”的公式句，也不要只是换个说法描述状态。\n"
     "- history：此刻仍在起作用的前史，1–3 条；每条 {\"from\": \"段落\", \"what\": \"那时具体发生了什么（他得到、相信、试过、发现了什么）\", "
     "\"now_effect\": \"它此刻怎样影响他\"}。只列真正起作用的，不要罗列；第一段可以为空。\n"
     "- revises：（可选）这一段改写了之前的哪个认识：原以为……，现在……\n"
     "- open：这一段留给后面的问题（一句）。\n"
     "- weight：1–3，这一段新发生的事有多少。\n"
     "全篇字段：center（整篇围绕的那件事，一句人话）、arc（这件事从头到尾怎样变，两三句）。\n"
     + stateinc.RULES +
     "只输出一个 ```json 代码块：{\"center\": \"…\", \"arc\": \"…\", \"segments\": [{\"bars\": \"{FIRST}\", \"now\": \"…\", \"why_now\": \"…\", "
     "\"history\": [{\"from\": \"…\", \"what\": \"…\", \"now_effect\": \"…\"}], \"revises\": \"\", \"open\": \"…\", \"weight\": 2}]}\n"
     "segments 按顺序覆盖：{BARS}。\n\n")


def render(j, title):
    md = [f"# {title}", "", f"**这件事：**{j['center']}", "", f"**走向：**{j['arc']}", ""]
    for s in j["segments"]:
        md += [f"### {s['bars']}", "", f"**此刻：**{s['now']}", "", f"**为什么此刻：**{s['why_now']}"]
        for h in s.get("history") or []:
            md.append(f"- 前史（{h.get('from')}）：{h.get('what')} → 此刻：{h.get('now_effect')}")
        if s.get("revises"):
            md.append(f"- ↺ {s['revises']}")
        if s.get("open"):
            md.append(f"- 留下的问题：{s['open']}")
        md.append("")
    return "\n".join(md)


def save(rid, w):
    j = evo.parse_json(evo.output(rid)); got = [s["bars"].replace("-", "–").replace("—", "–") for s in j["segments"]]
    txt = " ".join(s["now"] + s["why_now"] for s in j["segments"])
    j.update(work=w, source=rid, segments_valid=got == structured.bars(w),
             formula=sum(len(re.findall(v, txt)) for v in fmt4.PAT.values()), because_so=len(re.findall(r"因为[^。]{0,40}所以", txt)))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{rid}.json").write_text(json.dumps(j, ensure_ascii=False, indent=1), encoding="utf-8")
    md = render(j, rid); (OUT / f"{rid}.md").write_text(md, encoding="utf-8")
    print(rid, "ok" if j["segments_valid"] else "SEG MISMATCH", "formula", j["formula"], "因为…所以", j["because_so"],
          "history", sum(len(s.get("history") or []) for s in j["segments"]), "chars", len(md), flush=True)


if __name__ == "__main__":
    jobs = []
    for w, ts in plain.THREADS.items():
        for t in ts:
            sk = (evo.ROOT / "evaluations" / "skeleton" / f"{t}.json").read_text(encoding="utf-8")
            msg = stateinc.fill(P, w) + "========== 原稿 ==========\n" + arts.clean(evo.output(t)) + "\n\n========== 骨架 ==========\n" + sk
            for j in (1, 2):
                if not evo.done(f"st4_{t}_r{j}"):
                    jobs.append(node2b.job(f"st4_{t}_r{j}", msg, {"stage": "st4", "thread": t}))
    evo.run_parallel(jobs, 4)
    for w, ts in plain.THREADS.items():
        for t in ts:
            for j in (1, 2):
                if evo.done(f"st4_{t}_r{j}"):
                    save(f"st4_{t}_r{j}", w)
