"""Thread as a graph (user 10-21: structured = discrete elements with relations, like the mechanism arrows; makes
later presentation and extraction easy). Source: original line + skeleton.
  nodes: {id, type, text, seg, certainty}; types: 经历 认识 愿望 恐惧 办法 发现 机制 状态 问题
  edges: {from, to, rel, note}; rels: 导致 使成为可能 阻碍 改写 唤起 冲突 用来抵挡 失效 部分回答
  segments: {bars, state:[ids], new:[ids], active_history:[ids]}
Checks: every segment's state has an incoming edge (why-now present); long-range edges; orphans; formula sentences.
View: per segment, state nodes with their incoming arrows (rel + source + source segment).
ids: tg_<t>_r<j> -> evaluations/tgraph/<id>.json/.md"""
import json, re, sys
from collections import defaultdict
import arts, evo, fmt4, node2b, plain, stateinc, structured

OUT = evo.ROOT / "evaluations" / "tgraph"
TYPES = "经历、认识、愿望、恐惧、办法、发现、机制、状态、问题"
RELS = "导致、使成为可能、阻碍、改写、唤起、冲突、用来抵挡、失效、部分回答"
P = ("请把下面的原稿拆成一张“Thread 图”：一堆离散的元素，以及它们之间的关系。之后视频怎么呈现、要提取什么，都从这张图里取，所以它要完整、准确、每个元素都具体。"
     "后面附有原稿的骨架，作为不能丢的清单。\n"
     f"1. nodes：每个元素一句具体的人话（他经历了什么、相信什么、想要什么、怕什么、用了什么办法、发现了什么、背后是什么心理机制、此刻处于什么状态、留下什么问题）。"
     f"type 取：{TYPES}。seg 写它出现的段落。certainty 写“清楚”或“模糊”——原稿里他还说不清的，就标模糊，不要替他说清。"
     "机制节点用人话点出心理机制本身（他为什么会这样反应），不要用术语。\n"
     f"2. edges：元素之间的关系，rel 取：{RELS}。note 用一句话说清这条关系具体是怎么回事（可省略）。"
     "要连出原稿写到的远处关系：较早段落的经历、认识或办法，怎样在后面的段落被唤起、失效、被改写。\n"
     "3. segments：每段列出 state（此刻他的状态，节点 id）、new（这一段新出现的节点）、active_history（此刻仍在起作用的更早节点）。"
     "每个 state 节点都必须至少有一条从更早节点指向它的边——这就是“为什么此刻”。\n"
     + stateinc.RULES +
     "只输出一个 ```json 代码块：{\"center\": \"…\", \"nodes\": [{\"id\": \"N1\", \"type\": \"经历\", \"text\": \"…\", \"seg\": \"{FIRST}\", \"certainty\": \"清楚\"}], "
     "\"edges\": [{\"from\": \"N1\", \"to\": \"N2\", \"rel\": \"导致\", \"note\": \"…\"}], \"segments\": [{\"bars\": \"{FIRST}\", \"state\": [\"N2\"], \"new\": [\"N1\", \"N2\"], \"active_history\": []}]}\n"
     "segments 按顺序覆盖：{BARS}。\n\n")


def check(j, w):
    bars = structured.bars(w); pos = {b: i for i, b in enumerate(bars)}
    N = {n["id"]: n for n in j["nodes"]}; inc = defaultdict(list)
    for e in j["edges"]:
        inc[e["to"]].append(e)
    seg_ok = [s["bars"].replace("-", "–") for s in j["segments"]] == bars
    no_why = [s["bars"] for i, s in enumerate(j["segments"]) if i > 0 and not any(
        pos.get(N.get(e["from"], {}).get("seg"), 99) <= i and e["from"] not in s["state"] for x in s["state"] for e in inc[x])]
    far = sum(1 for e in j["edges"] if e["from"] in N and e["to"] in N and pos.get(N[e["to"]]["seg"], 0) - pos.get(N[e["from"]]["seg"], 0) >= 2)
    linked = {e["from"] for e in j["edges"]} | {e["to"] for e in j["edges"]}
    txt = " ".join(n["text"] for n in j["nodes"])
    return {"segments_valid": seg_ok, "nodes": len(N), "edges": len(j["edges"]), "far_edges": far, "orphans": [n for n in N if n not in linked],
            "segments_without_why": no_why, "fuzzy": sum(n.get("certainty") == "模糊" for n in N.values()),
            "formula": sum(len(re.findall(v, txt)) for v in fmt4.PAT.values()),
            "types": {t: sum(n["type"] == t for n in N.values()) for t in TYPES.split("、")}}


def view(j, title):
    N = {n["id"]: n for n in j["nodes"]}; inc = defaultdict(list)
    for e in j["edges"]:
        inc[e["to"]].append(e)
    md = [f"# {title}", "", f"**这件事：**{j['center']}", ""]
    for s in j["segments"]:
        md += [f"### {s['bars']}", ""]
        for sid in s["state"]:
            n = N.get(sid, {}); md.append(f"**此刻｜{n.get('text')}**" + ("（还模糊）" if n.get("certainty") == "模糊" else ""))
            for e in inc[sid]:
                src = N.get(e["from"], {})
                md.append(f"  ← {e['rel']}：［{src.get('type')}｜{src.get('seg')}］{src.get('text')}" + (f"　—— {e['note']}" if e.get("note") else ""))
        others = [x for x in s.get("new", []) if x not in s["state"]]
        for x in others:
            n = N.get(x, {})
            outs = [e for e in j["edges"] if e["from"] == x]
            md.append(f"- ［{n.get('type')}］{n.get('text')}" + ("（还模糊）" if n.get("certainty") == "模糊" else "")
                      + "".join(f"\n    → {e['rel']}：{N.get(e['to'], {}).get('text')}" for e in outs[:2]))
        md.append("")
    return "\n".join(md)


def save(rid, w):
    j = evo.parse_json(evo.output(rid)); c = check(j, w); j["check"] = c
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{rid}.json").write_text(json.dumps(j, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / f"{rid}.md").write_text(view(j, rid), encoding="utf-8")
    print(rid, {k: v for k, v in c.items() if k != "types"}, flush=True)


if __name__ == "__main__":
    jobs = []
    for w, ts in plain.THREADS.items():
        for t in ts:
            sk = (evo.ROOT / "evaluations" / "skeleton" / f"{t}.json").read_text(encoding="utf-8")
            msg = stateinc.fill(P, w) + "========== 原稿 ==========\n" + arts.clean(evo.output(t)) + "\n\n========== 骨架 ==========\n" + sk
            for j in (1, 2):
                if not evo.done(f"tg_{t}_r{j}"):
                    jobs.append(node2b.job(f"tg_{t}_r{j}", msg, {"stage": "tgraph", "thread": t}))
    evo.run_parallel(jobs, 4)
    for w, ts in plain.THREADS.items():
        for t in ts:
            for j in (1, 2):
                if evo.done(f"tg_{t}_r{j}"):
                    save(f"tg_{t}_r{j}", w)
