"""Bead element roles (user 10-21: "听法 abc 真的有这么互斥吗 你有评定过他吗" — no, and mostly they are not: Op.61 S04's text says
"另一个可以同时听见的层面" yet it got its own letter). r2 opened a new letter at every "另一种/也可以". Roles now:
  主线  — the segment's first listening and its unfolding in time
  同时  — another layer that holds at the same moment (body, mind, another image, another situation)
  替代  — the same sound heard as something else; cannot hold together with alt_of (an element id)
Then every 替代 is audited separately (is it really incompatible with alt_of?); failed ones become 同时.
Elements stay verbatim (from bg_<w>_r2). usage: python beadrole.py label | audit | view"""
import json, sys
from collections import Counter
import beadgraph, evo

W = beadgraph.W
LABEL = ("下面是一段音乐的“珠子”原文，以及从原文逐字摘出的元素（带 id）。请给每个元素标它和这一段主线的关系：\n"
         "- 主线：这一段最先写的那条听感，以及它在段内时间上的展开；\n"
         "- 同时：可以和主线同时成立的另一层——身体感觉、心理、另一个意象、另一个处境。原文说“若把注意力放到……”“另一个可以同时听见的层面”“还有一种……”，"
         "通常是这一类；\n"
         "- 替代：把同一处声音听成另一种东西，和某个元素不能同时成立（例如同一段材料被认作两种不同的来源）。标替代时，alt_of 写它替代的那个元素 id。\n"
         "拿不准时标“同时”。只输出一个 ```json 代码块：{\"E1\": {\"role\": \"主线\"}, \"E7\": {\"role\": \"替代\", \"alt_of\": \"E2\"}, ...}\n\n")
AUDIT = ("下面是一段音乐的“珠子”原文，以及几对元素：每对里后一个被标成前一个的“替代听法”，意思是两者不能同时成立。"
         "请逐对判断：真的不能同时成立（互斥），还是其实可以同时感受到（同时）？只输出一个 ```json 代码块：{\"P1\": \"互斥\", \"P2\": \"同时\", ...}\n\n")


def load(w):
    return json.loads((beadgraph.OUT / f"bg_{w}_r2.json").read_text(encoding="utf-8"))


def view(j, w):
    segs = beadgraph.bead_segments(w)
    md = [f"# {'Op.60' if w == 'op60' else 'Op.61'}｜珠子元素", "",
          "每条都是珠子原文逐字摘出；（小节·种类）。主线 = 这一段先写的听感及其展开；同时 = 可以同时成立的另一层；替代 = 同一处声音的另一种认法，不能同时成立。", ""]
    for s in j["segments"]:
        info = segs.get(s["id"], {}); E = {e["id"]: e for e in s.get("elements") or []}
        md += [f"### {s['id']} · {info.get('bars', s.get('bars'))} · {info.get('title', '')}", ""]
        for role in ("主线", "同时", "替代"):
            es = [e for e in s.get("elements") or [] if e.get("role", "主线") == role]
            if not es:
                continue
            md.append(f"**{role}**")
            for e in es:
                alt = E.get(e.get("alt_of"))
                md.append(f"- （{e.get('bars')}·{e.get('kind')}）{e.get('text')}" + (f"　〔替代：{alt['text'][:16]}…〕" if role == "替代" and alt else ""))
            md.append("")
    return "\n".join(md)


if __name__ == "__main__":
    ph = sys.argv[1]
    if ph == "label":
        jobs = []
        for w in W:
            j = load(w); segs = beadgraph.bead_segments(w)
            for s in j["segments"]:
                rid = f"brole_{w}_{s['id']}"
                msg = LABEL + f"========== 原文 ==========\n{segs[s['id']]['text']}\n\n========== 元素 ==========\n" + "\n".join(f"{e['id']}：{e['text']}" for e in s["elements"])
                if not evo.done(rid):
                    jobs.append((rid, (lambda rid=rid, msg=msg: evo.call(rid, msg, prompt_text=LABEL, model=evo.G56, meta={"stage": "bead_role"}))))
        evo.run_parallel(jobs, 6)
    if ph in ("label", "audit"):
        jobs, pairs = [], {}
        for w in W:
            j = load(w); segs = beadgraph.bead_segments(w)
            for s in j["segments"]:
                lab = evo.parse_json(evo.output(f"brole_{w}_{s['id']}")); E = {e["id"]: e for e in s["elements"]}
                for e in s["elements"]:
                    e.update(lab.get(e["id"], {"role": "同时"}))
                ps = [(e["alt_of"], e["id"]) for e in s["elements"] if e.get("role") == "替代" and e.get("alt_of") in E]
                pairs[(w, s["id"])] = ps
                if ps:
                    rid = f"baudit_{w}_{s['id']}"
                    msg = AUDIT + f"========== 原文 ==========\n{segs[s['id']]['text']}\n\n========== 元素对 ==========\n" + "\n".join(
                        f"P{k + 1}：{E[a]['text']}  ／  {E[b]['text']}" for k, (a, b) in enumerate(ps))
                    if not evo.done(rid):
                        jobs.append((rid, (lambda rid=rid, msg=msg: evo.call(rid, msg, prompt_text=AUDIT, model=evo.G56, meta={"stage": "bead_role_audit"}))))
            (beadgraph.OUT / f"bg_{w}_r3.json").write_text(json.dumps(j, ensure_ascii=False, indent=1), encoding="utf-8")
        evo.run_parallel(jobs, 6)
        for w in W:
            j = json.loads((beadgraph.OUT / f"bg_{w}_r3.json").read_text(encoding="utf-8")); flips = []
            for s in j["segments"]:
                ps = pairs[(w, s["id"])]
                if not ps:
                    continue
                a = evo.parse_json(evo.output(f"baudit_{w}_{s['id']}"))
                for k, (x, y) in enumerate(ps):
                    if a.get(f"P{k + 1}") != "互斥":
                        e = next(e for e in s["elements"] if e["id"] == y); e["role_before_audit"] = "替代"; e["role"] = "同时"; flips.append(f"{s['id']} {y}")
            (beadgraph.OUT / f"bg_{w}_r3.json").write_text(json.dumps(j, ensure_ascii=False, indent=1), encoding="utf-8")
            (beadgraph.OUT / f"bg_{w}_r3_view.md").write_text(view(j, w), encoding="utf-8")
            c = Counter(e.get("role") for s in j["segments"] for e in s["elements"])
            print(w, dict(c), "替代→同时 after audit:", flips, flush=True)
