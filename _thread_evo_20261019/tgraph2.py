"""Thread graph v2 — built around the P0 concepts (user 10-21: Center etc. must be kept; v1 dropped Center).
  center : {matters: 什么对他重要, hard: 是什么使它难以安顿}  — must NOT preview the route or the final answer
  nodes  : {id, type, text, seg, certainty, kind?}
           types — Inner: 处境 所求 理由 代价 恐惧; History: 快乐 回报 困难 需要; plus 办法 发现 机制 状态 问题
           kind (on 发现): 分清 办法的限度 选择的代价 满足照出未满足 知道更多反而更尖锐 其他
  edges  : {from, to, rel, note}; rel — Connection (P0 verbs): 说明 限制 动摇 提供理由; plus 唤起 失效 改写 冲突 用来抵挡
  segments: {bars, center_touch: 这一段怎样触及 Center（一句）, center_move: 触及|分化|加深|松动,
             state:[ids], new:[ids], history:[earlier ids still acting], outer: (optional, only if the original has it)}
Checks: Center previews an answer?; every state has a Connection edge from an earlier node (why-now); every segment has
center_touch; history present after S01; accumulation kinds used; far edges; orphans; formula sentences.
ids: tg2_<t>_r<j> -> evaluations/tgraph2/<id>.json/.md"""
import json, re, sys
from collections import defaultdict
import arts, evo, fmt4, node2b, plain, stateinc, structured

OUT = evo.ROOT / "evaluations" / "tgraph2"
P = ("请把下面的原稿拆成一张“Thread 图”：一堆离散的元素，以及它们之间的关系。之后视频怎么呈现、要提取什么，都从这张图里取，所以它要完整、准确、每个元素都具体。"
     "后面附有原稿的骨架，作为不能丢的清单。这张图要按原稿提示词里的几个核心概念来组织：\n"
     "【Center】说清楚共同的困扰：什么对他重要（matters），又是什么使它难以安顿（hard）。它不预告发展的路线和最后的回答——不要写他最后怎样了。\n"
     "【History】到此刻已经实际获得的根据：哪些快乐发生过、哪些期待有过回报、哪些困难已经显露、哪些需要仍在。\n"
     "【Connection】把关系实际说出来：这一份经历如何说明、限制、动摇另一份经历，或者给当前的回应提供理由。\n"
     "【Inner】把他的处境、所求、理由和代价理解清楚，并用人话说清楚。\n"
     "【理解的积累】例如：原先挤在一起的两个要求逐渐被分清；一种确实给过人东西的办法显出了它不能处理的部分；某个看似合理的选择需要付出另一种代价；"
     "一次充分的满足使仍未满足的东西更明确；人知道了更多，困扰却可能因此更尖锐。\n\n"
     "输出：\n"
     "1. center：{matters, hard}。\n"
     "2. nodes：每个元素一句具体的人话。type 取：处境、所求、理由、代价、恐惧（Inner）；快乐、回报、困难、需要（History）；办法、发现、机制、状态、问题。"
     "seg 写它出现的段落；certainty 写“清楚”或“模糊”——原稿里他还说不清的，标模糊，不要替他说清。发现节点加 kind："
     "分清、办法的限度、选择的代价、满足照出未满足、知道更多反而更尖锐、其他。机制节点用人话点出他为什么会这样反应，不用术语。\n"
     "3. edges：rel 优先用 Connection 的词：说明、限制、动摇、提供理由；也可用：唤起、失效、改写、冲突、用来抵挡。note 一句话说清这条关系（可省略）。"
     "要连出原稿写到的远处关系：较早的快乐、回报、困难、办法，怎样在后面被唤起、失效、被改写。\n"
     "4. segments：每段 center_touch（一句：这一段怎样触及 Center）、center_move（触及／分化／加深／松动）、state（此刻他的状态，节点 id）、"
     "new（这一段新出现的节点）、history（此刻仍在起作用的更早节点）、outer（可选：原稿里有的可感处境，一句；没有就省略，不要编）。"
     "每个 state 节点都必须至少有一条从更早节点指向它的 Connection——这就是“为什么此刻”。\n"
     + stateinc.RULES +
     "只输出一个 ```json 代码块：{\"center\": {\"matters\": \"…\", \"hard\": \"…\"}, \"nodes\": [{\"id\": \"N1\", \"type\": \"所求\", \"text\": \"…\", \"seg\": \"{FIRST}\", \"certainty\": \"模糊\"}], "
     "\"edges\": [{\"from\": \"N1\", \"to\": \"N2\", \"rel\": \"提供理由\", \"note\": \"…\"}], \"segments\": [{\"bars\": \"{FIRST}\", \"center_touch\": \"…\", \"center_move\": \"触及\", "
     "\"state\": [\"N2\"], \"new\": [\"N1\", \"N2\"], \"history\": []}]}\n"
     "segments 按顺序覆盖：{BARS}。\n\n")
CONN = ("说明", "限制", "动摇", "提供理由", "唤起", "失效", "改写", "冲突", "用来抵挡")
HIST = ("快乐", "回报", "困难", "需要")


def check(j, w):
    bars = structured.bars(w); pos = {b: i for i, b in enumerate(bars)}
    N = {n["id"]: n for n in j["nodes"]}; inc = defaultdict(list)
    for e in j["edges"]:
        inc[e["to"]].append(e)
    segs = j["segments"]
    def reaches_earlier(x, i, hops=2):   # why-now may run state <- same-segment mechanism <- earlier node
        for e in inc[x]:
            p = pos.get(N.get(e["from"], {}).get("seg"), 99)
            if p < i or (hops > 1 and p == i and reaches_earlier(e["from"], i, hops - 1)):
                return True
        return False
    no_why = [s["bars"] for i, s in enumerate(segs) if i > 0 and not any(reaches_earlier(x, i) for x in s["state"])]
    far = sum(1 for e in j["edges"] if e["from"] in N and e["to"] in N and pos.get(N[e["to"]]["seg"], 0) - pos.get(N[e["from"]]["seg"], 0) >= 2)
    linked = {e["from"] for e in j["edges"]} | {e["to"] for e in j["edges"]}
    c = j.get("center", {}); ctext = (c.get("matters", "") + c.get("hard", "")) if isinstance(c, dict) else str(c)
    txt = " ".join(n["text"] for n in j["nodes"])
    return {"segments_valid": [s["bars"].replace("-", "–") for s in segs] == bars, "nodes": len(N), "edges": len(j["edges"]),
            "center_previews": bool(re.search(r"最终|最后|终于|走下去|学会|接受了|放下了", ctext)),
            "segments_without_center_touch": [s["bars"] for s in segs if not s.get("center_touch")],
            "segments_without_why": no_why, "segments_without_history": [s["bars"] for i, s in enumerate(segs) if i > 0 and not s.get("history")],
            "conn_edges_P0_verbs": sum(e.get("rel") in ("说明", "限制", "动摇", "提供理由") for e in j["edges"]),
            "history_nodes": sum(n["type"] in HIST for n in N.values()),
            "accumulation": {k: sum(n.get("kind") == k for n in N.values()) for k in ("分清", "办法的限度", "选择的代价", "满足照出未满足", "知道更多反而更尖锐")},
            "far_edges": far, "orphans": len([n for n in N if n not in linked]), "fuzzy": sum(n.get("certainty") == "模糊" for n in N.values()),
            "formula": sum(len(re.findall(v, txt)) for v in fmt4.PAT.values())}


def view(j, title):
    N = {n["id"]: n for n in j["nodes"]}; inc = defaultdict(list)
    for e in j["edges"]:
        inc[e["to"]].append(e)
    c = j["center"]
    md = [f"# {title}", "", f"**Center｜什么对他重要：**{c.get('matters')}", f"**Center｜什么使它难以安顿：**{c.get('hard')}", ""]
    for s in j["segments"]:
        md += [f"### {s['bars']}", "", f"◇ Center（{s.get('center_move')}）：{s.get('center_touch')}", ""]
        for sid in s["state"]:
            n = N.get(sid, {}); md.append(f"**此刻｜{n.get('text')}**" + ("（还模糊）" if n.get("certainty") == "模糊" else ""))
            for e in inc[sid]:
                src = N.get(e["from"], {})
                md.append(f"  ← {e['rel']}：［{src.get('type')}｜{src.get('seg')}］{src.get('text')}" + (f"　—— {e['note']}" if e.get("note") else ""))
        for x in [x for x in s.get("new", []) if x not in s["state"]]:
            n = N.get(x, {})
            md.append(f"- ［{n.get('type')}{'｜' + n['kind'] if n.get('kind') else ''}］{n.get('text')}" + ("（还模糊）" if n.get("certainty") == "模糊" else ""))
        if s.get("history"):
            md.append("- History：" + "；".join(f"［{N.get(h, {}).get('type')}｜{N.get(h, {}).get('seg')}］{N.get(h, {}).get('text')}" for h in s["history"][:4]))
        if s.get("outer"):
            md.append(f"- Outer：{s['outer']}")
        md.append("")
    return "\n".join(md)


def save(rid, w):
    j = evo.parse_json(evo.output(rid)); c = check(j, w); j["check"] = c
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{rid}.json").write_text(json.dumps(j, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / f"{rid}.md").write_text(view(j, rid), encoding="utf-8")
    print(rid, json.dumps(c, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    jobs = []
    for w, ts in plain.THREADS.items():
        for t in ts:
            sk = (evo.ROOT / "evaluations" / "skeleton" / f"{t}.json").read_text(encoding="utf-8")
            msg = stateinc.fill(P, w) + "========== 原稿 ==========\n" + arts.clean(evo.output(t)) + "\n\n========== 骨架 ==========\n" + sk
            for j in (1, 2):
                if not evo.done(f"tg2_{t}_r{j}"):
                    jobs.append(node2b.job(f"tg2_{t}_r{j}", msg, {"stage": "tgraph2", "thread": t}))
    evo.run_parallel(jobs, 4)
    for w, ts in plain.THREADS.items():
        for t in ts:
            for j in (1, 2):
                if evo.done(f"tg2_{t}_r{j}"):
                    save(f"tg2_{t}_r{j}", w)
