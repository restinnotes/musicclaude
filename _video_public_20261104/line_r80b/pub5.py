"""第二步：把已经挑好的短文字（d2）彻底拆成词，线压到一扫就懂。全走 gpt3。
python pub5.py 来源TAG 新TAG
"""
import json, sys
from concurrent.futures import ThreadPoolExecutor
import pub2, pub3
from pub2 import G6, WORKS, call, parse, rd, tidy_keys, wr

P = """下面是一首器乐曲视频的文字，已经挑过一遍。观众边听边扫屏幕，只有一眼的工夫。请把它改成两种完全不同的东西。分组、rank、emotion、阶段、from 都不要动。

【beads：只留词】
每条珠子拆成词，放进 beads，每个词一条（emotion 和 from 沿用原来那条珠子）。
是词，不是短语，更不是半句。看到逗号、长长的“的”字定语、动作过程，就是还没拆完。
比如“心里空荡荡的，像走进一间搬空的屋子，说话都有回声”，只要“空荡荡”“回声”。
一条珠子通常拆出一两个词，最多留住它最有感觉的那几个。词单独扫到要有感觉，不要离开句子就不懂的半截话，也不要音乐术语。可以换成原文意思里更好扫的说法。
偶尔可以留一声很短的问，比如“是真的吗？”。除问号外不带标点。
整段的词加起来也要一眼扫得完。同一个感受不说两遍。

【lines：一句扫完的话】
每条线改到一扫就读完。只留一件事：这个人此刻怎么了。原因、过程、补充、第二层转折，能删就删。
不要“我想了很久，觉得就算事情没有按我希望的那样发展，我也还是愿意继续等下去”，要“没按我想的来，我还是想等”。
讲这件事的人一律写“我”。事情里如果有别的人或别的对象，全程用同一个称呼，不要换来换去；没有就不要加。
说得直接，像这个人自己在说，有正常的标点。意思不能走样，语气不能加重或减轻。
只读每段主组的线，从头到尾连起来，要接得上，是一件有发展的事；需要时留一点和上一句的关系（比如“还是”“这回”“可是”），要自然。

只输出 JSON，结构和输入完全一样，keys 一律留空数组。

输入：
"""


def one(a):
    w, src, tag = a; p = pub3.OUT/f'script_{w}_{tag}.json'
    if p.exists(): return True
    d0 = rd(pub3.OUT/f'script_{w}_{src}.json')
    for s in d0['sections']:
        for g in s['groups']:
            g.pop('kind', None)
            for x in g.get('lines', [])+g.get('beads', []): x.pop('keys', None)
    msg = P+json.dumps(d0, ensure_ascii=False)
    for k in range(3):
        ans = call(f'pub5_{w}_{tag}'+('' if not k else f'_r{k}'), msg, G6, 'gpt3s', 'public5-words')
        try:
            d = tidy_keys(parse(ans)); errs = pub3.check(w, d)
        except Exception as e:
            print(w, '解析失败', repr(e)[:200], flush=True); continue
        print(w, tag, '问题', len(errs), errs[:4], flush=True)
        wr(p.with_suffix('.try.json'), d)
        if not errs: wr(p, d); return True
    return False


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    src, tag = sys.argv[1:3]
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, src, tag) for w in WORKS])), flush=True)
    pub3.marks(tag)
