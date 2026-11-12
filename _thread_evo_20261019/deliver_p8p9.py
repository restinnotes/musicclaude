"""10-28 evening: the user reads the current best lines. P8 (T0 + sequential bead-aware repair) and P9 (same, no T0) per
segment, then the beads once (package 3, verbatim), plus the judges' verdicts. No model calls; labelled, not anonymised.
usage: python deliver_p8p9.py -> deliver_20261028/半成品_P8P9加珠子_Op60_Op61.md"""
import json
import covjudge, draft10, evo

S = evo.ROOT / "evaluations" / "seq8"
OUT = evo.ROOT / "deliver_20261028" / "半成品_P8P9加珠子_Op60_Op61.md"
HEAD = """# 半成品：两版线 + 珠子（10-28 晚）

两版都是逐段往下写：每段看着这一段的珠子和各篇独立稿的解释，写出“他此刻为什么会这样”，并写出这一段新确立的变化，后面的段必须接在上面。
写稿（独立稿）从头到尾没看过珠子。每段写完都由另一位评委核对：有没有编前史、有没有把音乐当原因、递进成不成立、不看珠子能不能读懂；不合格的退改一次。

- **P9（不用底稿）**：只用独立稿的解释池和珠子，Center 是全曲写完后按这条线回头写的。少了接线这一步，每部作品约省 100 次调用。
- **P8（有底稿）**：多给了一条事先接好的线（P4d）每段原来的解释作参考。Op.60 的 Center 用 P4d 的；Op.61 的 Center 写完后回头写。

## 评委怎么看（匿名、随机顺序，两位评委：gpt-6 / 5.6）

| | 主线盲评（不给珠子） | 珠子对应（给珠子） | 整首对照包3（问“丢没丢包3 说清的东西”） |
|---|---|---|---|
| Op.60 | gpt-6：P8 > P9 > 包3；5.6：P9 > 包3 > P8 | 两位都是包3 第一；主体验说清 P8 13–14、P9 13–14、包3 13 段 | P8、P9 各两位都判“实质退步” |
| Op.61 | gpt-6：P8 > 包3 > P9；5.6：P8 > P9 > 包3（P9 的“为什么此刻”第一）；另一轮 P8 两位都排在包3 前面 | gpt-6：包3 > P9 > P8；5.6：P9 > 包3 > P8；三版主体验都说清 13 段，5.6 判包3 S04 写反 | P8、P9 各两位都判“实质退步” |

评委的分歧：盲评批评包3 把“真切相伴”“对方怎样回应”这类关系事实写得太实；整首对照却认为我们的版本丢了包3 的几处骨架——
Op.60 的“对方心意未定、两人的以后不由他一个人决定”和“独自也能快乐 → 发现对方和共同时间本身有价值 → 从索求转向感受”；
Op.61 的“曾珍惜的生活回不来了”（时间不可逆、对方缺席）。我们的版本多写成了“留不留得住、有没有着落”。

"""


def body(rows, sec):
    out = []
    for x in rows.get(sec, {}).get("edit", {}).get("items") or []:
        if "text" in x:
            out.append(f"- {'→ ' if x.get('follows') else ''}{x['text']}")
        else:
            out += [f"- {x.get('feel', '')}", f"  → {x.get('why', '')}"]
    return out or ["（没有）"]


def center(tag, w):
    f = S / f"P{tag}_{w}.txt"
    return f.read_text(encoding="utf-8").split("\n")[1].replace("Center：", "", 1) if f.exists() else "（还没写）"


def main(p9_61="（还在评）", p9_61r="（还在评）"):
    out = [HEAD.replace("{P9_61}", p9_61).replace("{P9_61R}", p9_61r)]
    for w in ("op60", "op61"):
        r8, r9 = (json.loads((S / f"P{t}_{w}.json").read_text(encoding="utf-8")) for t in ("8", "9"))
        bs = covjudge.beads(w)
        out += [f"## 肖邦{covjudge.NAME[w]}", "", f"**P9 的 Center**：{center('9', w)}", "", f"**P8 的 Center**：{center('8', w)}", ""]
        for s in draft10.segs(w):
            sec = s["id"]
            out += [f"### {sec} ｜ {s['start']}–{s['end']} 小节", "", "**P9**", ""] + body(r9, sec) + ["", "**P8**", ""] + body(r8, sec) + ["", "**珠子**", ""]
            out += [f"- **{b['id'].split('-')[-1]}**［{b['role']}］（{b['measures']} 小节）{b['text']}" for b in bs if b["sec"] == sec]
            out.append("")
    OUT.write_text("\n".join(out), encoding="utf-8")
    print(OUT, len("\n".join(out)), "字")


if __name__ == "__main__":
    import sys
    main(*sys.argv[1:3])
