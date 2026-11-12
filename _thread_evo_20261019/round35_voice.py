"""R35 换口气：结构好但书面的稿，逐条改成平常话；人物走到哪里不变。
usage: python round35_voice.py TAG SOURCE VOICE  （VOICE 是同一首口气好的另一稿，只作口气参照）"""
import json, os, sys
from concurrent.futures import ThreadPoolExecutor
os.environ.setdefault('JV', '2')
import pipe, screen_flow as F, v6fix as V
import round34_restore as R34

PROMPT = """下面是一条“线”：一个人在这首曲子里经历的一件事，按音乐段落分段写成条目。它的发展写得好，人物一步步走到了新的地方；毛病是口气偏书面，像在分析心理。

你的任务：逐条改成一个平常人讲自己的事会说的话。人物在每一步想到什么、走到哪里，都不变。

- 写他此刻具体在乎什么、怕什么、盼什么；念头可以直接说出来，可以是一句问话。
- 少用“需要、依恋、亲近、归属、相互、承担、接纳、笃定、衡量”这类概括心理的词，能换就换成他会说的话；同一个词不要整篇反复用。
- 不替他总结，不站在外面讲解他意识到了什么；不用工整对称句，不用“越……越……”，不用多余的否定和多余的“也”。
- 能短就短，一句话说完的不绕；不必要的限定去掉。
- 意思不能丢：每条的实质内容要留下；只是重说前面意思的条目可以删。
- 不新增事件、前史、对白、物件、第三人和对方的新举动。
- 每段 2–4 条，每条一句。

下面的【口气参照】是同一件事的另一稿，只看它怎么说话，不要搬它的内容和发展。

【要改的线】（方括号里是条目编号）
{SOURCE}

【口气参照】
{VOICE}

只输出 JSON：
{{"edits":[{{"id":"S01-1","op":"replace","text":"改后的一句"}},{{"id":"S09-2","op":"delete"}}],"note":"一句话"}}"""


def one(tag, source, voice, w):
    msg = PROMPT.format(SOURCE=V.view(V.graph_of(w, source), ids=True), VOICE=V.view(V.graph_of(w, voice)))
    R34.apply(w, tag, source, pipe.call(f'sc{tag}_{w}_A8', msg, 'g6', tag))


if __name__ == '__main__':
    F.configure()
    tag, source, voice = sys.argv[1:4]
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda w: one(tag, source, voice, w), F.WORKS))
