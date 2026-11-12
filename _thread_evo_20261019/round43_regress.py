"""R43 只补评委明确说“退步”的那几处，最多改 6 条。usage: python round43_regress.py TAG SOURCE BASE"""
import json, os, sys
from concurrent.futures import ThreadPoolExecutor
os.environ.setdefault('JV', '2')
import pipe, screen_flow as F, v6fix as V
import round34_restore as R34

PROMPT = """下面是一条“线”（一个人在这首曲子里经历的一件事，按音乐段落分段写成条目）和它要取代的旧版。评委们整体上选这条线，但有几位觉得取代旧版会丢掉一些实质内容。

你的任务：只把确实该留下的那一点带回来，其他一字不动。
- 最多改 6 条，优先把意思带进已有的条目；每条仍是一句。
- 用这条线现在的口气：平常人讲自己的事，具体；旧版的说法如果像在分析心理（比如“用表现换安心”这类），不要照搬，换成他会说的话。
- 不要把重复带回来；已经有别处交代的不用补。
- 不新增事件、前史、对白、物件、第三人和对方的新举动。
- 整篇字数基本不变。

【这条线】（方括号里是条目编号）
{LINE}

【旧版】
{OLD}

【评委说退步的理由】
{WHY}

只输出 JSON：{{"edits":[{{"id":"S03-2","op":"replace","text":"改后的一句"}}],"note":"一句话"}}"""


def why(w, tag, base):
    out = []
    for j in F.JUDGES:
        for seat in ('newX', 'newY'):
            d = V.parse(f'v6b3_{w}_{j}_{tag}_vs{base}_{seat}')
            new, old = ('X', 'Y') if seat == 'newX' else ('Y', 'X')
            if d and d.get(f'{new}_replacing_{old}_regress') == '是':
                out.append((d.get(f'{new}_regress_why') or '').replace(new, '这条线').replace(old, '旧版'))
    return '\n'.join(f'- {x}' for x in out) or '（这一首没有评委判退步）'


def one(tag, source, base, w):
    reasons = why(w, source, base)
    msg = PROMPT.format(LINE=V.view(V.graph_of(w, source), ids=True), OLD=V.view(V.graph_of(w, base)), WHY=reasons)
    answer = pipe.call(f'sc{tag}_{w}_A10', msg, 'g6', tag)
    if len(answer.get('edits', [])) > 6:
        raise ValueError(f'{w}: 改了 {len(answer["edits"])} 条')
    R34.apply(w, tag, source, answer)


if __name__ == '__main__':
    F.configure()
    tag, source, base = sys.argv[1:4]
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda w: one(tag, source, base, w), F.WORKS))
