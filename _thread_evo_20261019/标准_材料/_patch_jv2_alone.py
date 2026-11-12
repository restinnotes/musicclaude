"""one-off patch (11-02): v6alone JV=2 prompts aligned to 标准.md; e2e_open goal 1/2 wording aligned, ids eo2_."""
from pathlib import Path
H = Path(__file__).resolve().parent.parent

p = H / "v6alone.py"; t = p.read_text(encoding="utf-8")
anchor = "\n\ndef graph(w, tag):"
assert anchor in t
ADD = '''

# 11-02 JV=2 (标准.md): "why now" is felt, not causal sentences; continuation / immersion can stand; no 原因/描写 split
# (it pushed lines toward psychological analysis); per segment also: repeats an earlier conclusion? label matches content?
import os as _os
JV = _os.environ.get("JV", "1")
ALONE2 = """下面是一条“线”：一个人在肖邦{NAME}里经历的一件事，按音乐段落分段，每段几条要点。只给你这条线，没有别的材料。
每段标题后的括号是他此刻和整件事的关系（没在想 / 还说不清 / 正在面对）；〔〕是这句接着前面哪一段的哪一条；方括号里是条目编号。

这条线应该自己就成立：有逻辑、有时序、内在有发展，各段不是各说各的；看得出他此刻为什么这样，但不需要用“因为……所以……”交代——前面经历过的、已经明白的，成为后面的理由，后面的经历又让前面的意味更清楚。推动它的是他自己前面的经历，不是音乐里发生了什么，也不是新编的事件。一段只是延续、沉浸或暂时没在想，也可以成立。

请逐段判断，每项写一句理由：
1. self：只读这条线，这一段他此刻为什么这样，读得出来吗？成立 / 勉强 / 不成立。
2. repeat：这一段有没有把前面已经说过、已经得出的东西当成新的再说一遍？有 / 没有；有就写出哪一条重说了哪一条。
3. label：段首标的关系和这一段实际写的内容对得上吗？对得上 / 对不上。
最后整体判断：只读这条线，是不是一件自己长出来、往前走的事；最主要的问题是什么。
戏剧化、主观、只讲一个故事都不算缺点。

【线】
{LINE}

只输出 json：
```json
{{"sections": [{{"sec": "S01", "self": "成立", "self_why": "……", "repeat": "没有", "repeat_what": "", "label": "对得上", "label_why": "……"}}],
 "whole": "……", "main_problem": "……"}}
```"""
TRANS2 = """下面是一条“线”（一个人在肖邦{NAME}里经历的一件事，按段写成要点），以及另一批人听这首曲子每一段写下的听感记录（珠子）。
线和珠子会排在一起给读者看：珠子写此刻听到、感到的样子；线讲他自己的经历，只要在同一段里有情境相近的处境或原因就行，不该把珠子再说一遍。

请逐条判断线的每一条：
- 自己的原因：说的是他自己的经历、想法或处境，拿掉珠子也有意义；
- 复述珠子：把珠子里的感受、画面、比喻换个说法放进了线，或者把珠子里想象出的人物动作、情节写成了他真的经历的事；
- 两者都有：既有自己的经历，也夹带了复述。
复述的写出是对应哪颗珠子的哪句话。

【线】（方括号里是条目编号）
{LINE}

【珠子】
{BEADS}

只输出 json：
```json
{{"items": [{{"id": "S01-1", "label": "自己的原因", "bead": "", "why": "……"}}]}}
```"""
'''
t = t.replace(anchor, ADD + anchor, 1)
old_run = '''            ma = ALONE.format(NAME=covjudge.NAME[w], LINE=line_ids(g))
            mt = TRANS.format(NAME=covjudge.NAME[w], LINE=line_ids(g), BEADS=V.beads(w))
            for j, m in V.JUDGES.items():
                for rid, msg in ((f"al_{w}_{j}_{tag}", ma), (f"tr_{w}_{j}_{tag}", mt)):'''
assert old_run in t
t = t.replace(old_run, '''            ma = (ALONE2 if JV == "2" else ALONE).format(NAME=covjudge.NAME[w], LINE=line_ids(g))
            mt = (TRANS2 if JV == "2" else TRANS).format(NAME=covjudge.NAME[w], LINE=line_ids(g), BEADS=V.beads(w))
            for j, m in V.JUDGES.items():
                for rid, msg in ((f"{A}_{w}_{j}_{tag}", ma), (f"{T}_{w}_{j}_{tag}", mt)):''')
t = t.replace('''def run(tags):
    jobs = []''', '''A, T = ("al2", "tr2") if JV == "2" else ("al", "tr")


def run(tags):
    jobs = []''', 1)
old_sum = '''            a = V.parse(f"al_{w}_{j}_{tag}") or {}; t = V.parse(f"tr_{w}_{j}_{tag}") or {}'''
assert old_sum in t
t = t.replace(old_sum, '''            a = V.parse(f"{A}_{w}_{j}_{tag}") or {}; t = V.parse(f"{T}_{w}_{j}_{tag}") or {}
            rep = sum(s.get("repeat") == "有" for s in a.get("sections") or []); badlab = sum(s.get("label") == "对不上" for s in a.get("sections") or [])''')
t = t.replace('''            out[key] = {"items": n_items,''', '''            out[key] = {"repeat": rep, "label_mismatch": badlab, "items": n_items,''')
old_print = '''            print(tag, key, f"段成立 {selfc.get('成立', 0)}/{len(g['segments'])} 勉强 {selfc.get('勉强', 0)} 不成立 {selfc.get('不成立', 0)} | "'''
assert old_print in t
t = t.replace(old_print, '''            print(tag, key, f"段成立 {selfc.get('成立', 0)}/{len(g['segments'])} 勉强 {selfc.get('勉强', 0)} 不成立 {selfc.get('不成立', 0)} | "
                  + (f"重说 {rep} 段 | 标签对不上 {badlab} 段 | " if JV == "2" else "") + ''')
t = t.replace('''    (V.OUT / f"alone_{tag}.md").write_text''', '''    (V.OUT / f"alone{'2' if JV == '2' else ''}_{tag}.md").write_text''')
t = t.replace('''open(V.OUT / f"alone_{tag}.json", "w"''', '''open(V.OUT / f"alone{'2' if JV == '2' else ''}_{tag}.json", "w"''')
p.write_text(t, encoding="utf-8")

p = H / "e2e_open.py"; t = p.read_text(encoding="utf-8")
old1 = "1. 线单独读也成立：只读线、不看珠子，每一段他为什么此刻这样，都能由前面已经发生在他身上的事说明，读得出一条往前走的路。"
assert old1 in t
t = t.replace(old1, "1. 线单独读也成立：只读线、不看珠子，它自己就是一件有逻辑、有时序、内在有发展的事；看得出他此刻为什么这样，但不靠“因为……所以……”生硬地交代；推动它的是他自己前面的经历，不是音乐事件或新编的事；像一步步往前探索，不像在迷宫里来回。")
old2 = "2. 不啰嗦：每一句都有它自己的用处。删掉也不丢东西的话、把前面已经说过的再说一遍的话，都是啰嗦。这一段真正发生得少，就该写得短。"
assert old2 in t
t = t.replace(old2, "2. 不啰嗦、连着读顺：连着读下来每一句都能自然接上前一句；每一句都有它自己的用处。删掉也不丢东西的话、把前面已经说过的再说一遍的话，都是啰嗦。这一段真正发生得少，就该写得短。")
t = t.replace("“线”：一个人在这首曲子里经历的一件事，按音乐的段落写成条目。", "“线”：一个人在这首曲子里经历的一件事，按音乐的段落写成几条要点。")
t = t.replace('    return f"eo_{w}_{TAG}_{j}_r{k}"', '    return f"eo2_{w}_{TAG}_{j}_r{k}"   # 11-02: eo2 = goals aligned to 标准.md')
t = t.replace('    fn = V.OUT / f"e2e_open_{TAG}.md"', '    fn = V.OUT / f"e2e_open2_{TAG}.md"')
assert 'eo2_' in t
p.write_text(t, encoding="utf-8")
print("ok")
