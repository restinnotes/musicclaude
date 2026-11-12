"""10-30 evening (user: "和珠子一起搞一篇试试"). One article per piece from the new-form line and the bead graph: per segment, his
reason in plain words (from the line) and the listeners' experience as VERBATIM excerpts of the beads in 「」 (cut, never
reworded); one experience explained once; another hearing marked 也可以听成. The script checks every 「」 excerpt against the
bead text and reports any that are not verbatim.
ids: es_<w>_<line>.  usage: python v6essay.py <line tag>  -> evaluations/v6fix/文章_<w>_<line>.md"""
import re, sys
import covjudge, evo, v6fix as V
from v6flow import render

P = """下面是肖邦{NAME}的两份材料：
一、一条“线”：一个人在这首曲子里经历的一件事，按段写成条目，说他每段此刻为什么会这样（〔〕里是引用的前面段落）；
二、另一批人听每一段写下的听感记录（珠子），写此刻听到、感到的样子。

请把两份合成一篇给普通读者看的短文，按原来的段落走，每段用小标题写小节号。要求：
1. 原因用线里的意思、他自己的平常话说；听到、感到的样子，一律直接摘珠子原文，放在「」里——可以截取一句或半句，但不改字、不拼接；
2. 同一份体验只说一次：珠子已经写出来的感受，线那边不要再用别的话说一遍，只说他为什么会这样；
3. 每颗珠子摘它最有代表性的一句或半句（不要整段照抄）；“另一种理解”的珠子写成“也可以听成「……」”；
   摘录要和他的原因接起来：读者要看得出，正因为他此刻这样，这一段听起来才像「……」——用平常的连接说出来，不要只是把摘录排在原因后面罗列；
4. 不新增线和珠子里都没有的事；不写总结句和哲理句；
5. 尽量短：全文不超过 {N} 个字；每段两三句到四五句；读起来要像一篇连贯的文章，段与段接得上，前面的事在后面需要时直接提起，不用箭头和标签。

【线】
{LINE}

【珠子】（B 后是编号，［］里是角色，（）里是小节）
{BEADS}

直接输出文章（markdown），不要别的说明。"""


def check(w, text):
    src = "".join(b["text"] for b in covjudge.beads(w))
    norm = lambda s: re.sub(r"\s", "", s)
    S = norm(src)
    qs = re.findall(r"「([^」]+)」", text)
    bad = [q for q in qs if norm(q).strip("。，；、") not in S]
    return len(qs), bad


def main(T):
    def piece(w):
        W = "Op.60" if w == "op60" else "Op.61"
        rid = f"es2_{w}_{T}"
        if not evo.done(rid):
            evo.call(rid, P.format(NAME=covjudge.NAME[w], LINE=render(V.graph_of(w, T), W), BEADS=V.beads(w), N=2400 if w == "op60" else 2600),
                     model=evo.G6, meta={"stage": "v6-essay"})
        text = (evo.output(rid) or "").strip()
        n, bad = check(w, text)
        note = f"\n\n---\n（核对：「」摘录 {n} 处，不是珠子原文的 {len(bad)} 处" + ("：" + "；".join(bad[:10]) if bad else "") + "）\n"
        (V.OUT / f"文章2_{w}_{T}.md").write_text(text + note, encoding="utf-8")
        print(w, T, "字数", len(re.sub(r"\s", "", text)), "摘录", n, "非原文", len(bad), flush=True)
    evo.run_parallel([(w, (lambda w=w: piece(w))) for w in ("op60", "op61")], 2)


if __name__ == "__main__":
    main(sys.argv[1])
