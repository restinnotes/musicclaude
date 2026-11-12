"""Node 2 round D11 = P0+ v2 (10-23). Coverage of the D10 pool (covjudge.py): Op.60 44/50, Op.61 40/53 strict, a little above
the old corrected drafts, but the gaps are one kind: memory / loss / time passing (Op.61 旧歌, 记忆里挪舞步, "如果当时……",
具体生活记忆; Op.60 握紧, "能维持多久", 想起童年) and the self stepping back (Op.60 93–102). Every draft family, N8 and B0
included, explains everything as present-tense wanting / getting / not enough.
Two generic rule changes, same cells as D10 otherwise:
  rule 1 names other sources of a feeling besides wanting/getting (time, something larger than oneself, body/situation);
  rule 5 says "no invented backstory" does not mean every feeling is present-tense: a feeling can itself carry memory or loss.
These sources come from the gap analysis on these two pieces, so generalisation needs a new piece later.
ids: d11{c|o}{6|56}_<work>_r<j>.  usage: python draft11.py"""
import draft10 as d, evo

d.RULES = (d.RULES
           .replace("一段里可以有几种相容的感受，不必只挑最主要的一种。\n",
                    "一段里可以有几种相容的感受，不必只挑最主要的一种。感受的来源很多：想要什么、得到了什么、还缺什么只是其中一种；"
                    "它也可能来自时间（正在过去、已经回不来、像在回忆什么），来自比自己更大的东西（自己暂时退到后面），"
                    "或者来自身体和处境本身。每一段都想一想，这里的感受来自哪里。\n")
           .replace("5. 开头不要交代人物的过去、性格、习惯，也不要提前说出主题；任何一段都不要预告后面会怎样。\n",
                    "5. 开头不要交代人物的经历、性格、习惯，也不要提前说出主题；任何一段都不要预告后面会怎样。"
                    "不编前史，不等于感受只能发生在当下：此刻的感受本身可以带着回忆或失去的性质，这不需要编出具体发生过什么。\n"))
d.ONE = d.ONE.replace(d.ONE.split("\n按上面给定的分段")[0], d.RULES.rstrip("\n"))
assert "来自时间" in d.RULES and "不编前史" in d.RULES and "来自时间" in d.ONE

if __name__ == "__main__":
    jobs = []
    for w in d.W:
        for m in ("6", "56"):
            mdl = "g6" if m == "6" else "g56"
            for j in d.R:
                for kind, fn in (("c", d.chain), ("o", d.one)):
                    name = f"d11{kind}{m}_{w}_r{j}"
                    if not (d.OUT / f"{name}.json").exists():
                        jobs.append((name, lambda name=name, w=w, mdl=mdl, fn=fn: fn(name, w, mdl)))
    evo.run_parallel(jobs, 24)
