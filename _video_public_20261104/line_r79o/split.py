"""11-08 打碎层：把屏幕稿的感受块打碎成短语，每个短语挂一个珠子要点（pt），按要点自己的时间窗到时出现；正文去掉小节号。
来由：用户 11-08：“为什么会还有小节 我们不是应该更精细的会给他做动画吗 然后也没有试要不要打碎？”
K3A 的感受块平均 36–44 字，几个局部要点并成一句，只好在正文里写“44–65小节……52–63小节……”区分，渲染也只能整块按一颗珠子的第一个时间出现。
python split.py SRC NEW split|nobar      split = 打碎 + 去小节号；nobar = 只去小节号、不拆（对照，只差打碎这一处）
"""
import copy, json, re, sys
from concurrent.futures import ThreadPoolExecutor
import prompt_lint
from pub24 import S, R2, rd, wr, call, parse, G6, WORKS, to_script

COMMON = """下面是钢琴曲大众版“边听边看”视频屏幕稿里的“感受”小字。观众边听边扫，每段只停留写明的秒数。每块感受后面附了它来自的珠子要点（带编号；标“局部”的要点只在音乐的某一小段出现，屏幕会在那一刻才让它出现）。
"""
SPLIT = COMMON + """现在每块感受多是一整句长话，有的还写了小节号。请把每块打碎成散落的短语，让每个短语能在音乐走到它对应的那一刻单独出现。

怎么打碎：
1. 一块拆成几个短语，每个短语只装一个东西：一个画面、一种身体感觉、一个比喻或一句心里话。口语，像人随口说出来的，不是书面词；也不是把一句话硬切成两半，拆完每个短语都要自己读得懂。不加句末标点。
2. 每个短语写明它来自哪个要点（pt，只能用这块附的编号）。不同局部要点的内容要拆开，不合在一个短语里。
3. 正文里不写小节号，也不写“第几小节”“从某小节起”这类位置说明：什么时候出现由 pt 决定，观众不需要看到。原句里靠小节号区分的前后变化，用“先……”“后来……”或直接拆成两个短语表达。
4. 只拆不改：意思、语气、比喻、具体说法都照原块；不加原块没有的内容，不删原块里的具体东西；只可以去掉拆开后多余的连接词和重复的主语。原块是疑问仍是疑问，是猜测仍是猜测。
5. 原块本来就是一个短语的，原样保留，只补 pt。

只输出 JSON：{"blocks":[{"id":"块编号","items":[{"text":"短语","pt":"要点编号"}]}]}，每块都要有，按原顺序。

{BLOCKS}
"""
NOBAR = COMMON + """有的感受块里写了小节号。请只做一件事：去掉正文里的小节号和“第几小节”“从某小节起”这类位置说明，观众不需要看到它们。

怎么改：
1. 每块仍是一块，不拆、不合。
2. 没有小节号的块原样照抄。
3. 有小节号的块只删位置说明，其余字尽量不动；原句靠小节号区分的前后变化，改用“先……”“后来……”这类说法接上，意思、语气、比喻、具体说法都照原块，不加不删。
4. pt 写这块主要来自的要点编号（只能用这块附的编号）。

只输出 JSON：{"blocks":[{"id":"块编号","items":[{"text":"改后的整块","pt":"要点编号"}]}]}，每块都要有，按原顺序。

{BLOCKS}
"""
SPLIT2 = SPLIT.replace("""1. 一块拆成几个短语，每个短语只装一个东西：一个画面、一种身体感觉、一个比喻或一句心里话。口语，像人随口说出来的，不是书面词；也不是把一句话硬切成两半，拆完每个短语都要自己读得懂。不加句末标点。""", """1. 按意思单位拆，不按逗号拆：一个短语装一个完整的画面、一种身体感觉、一个比喻或一句心里话。一个画面连带的几层（动作和它的结果、比喻和它比的东西、转折的前后两半）留在同一个短语里；并列的几样东西留在一个短语里，不要拆成句式重复的几条。拆完每个短语都要能单独读懂，不能是接不上前文的半句。口语，不是书面词，不加句末标点。""")   # 11-08 中等碎：K3S 按逗号拆出了半句和重复句式
prompt_lint.lint(SPLIT, 'split.py'); prompt_lint.lint(SPLIT2, 'split.py'); prompt_lint.lint(NOBAR, 'split.py')
BARRE = re.compile(r'\d+\s*[–—\-~～至到]\s*\d+\s*小节|第\s*\d+|\d+\s*小节|小节\s*\d+')


def one(a):
    w, src, new, mode = a; p = S/f'screen_{w}_{new}.json'
    if p.exists(): to_script(w, new, rd(p)); return True
    scr = copy.deepcopy(rd(S/f'screen_{w}_{src}.json'))
    beads = {b['id']: b for s in rd(R2/f'{w}_src.json')['sections'] for b in s['beads']}
    import pub16
    win = pub16.windows(w); txt = []; blocks = {}
    for s in scr['sections']:
        txt.append(f"\n### {s['sec']}（停留 {round(win[s['sec']][1]-win[s['sec']][0])} 秒）")
        for k, x in enumerate(s['rows'], 1):
            if x['kind'] != 'feel': continue
            for n, i in enumerate(x['items'], 1):
                bid = f"{s['sec']}-r{k}-i{n}"; fr = [i.get('bead')] + [f for f in (i.get('from') or []) if f != i.get('bead')]
                pts = [q for f in fr if f in beads for q in beads[f]['points']]
                blocks[bid] = (i, {q['id'] for q in pts}, pts)
                txt.append(f"[{bid}] {i['text']}")
                txt.extend(f"    要点 {q['id']}{'（局部）' if q['local'] else ''}：{q['text']}" for q in pts)
    msg = {'split': SPLIT, 'split2': SPLIT2, 'nobar': NOBAR}[mode].replace('{BLOCKS}', '\n'.join(txt))
    for t in range(3):
        ans = call(f'pub24SP_{mode}_{w}_{new}' + ('' if not t else f'_r{t}'), msg, G6, 'gpt3s', 'public24-split')
        try:
            r = {b['id']: b.get('items') or [] for b in parse(ans)['blocks']}
            miss = [b for b in blocks if not r.get(b)]
            assert len(miss) <= max(1, len(blocks)//20), f'缺块 {miss[:5]}'
            for s in scr['sections']:
                for k, x in enumerate(s['rows'], 1):
                    if x['kind'] != 'feel': continue
                    out = []
                    for n, i in enumerate(x['items'], 1):
                        bid = f"{s['sec']}-r{k}-i{n}"; old, ok, pts = blocks[bid]; got = r.get(bid)
                        if not got: out.append(old); continue
                        for g in got:
                            tx = (g.get('text') or '').strip().rstrip('，。、；'); pt = g.get('pt') if g.get('pt') in ok else None
                            if not tx: continue
                            bead = pt.rsplit('-p', 1)[0] if pt else old.get('bead')
                            it = {'text': tx, 'bead': bead, 'from': [bead], 'bars': None if mode.startswith('split') else old.get('bars')}
                            if mode.startswith('split') and pt: it['pt'] = pt
                            out.append(it)
                    x['items'] = out
            left = [i['text'] for s in scr['sections'] for x in s['rows'] for i in (x.get('items') or [{'text': x.get('text', '')}]) if BARRE.search(i['text'])]
            wr(p, scr); to_script(w, new, scr)
            F = [i for s in scr['sections'] for x in s['rows'] if x['kind'] == 'feel' for i in x['items']]
            print(w, new, mode, '感受块', len(F), '平均字', round(sum(len(i['text']) for i in F)/max(1, len(F)), 1),
                  '挂要点', sum(bool(i.get('pt')) for i in F), '仍有小节号', len(left), left[:3], flush=True)
            return True
        except Exception as ex: print('不合格', w, new, repr(ex)[:200], flush=True)
    return False


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    src, new, mode = sys.argv[1], sys.argv[2], sys.argv[3]
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, src, new, mode) for w in WORKS])), flush=True)
