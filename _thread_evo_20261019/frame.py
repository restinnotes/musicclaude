"""Starting-frame ranking for path assembly (10-28). P4a/P4c lost to package 3 mainly on the line's centre, and the centre was
fixed at S01: the picker took the candidate most authors wrote (Op.61 M4, 4 authors) over a one-author one whose premise
the later beads keep pointing to. Assembly may see beads; this step reads the whole piece's beads once and ranks S01's
whole-segment candidates by how well their starting point lets the later segments' feelings follow and be explained,
author counts hidden. The ranking is only a hint to the S01 pick.
ids: fr_<work>.  usage: THREAD_ROUTE=gpt3s python frame.py <pool-tag>  -> evaluations/pool/<tag>/<work>/frame.json"""
import json, sys
import covjudge, evo, node2b, pool

Q = """下面是肖邦{NAME}全曲各段的听感记录（另一批人听这首曲子时写下的原文），以及第一段（第{A}–{B}小节）的若干条候选解释。
一条 Thread 从第一段开始，逐段解释他此刻为什么会这样感受；第一段确立的处境和原因，会成为后面每一段的起点。

请判断：哪几条候选的起点（它说他此刻处在什么处境、为什么这样感受），最能让后面各段的听感顺着发展下来、被一条前后连贯的理由解释？
- 只看全曲听感记录本身，不要预设这首曲子“应该”讲什么；
- 起点要能解释第一段自己的听感（包括写成比喻的那些：比喻是在描述感受）；
- 一个起点如果只是听起来深刻，却和后面多段听感的方向对不上，就排在后面。
选出前 3 名，每条写一两句理由，并写出它和后面哪几段的听感最对得上。

【全曲听感记录】
{BEADS}

【第一段候选】
{CANDS}

只输出 json：
```json
{{"top": [{{"id": "M14", "why": "……", "fits": ["S04", "S09"]}}]}}
```"""


def rid(tag, w):
    return f"fr_{w}" if tag == "P27t" else f"fr{tag}_{w}"


def main(tag):
    jobs = []
    for w in ("op60", "op61"):
        beads = "\n".join(f"- {b['id']}（第{b['measures']}小节）［{b['role']}］{b['text']}" for b in covjudge.beads(w) if b["role"] != "演奏条件")
        ms = [m for m in json.loads((pool.OUT / tag / w / "S01.json").read_text(encoding="utf-8"))["mechs"] if "#t" not in m["rep"]["src"] and "#c" not in m["rep"]["src"]]
        cands = "\n".join(f"{m['id']}：感受：{m['rep']['feel']} 为什么：{m['rep']['thread']}" for m in ms)
        s = next(x for x in __import__("draft10").segs(w) if x["id"] == "S01")
        if not evo.done(rid(tag, w)):
            jobs.append(node2b.job(rid(tag, w), Q.format(NAME=covjudge.NAME[w], A=s["start"], B=s["end"], BEADS=beads, CANDS=cands), {"stage": "frame"}, w="g6"))
    evo.run_parallel(jobs, 2)
    for w in ("op60", "op61"):
        top = evo.parse_json(evo.output(rid(tag, w)))["top"]
        (pool.OUT / tag / w / "frame.json").write_text(json.dumps({"top": top}, ensure_ascii=False, indent=1), encoding="utf-8")
        print(w, "起点排名:", [(t["id"], t.get("fits")) for t in top], flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
