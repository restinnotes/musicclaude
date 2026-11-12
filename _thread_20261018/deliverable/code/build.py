"""Assemble the Thread deliverables from model outputs (verbatim; code only orders and joins)."""
import json, re
from collections import defaultdict
import thr, common
import step3_inner_outer as s3
import step5_final as s5

D = thr.ROOT / "deliverable"; (D / "data").mkdir(parents=True, exist_ok=True)
LABEL = {t["id"]: t["label"] for t in s3.SEL}
ORDER = ["TA", "TB", "TC"]
CMP = {c: thr.load("compare", c) for c in ("C1", "C2")}
SRC = {"TA": [("C1", "TH1"), ("C2", "TH1")], "TB": [("C2", "TH2")], "TC": [("C1", "TH2"), ("C2", "TH3")]}


def seg_start(m):
    s = m.get("segment")
    if s in thr.SEGS:
        return int(thr.SEGS[s][0].split("-")[0])
    n = re.findall(r"\d+", m.get("where") or "")
    return int(n[0]) if n else 999


def final(tid):
    inner = thr.load("inner_final", tid) or thr.load("merge", tid)
    outer = thr.load("outer_final", tid) or thr.load("curate_final", tid) or {}
    return inner, outer


def thread_header(tid):
    out = []
    for c, th in SRC[tid]:
        t = next(x for x in CMP[c]["threads"] if x["id"] == th)
        out.append(f"> **{t['name']}**  \n> 核心关系：{t.get('core_relation')}")
    return "\n>\n".join(out)


def why_piece(tid):
    c, th = SRC[tid][0]
    return next(x for x in CMP[c]["threads"] if x["id"] == th).get("why_this_piece", "")


def reader():
    L = ["# 肖邦《船歌》Op.60 · Thread 候选与 Inner / Outer\n",
         "这首曲子里持续发生的事情，经过三入口、三十余路独立寻找与两轮独立比较，收敛为三条可以同时存在的线。它们不是同一个故事的三章，也不是要选出唯一正确的一条：同一段音乐可以同时在三条线上。",
         "每条线先给出它是什么、为什么是这首曲子；然后按音乐时间排列关键时刻——「听到」是音乐事件，「仍然活着」是此前已经发生、此刻仍在起作用的经历，正文是 Inner（这一刻能被感到的那层理解）；Outer 是让它在具体人类处境里显现的瞬间，只放在少数时刻。每个时刻的 Inner 只依靠此前已经发生的音乐（曲终回看除外）。",
         "所有文字为模型原文（GPT‑6 Thinking / GPT‑5.6 Thinking，max；Outer 候选另含 Gemini 3.8 Flash），由代码按时间拼接，没有人工改写。Bead 作为当前体验依据，未被改动。\n"]
    for tid in ORDER:
        inner, outer = final(tid)
        L.append(f"\n---\n\n## 线 {ORDER.index(tid)+1}｜{LABEL[tid]}\n")
        L.append(thread_header(tid) + "\n")
        L.append(f"**为什么是这首曲子**：{why_piece(tid)}\n")
        by_m = defaultdict(list)
        for s in outer.get("selected", []):
            by_m[s.get("moment")].append(s["text"])
        for m in sorted(inner["moments"], key=seg_start):
            L.append(f"### {m.get('where')}" + (f"（{m.get('kind')}）" if m.get("kind") else ""))
            L.append(f"*听到*：{m.get('heard')}  \n*仍然活着*：{m.get('alive')}\n")
            L.append(m.get("inner", "").strip() + "\n")
            for o in by_m.get(m["id"], []):
                L.append(f"> **Outer**　{o}\n")
        L.append(f"### 曲终回看\n\n{inner.get('retrospective', '').strip()}\n")
        if inner.get("not_touched"):
            L.append("**这条线不去解释、让它保持独立的段落**：" + "；".join(f"{x.get('segment')}：{x.get('why')}" for x in inner["not_touched"]) + "\n")
    return "\n".join(L)


def key_moments():
    """Same music position, three threads side by side (verbatim Inner)."""
    rows = defaultdict(dict)
    for tid in ORDER:
        inner, outer = final(tid)
        for m in inner["moments"]:
            s = m.get("segment")
            if s in thr.SEGS:
                rows[s][tid] = m
    L = ["# 关键时刻对照：同一段音乐，三条线各自听见了什么\n",
         "只列至少两条线都在此处有 Inner 的段落。三条线在同一时刻并存，不互相取代。\n"]
    for s in thr.SEGS:
        if len(rows[s]) < 2:
            continue
        L.append(f"\n## {s} · 第 {thr.mm(s)} 小节（{thr.SEGS[s][1]}）\n")
        for tid in ORDER:
            m = rows[s].get(tid)
            if m:
                L.append(f"**{LABEL[tid]}**（{m.get('where')}）  \n{m.get('inner', '').strip()}\n")
    return "\n".join(L)


if __name__ == "__main__":
    (D / "C_Thread阅读稿.md").write_text(reader(), encoding="utf-8")
    (D / "C_关键时刻对照.md").write_text(key_moments(), encoding="utf-8")
    for tid in ORDER:
        inner, outer = final(tid)
        (D / "data" / f"{tid}_final.json").write_text(json.dumps({"thread": LABEL[tid], "inner": inner, "outer": outer}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("ok")
