"""Wording pass over the winning beam path (user 10-23: the main AI smell is monotone sentence patterns and abstract,
monotone words). The line was written section by section, so no call saw the whole text's repetitions: "越……越……" 4x,
"依赖中的片刻自在" 3x, "多了一分信任" 2x, "因为……" openers, banned words (代价、安稳-type). This pass may change wording only;
every change is logged with the defect it fixes and a check that no cause/step was lost or added.
usage: python polish.py <T> <path_id> <tag>  -> evaluations/beam/<T>/polish_<tag>.json"""
import json, re, sys
import evo, node2b, seq

BAN = "站稳 立足 挺直 安顿 承受 承担 敞开 托住 悬着 落定 归属 边界 限度 代价 空缺 位置 意义 回应 辨认".split()
P = ("下面是一条讲解视频旁白“线”，共 14 段，每段两三句，讲一个人在肖邦《船歌》里经历的一件事：每段说明他此刻为什么会这样，理由来自前面的经历。"
     "它是一段一段分开写成的，所以放在一起读时，句式和用词重复、单调。请只改说法，让全篇读起来像一个人在自然地讲这件事：\n"
     "1. 每段的意思、理由和它指向的前面哪段经历都不能变；不加新的心理动作、新的理由、新的事件，也不删掉任何一层因果。\n"
     "2. 句式要有变化：不要每段都以“他”开头，不要反复用“因为……”“这一次……”起句；“越……越……”全篇最多留两处。\n"
     "3. 同一个说法不要在几段里反复出现（例如“依赖中的片刻自在”“多了一分信任”），换成那一段里更具体的说法。\n"
     "4. 少用抽象的词（依靠、安稳、掌控、约束、踏实、牵挂这一类），能换成他具体在想什么、怕什么、想要什么就换；"
     "不用这些词：" + "、".join(BAN) + "。\n"
     "5. 每段仍是两三句、不超过 80 字，普通人一遍能懂。\n"
     "6. 只改有毛病的地方，没毛病的句子原样保留。\n\n"
     "每处改动都要记录：改了哪段、原句、新句、修的是什么毛病、有没有丢掉或多出意思（说明理由）。\n"
     "最后只输出一个 ```json 代码块：\n"
     '{"lines": ["第1段的新文本", "…（14 项）"], "changes": [{"seg": 1, "before": "…", "after": "…", "defect": "…", "meaning_check": "…"}]}\n\n'
     "# 原文\n\n{TEXT}")


def stats(lines):
    t = "".join(lines)
    return {"越越": len(re.findall(r"越[^。；，]{0,12}越", t)), "禁用词": [w for w in BAN if w in t],
            "以他开头": sum(l.startswith("他") for l in lines), "因为": t.count("因为"), "最长": max(map(len, lines))}


if __name__ == "__main__":
    T, pid, tag = sys.argv[1:4]
    p = next(x for x in json.loads((evo.ROOT / "evaluations" / "beam" / T / "S14.json").read_text(encoding="utf-8"))["kept"] if x["id"] == pid)
    lines = [st["line"] for st in p["steps"]]
    text = "\n".join(f"第{i + 1}段（{'–'.join(map(str, seq.bars(st['sec'])))}小节）：{st['line']}" for i, st in enumerate(p["steps"]))
    rid = f"pol{T}_{tag}"
    if not evo.done(rid):
        node2b.job(rid, P.replace("{TEXT}", text), {"stage": "polish"}, w="g6")[1]()
    r = seq.parse(evo.output(rid)) or {}
    new = r.get("lines") or []
    assert len(new) == 14, f"got {len(new)} lines"
    out = {"path": pid, "before": lines, "after": new, "changes": r.get("changes"), "stats_before": stats(lines), "stats_after": stats(new)}
    (evo.ROOT / "evaluations" / "beam" / T / f"polish_{tag}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("before", out["stats_before"], "\nafter ", out["stats_after"], flush=True)
