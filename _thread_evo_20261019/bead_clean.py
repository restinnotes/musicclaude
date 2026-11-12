"""DAG N03h (10-31, user: "正文的编辑句确实要去掉"): strip editorial meta-language from bead texts — sentences that talk about
sources, materials, whether a hearing is supported, whether hearings should be joined into one story, "not the only story" —
and nothing else. Piece-agnostic, all beads of a work in one GPT-6 call; the script then checks every changed bead: the new
text must come from the old by deletions plus at most a few joining characters, otherwise the bead is kept as it was.
ids bc_<w> -> evaluations/beads_clean/<w>.json {bead id: text} (+ .md with every change). Beads are never rewritten otherwise.
usage: python bead_clean.py"""
import difflib, json
import covjudge, evo

OUT = evo.ROOT / "evaluations" / "beads_clean"; OUT.mkdir(parents=True, exist_ok=True)
P = """下面是一组音乐听感记录（每条是一颗“珠子”：一段音乐听起来像什么、让人想到什么）。它们会原样给听众看。
其中有些句子或分句不是在写听感，而是在说明材料和写作判断，例如：提到原稿、材料、资料，说某种听法有没有依据、来自哪里，说几种听法要不要拼成同一个故事，说“这不是唯一的答案/唯一确定的故事”之类。
请只删去这类句子或分句。删去以后，每一句都必须仍是完整、通顺的句子；如果接不上或句子残缺，就在接缝处补或改最少的几个字（不超过 6 个字）。其余文字一个字都不要动：比喻、感受、语气、“也可以听成”这类引出另一种听法的话都保留，它们是听感本身。没有这类句子的珠子不要输出。

{BEADS}

只输出 json：
```json
{{"beads": [{{"id": "S01-B1", "removed": "被删去的原文", "text": "删改后的完整正文"}}]}}
```"""


CHECK = """下面几段文字是从更长的原文里删去了一些句子后得到的。请逐句检查：删改之后，有没有句子变得不完整、读不通（例如句子只剩半截、缺了谓语）？
有的话，只在那一处补上或改动最少的字（不超过 6 个字），让句子完整；完整的不要动。没有问题的段落不要输出。

{BEADS}

只输出 json：
```json
{{"beads": [{{"id": "S01-B1", "text": "修好后的完整正文"}}]}}
```"""


def added_chars(old, new):
    return sum(j2 - j1 for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes() if op in ("insert", "replace"))


if __name__ == "__main__":
    B = {w: covjudge.beads(w) for w in ("op60", "op61")}
    evo.run_parallel([(w, (lambda w=w: evo.call(f"bc2_{w}", P.format(BEADS="\n".join(f"[{b['id']}] {b['text']}" for b in B[w])), model=evo.G6,
                                                 meta={"stage": "bead_clean"}))) for w in B], 2)
    for w, bs in B.items():
        old = {b["id"]: b["text"] for b in bs}; new = dict(old); md = [f"# {w}｜珠子去编辑句", ""]
        for x in (evo.parse_json(evo.output(f"bc2_{w}") or "{}") or {}).get("beads") or []:
            i, t = x.get("id"), x.get("text") or ""
            if i not in old or not t or t == old[i]:
                continue
            a = added_chars(old[i], t); ok = a <= 6 and len(t) < len(old[i])
            md += [f"## {i} {'采用' if ok else '不采用（新增 ' + str(a) + ' 字）'}", f"- 删去：{x.get('removed', '')}", f"- 原文：{old[i]}", f"- 现在：{t}", ""]
            if ok:
                new[i] = t
        changed = [i for i in old if new[i] != old[i]]
        if changed:   # second pass: are the edited sentences still complete? (10-31: S04-B2 was left as a fragment)
            r = evo.call(f"bcc_{w}", CHECK.format(BEADS="\n".join(f"[{i}] {new[i]}" for i in changed)), model=evo.G6, meta={"stage": "bead_clean_check"})
            for x in (evo.parse_json(r or "{}") or {}).get("beads") or []:
                i, t = x.get("id"), x.get("text") or ""
                if i in changed and t and t != new[i] and added_chars(new[i], t) <= 6 and added_chars(old[i], t) <= 6:
                    md += [f"## {i} 复查补字", f"- 补后：{t}", ""]; new[i] = t
        (OUT / f"{w}.json").write_text(json.dumps(new, ensure_ascii=False, indent=1), encoding="utf-8")
        (OUT / f"{w}.md").write_text("\n".join(md), encoding="utf-8")
        print(w, "改动的珠子", sum(new[i] != old[i] for i in old), "/", len(old), flush=True)
