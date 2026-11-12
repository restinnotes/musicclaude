"""11-08 精确去小节号：K3N（模型去小节号）连带删了别的内容，op60 整屏珠子覆盖从 0.68 掉到 0.656；纯正则删又留下“附近，”“约”“直交界”这类断口。
这里先正则删，再只让模型修断口：除小节号和位置说明外，删掉的字不超过 4 个，否则用正则结果。
python nobar2.py SRC NEW
"""
import copy, difflib, re, sys
from concurrent.futures import ThreadPoolExecutor
import prompt_lint, gate2
from pub24 import S, rd, wr, call, parse, G6, WORKS, to_script

N = r'\d+\s*(?:[–—\-~～至到]\s*\d+\s*)?'
PAT = [re.compile(r'第?' + N + r'小节(?:起|里|处|开始|时|前后|以后|之后|附近|交界)?[，,：:、]?\s*'), re.compile(r'小节\s*' + N + r'[，,：:、]?\s*')]
BAR = re.compile(r'\d+\s*小节|第\s*\d+|小节\s*\d+|\d{2,3}')
FIX = """下面是钢琴曲视频屏幕上的几块感受小字。每块给了原文和“删掉小节号后”的样子：小节号观众不需要看到，已经删掉，但有的地方删出了断口（句子开头不完整、只剩“附近”“约”“的”、“直到……才”缺了中间、还剩孤立的数字）。
请只修断口，让每块读得通：
1. 只在断口处改动，其余字一个不动；不加原文没有的意思，不删原文的画面、比喻、身体感觉、心里话。
2. 原来靠小节号表示的先后、时间点，用“先”“后来”“接着”“最后”“到这里”这类词接上；不写任何数字。
3. 已经通顺的块原样照抄。

只输出 JSON：{"items":[{"id":"编号","text":"修好的整块"}]}

{ITEMS}
"""
prompt_lint.lint(FIX, 'nobar2.py')


def cut(t):
    for p in PAT: t = p.sub('', t)
    return re.sub(r'^[，,；;：:、\s]+', '', t)


def lost_chars(old, new):
    o = cut(old); sm = difflib.SequenceMatcher(None, o, new)
    return sum(i2 - i1 for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag in ('delete', 'replace'))


def one(a):
    w, src, new = a; p = S/f'screen_{w}_{new}.json'
    if p.exists(): to_script(w, new, rd(p)); return True
    scr = copy.deepcopy(rd(S/f'screen_{w}_{src}.json')); todo = {}
    for s in scr['sections']:
        for k, x in enumerate(s['rows'], 1):
            for n, i in enumerate(x['items'] if x['kind'] == 'feel' else [x], 1):
                if BAR.search(i['text']) and '小节' in i['text'] or re.search(r'第\s*\d+', i['text']):
                    todo[f"{s['sec']}-r{k}-i{n}"] = i
    if not todo:   # 11-09：这一首没有小节号（另一首有），原样保留，不发空清单（K10b 幻想发了空清单，模型三次都回来要原文）
        wr(p, scr); to_script(w, new, scr); print(w, new, '没有小节号，原样保留', flush=True); return True
    txt ='\n'.join(f"[{bid}] 原文：{i['text']}\n    删掉小节号后：{cut(i['text'])}" for bid, i in todo.items())
    for t in range(3):
        ans = call(f'pub24NB2_{w}_{new}' + ('' if not t else f'_r{t}'), FIX.replace('{ITEMS}', txt), G6, 'gpt3s', 'public24-nobar2')
        try:
            r = {x['id']: (x.get('text') or '').strip() for x in parse(ans)['items']}; fb = 0
            for bid, i in todo.items():
                nt = r.get(bid) or ''
                if not nt or lost_chars(i['text'], nt) > 4 or re.search(r'\d', nt): nt = cut(i['text']); fb += 1
                i['text'] = nt
            wr(p, scr); to_script(w, new, scr)
            print(w, new, '改', len(todo), '块；退回正则', fb, '；仍有小节号', gate2.barnums(w, new), flush=True)
            for bid, i in todo.items(): print('   ', bid, i['text'][:70], flush=True)
            return True
        except Exception as ex: print('不合格', w, new, repr(ex)[:200], flush=True)
    return False


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, sys.argv[1], sys.argv[2]) for w in WORKS])), flush=True)
