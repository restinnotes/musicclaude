"""11-09 感受锚点：K11g 绝对验收里反复出现的中等问题之一是“小字感受是一长串多层意思的句子，扫不动”，评委原话里有“没有加亮的阅读锚点”。
标准第 7 条：关键词放大，带着人先看该先看的。现在只有大字（话）有放大词，小字感受一个都没有。
这里不删字、不改字：给较长的感受块各挑一个关键词（照抄块里连续的字）加亮，当扫读锚点。
python anchor.py SRC NEW [最短块长，默认 22]
"""
import copy, os, sys
from concurrent.futures import ThreadPoolExecutor
import prompt_lint
from pub24 import S, rd, wr, call, parse, G6, WORKS, to_script

ANC = """下面是一首钢琴曲大众版“边听边看”视频屏幕上的一些小字感受（每条有编号）。观众边听边扫，长的小字一眼读不完；我们想在每条里加亮一个词，让人扫一眼先抓到它。
请给每条挑一个词：
1. 照抄这条里连续的字，2 到 6 个字。
2. 挑最能让人一下感到这一刻的那个：具体的画面、身体感觉、或心里冒出的那句话里最关键的几个字；不要挑“声音”“音乐”“感觉”“仿佛”这类空词，也不要挑纯讲音乐技法的词。
3. 只挑一个。

只输出 JSON：{"items":[{"id":"编号","key":"照抄的词"}]}

{ITEMS}
"""
prompt_lint.lint(ANC, 'anchor.py')
MINLEN = int(sys.argv[3]) if len(sys.argv) > 3 else 22


def one(a):
    w, src, new = a; p = S/f'screen_{w}_{new}.json'
    if p.exists(): to_script(w, new, rd(p)); return True
    scr = copy.deepcopy(rd(S/f'screen_{w}_{src}.json')); todo = {}
    for s in scr['sections']:
        for x in s['rows']:
            if x['kind'] != 'feel': continue
            for it in x['items']:
                if len(it['text']) >= MINLEN: todo[str(len(todo)+1)] = it
    NL = chr(10); txt = NL.join(f"[{k}] {it['text']}" for k, it in todo.items())
    r = {}
    for t in range(3):
        try: r = {str(x['id']): (x.get('key') or '').strip() for x in parse(call(f'pub24ANC_{w}_{new}' + ('' if not t else f'_r{t}'), ANC.replace('{ITEMS}', txt), G6, 'gpt3s', 'public24-anchor'))['items']}; break
        except Exception as ex: print('不合格', w, new, repr(ex)[:150], flush=True)
    n = 0
    for k, it in todo.items():
        key = r.get(k, '')
        if 2 <= len(key) <= 8 and key in it['text']: it['keys'] = [key]; n += 1
    wr(p, scr); to_script(w, new, scr)
    print(w, new, '长感受块', len(todo), '；加了锚点', n, flush=True); return True


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, sys.argv[1], sys.argv[2]) for w in WORKS])), flush=True)
