"""顾问：看标准、用户原话、材料和评审问题，给诊断和候选。python advise.py ROUND MAINLINE [上一轮结果文件…]"""
import json, re, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import pub2
from pub2 import OUT, ROOT, G6, G56, rd, wr

P = """你是一位帮我们改进“视频文字流水线”的顾问。请认真思考，不用顾及我们之前的做法，可以大刀阔斧。回答时不要进行联网搜索。

【我们在做什么】
给一首器乐作品（钢琴曲）做“边听边看”的视频。上游已经有两样定稿的东西：
- 线：一个人在这首曲子里经历的一件事，按音乐段落分段，每段几条 bullet。每条性质不同，很多是一起描述这一段的，不是时间先后。
- 珠子：听这一段的人写下的当下体验。

定稿文字太长，只适合能暂停细读的小众版。我们要做一个给大众看的主版本，先到七八十分。流水线的输入是定稿的线和珠子，输出是每段一屏的文字（线、珠子、高亮的关键词）和全曲的阶段短语。下方是音乐动画，文字和音乐同时在屏幕上。

【大众版标准（用户定的，以此为准）】
{STD}

【用户对上一个做法的评判，以及之前说过的话（原话，最高优先级）】
{USER}

【任何方案都必须满足】
1. 泛化：换任何作品都能照样跑。提示词里不放具体作品的内容或例子，也不写只针对眼前某处毛病的规定。
2. 成品全部由流水线产出，不经人手修改。
3. 不改变听感内容：可以重新组织、压缩、换说法，不能加原文没有的事件、画面和情节；不把珠子里的比喻变成线里真的发生的事。
4. 两首作品同一套提示词。
5. 不靠写死的字数、句数、秒数来控制；用目的来引导模型。屏幕放得下多少由版面解决，字太多会被评委判输。

【已经试过的】
{TRIED}

【画面能做什么】
每段一屏，同一屏的内容同时显示。可以高亮词语。标了“局部”的句子能在那几小节才出现，并和音乐一起变色。分组、上下左右的摆放、谁大谁小、谁先淡入，都可以由程序按你提的规则做。你的提示词只负责文字和关键词；如果你需要某种呈现，在“阅读顺序”和“呈现要点”里写。

【输出格式是固定的（程序会自动加在提示词后面，你不用写）】
{FORMAT}

【当前主线的文字（给评委看的形式，【】是高亮词）】
{MAIN}

【开放评审对它挑出的问题】
{ISSUES}

【上一轮的候选结果】
{LAST}

【原文：{W0}】
{SRC0}

【原文：{W1}】
{SRC1}

【请你回答】
1. 诊断：现在的文字为什么像截断、为什么音乐描述多、为什么反而妨碍理解？问题出在哪里？
2. 你认为大众版一屏应该长什么样？观众的眼睛怎么走，先抓到什么，再抓到什么？
3. 给 {N} 套彼此假设不同的候选，每套写完整提示词。可以是一步，也可以是两步（比如先想清楚这一段的核心，再写）。第一步的提示词里用 {{SOURCE}} 代表原文；第二步用 {{PREV}} 代表上一步的输出，也可以用 {{SOURCE}}。不要在提示词里写输出格式。

每套严格按下面的样子写，程序会解析：

=== 候选：英文短名 ===
假设：一句话，这套想验证什么。
阅读顺序：珠子在前 或 线在前
呈现要点：一两句话，这一屏怎么摆。
第一步：
```text
提示词全文
```
第二步（可选）：
```text
提示词全文
```
"""

TRIED = """- 首版（用户已否定）：写死字数和句数上限，每拍先几句珠子再落一句线，按时间依次出现。结果像把原文截断，把一起描述一段的 bullet 排成先后，音乐描述过多。比较起点 base0 就是这个做法在当前版本上的产物。
- 只摘原文 10% 的句子放在底部字幕，加一堆视觉元素（用户否定：“你这种去掉字数意义是什么”“这些视觉我完全看不出意义”）。
- 全文铺满屏幕加节点和连线（用户否定：读不完；“不应该要节点和连线”）。
- 上游写线的经验：整篇一次写胜过逐段写；事后改写改不动结构；固定禁词表无效；局部修订再把评委说丢的补回来，比整篇重写赢得多。"""

ADV = [('g6a', G6, 4), ('g6b', G6, 3), ('g56', G56, 3)]


def issues(tag):
    rows = []
    for w in pub2.WORKS:
        for j in ['g6', 'g56']:
            p = OUT/f'open_{w}_{tag}_{j}.json'
            if not p.exists(): continue
            d = rd(p); rows.append(f"——{pub2.NAME[w]}，评委 {j} 整体印象：{d.get('overall', '')}")
            rows += [f"[{i.get('severity')}] {i.get('where')}：{i.get('quote', '')[:60]}｜{i.get('why', '')[:160]}" for i in d['issues'] if i.get('severity') in ('严重', '中等')]
    return '\n'.join(rows)


def run(rnd, main, last_files):
    last = '\n\n'.join(Path(f).read_text(encoding='utf-8') for f in last_files) or '（第一轮，没有）'
    W0, W1 = pub2.WORKS
    msg0 = P.replace('{STD}', pub2.std()).replace('{USER}', (ROOT/'用户判定.md').read_text(encoding='utf-8')).replace('{TRIED}', TRIED).replace('{FORMAT}', pub2.FORMAT.strip())
    msg0 = msg0.replace('{MAIN}', pub2.screen(W0, main)+'\n\n'+pub2.screen(W1, main)).replace('{ISSUES}', issues(main)).replace('{LAST}', last)
    msg0 = msg0.replace('{W0}', pub2.NAME[W0]).replace('{W1}', pub2.NAME[W1]).replace('{SRC0}', pub2.source(W0)).replace('{SRC1}', pub2.source(W1))

    def one(a):
        j, m, n = a; msg = msg0.replace('{N}', str(n)).replace('{{SOURCE}}', '{SOURCE}').replace('{{PREV}}', '{PREV}')
        ans = pub2.call(f'pub2_adv_{rnd}_{j}', msg, m, 'gpt3s', 'public2-advise')
        (OUT/f'adv_{rnd}_{j}.md').write_text(ans or '', encoding='utf-8')
        return j, len(ans or '')
    print(len(msg0), flush=True)
    with ThreadPoolExecutor(3) as ex: print(list(ex.map(one, ADV)), flush=True)
    collect(rnd)


def collect(rnd):
    (OUT/'candidates').mkdir(exist_ok=True); names = []
    for j, _, _ in ADV:
        t = (OUT/f'adv_{rnd}_{j}.md').read_text(encoding='utf-8')
        for block in re.split(r'(?:={3,}\s*候选[:：]\s*|#+\s*候选[一二三四五六七八九十\d]*[:：]\s*)', t)[1:]:
            name = re.match(r'[^\s=]+', block).group(0)
            steps = re.findall(r'```(?:text)?\n(.*?)\n```', block, re.S)
            if not steps or '{SOURCE}' not in steps[0]:
                print('跳过（没有 {SOURCE}）', j, name); continue
            hyp = re.search(r'假设[:：]\s*(.*)', block); order = re.search(r'阅读顺序[:：]\s*(.*)', block); show = re.search(r'呈现要点[:：]\s*(.*)', block)
            tag = f"{rnd}{j}_{re.sub(r'[^A-Za-z0-9]', '', name)[:14]}"
            wr(OUT/f'candidates/{tag}.json', {'advisor': j, 'hypothesis': hyp.group(1).strip() if hyp else '', 'order': '线在前' if order and '线在前' in order.group(1) else '珠子在前', 'show': show.group(1).strip() if show else '', 'steps': steps})
            names.append(tag); print(tag, '｜', hyp.group(1)[:90] if hyp else '', '｜', order.group(1)[:8] if order else '', '｜步骤', len(steps), flush=True)
    return names


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    if sys.argv[1] == 'collect': collect(sys.argv[2])
    else: run(sys.argv[1], sys.argv[2], sys.argv[3:])
